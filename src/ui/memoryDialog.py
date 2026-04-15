import os
import sys
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QTextEdit, QMainWindow, QPushButton, QMessageBox, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer,QFile
from PySide6.QtUiTools import QUiLoader

from file_load import ResourceExtractor
from string_manager import StringManager
from ui.loadingUi import TransparentOverlay

# 判断是否为打包后的环境
if getattr(sys, 'frozen', False):
    # 打包后，ui文件在 sys._MEIPASS 目录下的 ui 文件夹中
    base_path = sys._MEIPASS
    ui_path = os.path.join(base_path, "ui", "memoryUi.ui")
else:
    # 开发环境，使用当前脚本的目录
    base_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(base_path, "memoryUi.ui")

# 加载UI文件
# Form, Window = uic.loadUiType(ui_path)

class MemoryWindow(QMainWindow):
    show_memory_signal = Signal(str)
    save_memory_signal = Signal(bool)

    def __init__(self):
        super().__init__()

        # 加载 .ui 文件
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)  # 以只读方式打开 UI 文件
        loader = QUiLoader()
        # 将 UI 加载到当前窗口（self 是 QMainWindow 实例）
        self.ui = loader.load(ui_file, self)
        ui_file.close()  # 关闭文件

        self.text_edit:QTextEdit = self.findChild(QTextEdit,"textEdit")
        self.btn_change = self.findChild(QPushButton,"btn_change")
        self.btn_enter = self.findChild(QPushButton,"btn_enter")
        self.btn_update = self.findChild(QPushButton,"btn_update")
        self.need_change = False
        self.overlay = None
        self.string_manager = StringManager()
        self.chat = None
        # 读取配置文件
        self.config = ResourceExtractor.get_setting_config()
        self.memory_str = self.config["Memory"]["current_memory"]
        self.on_show_memory(self.memory_str)

        self.btn_change.clicked.connect(lambda :self.on_change_text())
        self.btn_enter.clicked.connect(lambda :self.on_enter_click())
        self.btn_update.clicked.connect(lambda :self.on_update_memory())
        self.show_memory_signal.connect(lambda text:self.on_show_memory(text))
        self.save_memory_signal.connect(lambda is_success:self.on_save_complete(is_success))

    def on_show_memory(self, text):
        if self.text_edit is None:
            # print("text_edit不存在！")
            return
        if text == "-1":
            QMessageBox.information(self, "提示", "无更新的记录可总结" )
            return
        self.text_edit.setText(text)
        self.text_edit.setEnabled(self.need_change)

    def on_change_text(self):
        self.need_change = not self.need_change
        self.text_edit.setEnabled(self.need_change)
        if self.need_change:
            self.text_edit.setFocus()

    def on_enter_click(self):
        # 获取文本框中的内容
        new_memory = self.text_edit.toPlainText()
        if new_memory == self.memory_str:
            self.close()
            return
        self.on_save_memory(new_memory)

    def on_save_memory(self, new_memory):
        current_memory = self.config["Memory"]["current_memory"]
        if ResourceExtractor.text_is_equal(current_memory, new_memory):
            # print("此处return")
            return

        ResourceExtractor.set_setting_config(
            {
                "Memory":
                    {
                        "current_memory": new_memory,
                        "current_file": self.config["Memory"]["current_file"]
                    }
            },  self.save_memory_signal)

    def on_save_complete(self, is_success):
        if is_success:
            QMessageBox.information(self, "提示", "保存成功" )
        else:
            QMessageBox.critical(self, "错误", "保存失败")

    def show_loading(self, is_loading):
        if self.overlay is None:
            self.overlay = TransparentOverlay(self)
        if is_loading:
            self.overlay.show()
            self.text_edit.setEnabled(False)
        else:
            self.overlay.hide()

    def on_update_memory(self):
        if self.chat is not None:
            self.show_loading(True)
            self.chat.run_type = 2
            self.chat.trigger_task.emit()

    def closeEvent(self, event):
        if self.chat is not None:
            self.chat.memory_dialog = None
