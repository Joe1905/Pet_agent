import os
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog

from file_load import ResourceExtractor
from link_model import ChatAgent
from string_manager import StringManager
from ui.chat_ui import Ui_Form  # 生成的类
from ui.loadingUi import TransparentOverlay
from ui.messageInfo import MessageListModel, MessageItemDelegate
from ui.messageUi import MessageWidget, MessageWidget2
# from ai_agent import AIAgent

# 判断是否为打包后的环境
if getattr(sys, 'frozen', False):
    # 打包后，ui文件在 sys._MEIPASS 目录下的 ui 文件夹中
    base_path = sys._MEIPASS
    ui_path = os.path.join(base_path, "ui", "mainUi.ui")
else:
    # 开发环境，使用当前脚本的目录
    base_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(base_path, "mainUi.ui")

# uic.loadUi(ui_path, self)

class MainWindow(QWidget, Ui_Form):
    str_content:str = None
    windowClosed:Signal = Signal()

    def __init__(self, on_close_window):
        super().__init__()
        self.string_manager = StringManager()
        
        # 修正 chat.ico 的路径
        # 如果是开发环境，base_path 是 src/ui，chat.ico 在 src 下
        # 如果是打包环境，base_path 是 sys._MEIPASS，chat.ico 应该在根目录或 src 下
        
        if getattr(sys, 'frozen', False):
             # 打包环境，chat.ico 通常在根目录
             icon_path = os.path.join(base_path, "chat.ico")
        else:
             # 开发环境，base_path 是 src/ui，chat.ico 在 src
             # 获取 src 目录
             src_path = os.path.dirname(base_path)
             icon_path = os.path.join(src_path, "chat.ico")
             
        self.setWindowIcon(QIcon(icon_path))

        self.setupUi(self)
        # 槽函数会自动连接，无需额外代码
        # 加载图片（使用资源文件路径或本地路径）
        self.normal_pix = QPixmap(":/btn/btn_send.png")  # 资源文件路径
        self.pressed_pix = QPixmap(":/btn/btn_send_hover.png")
        self.normal_pix2 = QPixmap(":/btn/btn_plus.png")  # 资源文件路径
        self.pressed_pix2 = QPixmap(":/btn/btn_plus_hover.png")
        self.textEdit.setAcceptRichText(False)

        self.overlay = TransparentOverlay()
        self.agent = ChatAgent.instance()
        self.thread = QThread()
        self.agent.moveToThread(self.thread)
        self.thread.start()

        self.msg_pack = None
        self.first_show = True
        self.timer = None

        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.model:MessageListModel = MessageListModel()
        self.delegate = MessageItemDelegate(self.listView)
        self.listView.setModel(self.model)
        self.listView.setItemDelegate(self.delegate)

        self.init_text_edit()

        layout = QVBoxLayout(self)

        layout.addWidget(self.listView)  # 中间控件

        # 底部输入栏
        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(self.textEdit)
        bottom_bar.addWidget(self.btn_send)
        bottom_bar.addWidget(self.btn_plus)

        layout.addLayout(bottom_bar)

        self.on_close_window = on_close_window

    def update_agent(self):
        if self.agent is None:
            return
        self.agent.update_system_prompt()
        return

    def init_text_edit(self):
        self.textEdit.setFontPointSize(MessageWidget.font_point_size)

    # 实现Qt Designer中定义的槽函数
    def on_button_clicked(self):
        self.add_item()

    def on_btn_pressed(self):
        # 按下时设置为按下状态图片
        self.btn_send.setIcon(QIcon(self.pressed_pix))

    def on_btn_released(self):
        # 释放时恢复普通状态图片
        self.btn_send.setIcon(QIcon(self.normal_pix))

    def on_button_clicked2(self):
        # 打开文件选择器
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                image_path = file_paths[0]
                # 发送图片消息
                # 使用特殊的标记或格式来表示这是一张图片，例如 "image:path/to/image.png"
                # 或者在 msg_pack 中增加一个字段来标识消息类型，但为了兼容现有结构，
                # 我们暂时使用前缀标识，并在 MessageWidget 中解析。
                # 更好的做法是修改 msg_pack 结构，但这里我们先用约定。
                # 假设约定：以 "image:" 开头的文本被视为图片路径。
                msg_content = f"image:{image_path}"
                self.add_item_image(msg_content)

    def add_item_image(self, image_path_str):
        # 新增图片消息子项
        msg_pack = MainWindow.finish_message_pack(image_path_str, 1)
        self.model.addItem(msg_pack)
        
        # 图片消息通常不需要发送给 LLM 进行文本回复，或者需要特殊的处理。
        # 这里我们假设图片发送后，只是显示在界面上，不触发 LLM 回复，
        # 或者触发一个默认的回复。
        # 如果需要 LLM 处理图片（多模态），则需要修改 agent 的接口。
        # 暂时只实现显示功能。
        self.on_new_item_add()
        
        # 触发发送逻辑，将图片路径传递给 agent
        QTimer.singleShot(0, lambda: self.send_message(image_path_str))

    def test_send_message(self):
        self.rebot_reply_message(self.textEdit.toPlainText())

    def on_btn_pressed2(self):
        # 按下时设置为按下状态图片
        self.btn_plus.setIcon(QIcon(self.pressed_pix2))

    def on_btn_released2(self):
        # 释放时恢复普通状态图片
        self.btn_plus.setIcon(QIcon(self.normal_pix2))

    def add_item(self, _type = 1):
        # 新增子项（数据会传递给模型）
        str_content = self.textEdit.toPlainText()
        if str_content != "":
            msg_pack = MainWindow.finish_message_pack(str_content, _type)

            self.model.addItem(msg_pack)
            self.textEdit.clear()
            self.textEdit.setEnabled(False)
            # 第一步：先处理UI刷新（确保item显示）
            # 使用单次定时器触发UI更新，完成后再触发send_message
            def after_ui_refresh():
                self.on_new_item_add()  # 执行UI相关操作
                # UI刷新后，再触发send_message
                QTimer.singleShot(0, lambda: self.send_message(str_content))

            # 先让UI有机会刷新（将after_ui_refresh放入事件队列）
            QTimer.singleShot(0, after_ui_refresh)
        # else:
        #     print(self.string_manager.get("mainUi.error_str1"))


    def append_text(self, token: str):
        if self.msg_pack is None:
            self.on_time_over(False)
            self.msg_pack = MainWindow.finish_message_pack(token, 2, True)
            self.model.addItem(self.msg_pack)
            self.on_new_item_add()
        else:
            self.msg_pack[0] += token
            response = self.msg_pack[0]
            if ChatAgent.get_response_have_tag(response, "final answer"):
                self.agent.on_response_back(response)

    def final_answer(self, reply:str):
        self.textEdit.setEnabled(True)
        self.textEdit.setFocus()
        if self.msg_pack is None:
            self.msg_pack = MainWindow.finish_message_pack(reply, 2, False)
        self.msg_pack[0] = reply
        row = self.model.rowCount() - 1
        if row >= 0 :
            last_index = self.model.index(row)
            self.msg_pack[3] = 1
            self.model.setData(last_index, self.msg_pack)
            self.on_new_item_add()
            self.msg_pack = None

    def rebot_reply_message(self, reply:str):
        self.textEdit.setEnabled(True)
        self.textEdit.setFocus()
        _type = 2
        str_content = reply
        if str_content != "":
            msg_pack = MainWindow.finish_message_pack(str_content, _type)
            self.model.addItem(msg_pack)
            QTimer.singleShot(0, lambda: self.on_new_item_add())

    def on_new_item_add(self):
        QTimer.singleShot(500, lambda: self.listView.update_scroll_range()
                  if hasattr(self, 'listView') else None)

    def send_message(self, str_content:str):
        now_time = datetime.now()
        self.textEdit.setEnabled(True)
        self.on_add_talk_times(now_time)
        self.agent.to_get_response(str_content, self.model.data_list)
        self.agent.trigger_task.emit()

    def on_add_talk_times(self, now_time):
        config = ResourceExtractor.get_setting_config()
        index = int(config["General_Set"]["current_index"])
        talk_times = int(config["Talk_Times"][f"talk_times_{index}"])
        talk_day = int(config["Talk_Times"][f"talk_day_{index}"])
        today = int(now_time.strftime("%Y%m%d"))
        cur_times = int(config["Talk_Times"][f"pet_{index}"])

        if talk_day == 0 or (talk_day == today and talk_times < 10) or talk_day != today:
            if talk_day != today:
                talk_times = 0
            talk_day = today
            talk_times += 1
            cur_times += 1

            ResourceExtractor.set_setting_config({
                "Talk_Times":
                    {
                        f"talk_times_{index}": talk_times,
                        f"talk_day_{index}": talk_day,
                        f"pet_{index}": cur_times
                    }
            }, None)

    def closeEvent(self, event):
        # print(self.string_manager.get("mainUi.log_str6"))
        if self.model is not None:
            self.model.to_save_loger()
        if self.agent is not None:
            self.agent.text_stream.disconnect()
            self.agent.final_answer.disconnect()
            self.agent.show_overlay.disconnect()
        self.windowClosed.emit()
        self.first_show = True
        super().closeEvent(event)

    def toggle_overlay(self):
        """显示或隐藏覆盖层"""
        if self.overlay and self.overlay.isVisible():
            self.overlay.hide()
            # print(self.string_manager.get("mainUi.log_str3"))
        else:
            # 创建并显示覆盖层
            self.overlay = TransparentOverlay(self)
            self.overlay.show()
            # print(self.string_manager.get("mainUi.log_str4"))

    def showEvent(self, event):
        super().showEvent(event)
        self.textEdit.textChanged.connect(lambda: self.on_text_changed())
        self.textEdit.returnPressed.connect(lambda: self.on_button_clicked())

        self.windowClosed.connect(lambda: self.on_close_window())
        self.btn_send.pressed.connect(lambda: self.on_btn_pressed())
        self.btn_send.released.connect(lambda: self.on_btn_released())

        self.btn_send.clicked.connect(lambda: self.on_button_clicked())
        self.btn_plus.pressed.connect(lambda: self.on_btn_pressed2())
        self.btn_plus.released.connect(lambda: self.on_btn_released2())
        self.btn_plus.clicked.connect(lambda: self.on_button_clicked2())

        self.agent.text_stream.connect(lambda token: self.append_text(token))
        self.agent.final_answer.connect(lambda reply: self.final_answer(reply))
        self.agent.show_overlay.connect(lambda: self.toggle_overlay())

        if self.agent and self.first_show:
            self.first_show = False
            self.toggle_overlay()

            # self.timer = QTimer()
            # self.timer.timeout.connect(lambda: self.on_time_over(True))
            # self.timer.start(5000)

            self.agent.is_start = True
            self.agent.init_send_message()
            self.agent.trigger_task.emit()

    def on_text_changed(self):
        text = self.textEdit.toPlainText()
        if text == "":
            self.init_text_edit()

    def on_time_over(self, is_over:bool):
        if self.timer is not None:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None
        if is_over:
            QMessageBox.critical(self , "错误", self.string_manager.get("main.error_sever"))
            self.close()

    @staticmethod
    def finish_message_pack(message, _type, is_thinking:bool = False):
        return [message, datetime.now(), _type, 0 if is_thinking else 1]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())