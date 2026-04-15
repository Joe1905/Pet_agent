import os
import sys
from PySide6.QtCore import Qt, QSize, QObject, Signal
from PySide6.QtGui import QMovie, QAction, QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QLabel, QVBoxLayout, \
    QMessageBox

from file_load import ResourceExtractor
from link_model import ChatAgent
from string_manager import StringManager
from ui.favor import FavorListWindow
from ui.login import LoginWindow
from ui.mainUi import MainWindow
import ui.resource_rc
from ui.memoryDialog import MemoryWindow

# from ai_agent import AIAgent

global_main_window:MainWindow

class DesktopPet(QWidget, QObject):
    def __init__(self):
        super().__init__()
        self.string_manager = StringManager()
        self.chat_window = None #MainWindow(self.on_close_window)
        self.drag_position = None
        # 提取需要隐藏的资源到临时目录
        temp_res_dir = ResourceExtractor.extract_to_temp([
            "pet_image",
            "config"
        ])
        config = ResourceExtractor.get_pet_config(temp_res_dir)
        if config is None:
            result = QMessageBox.critical(self, "错误",  self.string_manager.get("main.error_load"))
            if result == QMessageBox.StandardButton.Ok or result == QMessageBox.StandardButton.Cancel:
                sys.exit(1)
            return
        self.set_config = ResourceExtractor.get_setting_config()
        self.pet_index = self.set_config["General_Set"]["current_index"]
        self.gif_path = os.path.join(temp_res_dir, config[f"Pet{self.pet_index}"]["pet_icon"])
        self.config = config

        self.chat_window_state_changed = False

        # 获取最大屏幕
        desktop = QGuiApplication.primaryScreen()
        self.max_x = desktop.size().width()- self.width()
        self.max_y = desktop.size().height() - self.height()

        self.chat_window_open = False
        self.check_window = None
        self.memory_dialog = None
        self.agent = ChatAgent.instance()
        self.agent.update_memory.connect(lambda memory:self.on_update_memory(memory))
        self.init_ui()

        # 初始化界面
    def init_ui(self):
        # 父容器
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.pet_width = self.config.getint(f"Pet{self.pet_index}", "WIDTH")
        self.pet_height = self.config.getint(f"Pet{self.pet_index}", "HEIGHT")
        self.setFixedSize(self.pet_width + 20, self.pet_height + 20)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - self.width() - 500, screen_geometry.height() - self.height() - 100)

        # 宠物信息

        # 获取动图的正确路径
        self.pet_movie = QMovie(self.gif_path)
        self.pet_movie.setScaledSize(QSize(self.pet_width, self.pet_height))
        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(0,0,self.pet_width,self.pet_height)
        self.pet_label.setMovie(self.pet_movie)
        self.pet_movie.start()
        self.nickname = self.set_config["Nick_Name"][f"nickname{self.pet_index}"]

        # 创建一个布局管理器
        layout = QVBoxLayout(self)
        # 将 QLabel 添加到布局管理器中
        layout.addWidget(self.pet_label)
        # 设置布局管理器中的对齐方式，以让 QLabel 在中心显示
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 将布局管理器设置为父容器的布局
        self.setLayout(layout)

        # 右键功能区
        self.menu = QMenu(self)
        menus:list = self.string_manager.get("main.menu_list")
        menu_triggers:list = [self.show_settings_dialog, self.close_system]
        self.menu.addActions([QAction(menus[i], self, triggered=menu_triggers[i]) for i in range(len(menus))])
        self.show()

    def close_system(self):
        self.close()

    def on_close_window(self):
        self.chat_window = None
        self.chat_window_open = False
        self.chat_window_state_changed = True
        global global_main_window
        global_main_window = None

    # 快捷键启动窗口
    def toggle_chat_window(self):
        if self.chat_window_open:
            self.chat_window.close()
            self.chat_window = None
            self.chat_window_open = False
            self.chat_window_state_changed = True
        else:
            if self.chat_window is None:
                self.chat_window = MainWindow(self.on_close_window)
            self.chat_window.update_agent()
            self.chat_window.show()
            self.chat_window_open = True
            self.chat_window_state_changed = True

        global global_main_window
        global_main_window = self.chat_window


    # 根据鼠标更新对话框位置
    def update_chat_dialog_position(self):
        # if hasattr(self, 'chat_dialog') and self.chat_dialog.isVisible():
        #     dialog_position = self.mapToGlobal(QPoint(self.pet_pixmap.width() // 2, -self.chat_dialog.height()))
        #     self.chat_dialog.move(dialog_position)
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.update_chat_dialog_position()

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.toggle_chat_window()

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())

    def show_settings_dialog(self):
        self.to_show_select_window()

    def reset_Memory(self):
        ResourceExtractor.reset_setting_config(None)

    def to_show_current_memory(self):
        if self.memory_dialog is None:
            self.memory_dialog = MemoryWindow()
            self.memory_dialog.chat = ChatAgent.instance()
        self.memory_dialog.show()

    def on_update_memory(self, memory_str):
        if self.memory_dialog is None:
            return
        self.memory_dialog.show_loading(False)
        self.memory_dialog.show_memory_signal.emit(memory_str)
        if memory_str != "-1":
            self.memory_dialog.on_save_memory(memory_str)

    def set_chat_window_closed(self):
        self.chat_window_open = False

    # 控制宠物自由走动和随机提问功能
    def toggle_walk(self, state):
        # if state:
        #     self.timer.start(50)
        # else:
        #     self.timer.stop()
        pass

    def show_pet(self):
        # self.show()
        # if self.stop_timer.isActive():
        #     self.bubble.show()
        pass

    def hide_pet(self):
        # self.hide()
        # self.bubble.hide()
        pass

    def closeEvent(self, event):
        if self.chat_window is not None:
            self.chat_window.close()
            self.chat_window = None
        # 退出时清理临时文件
        ResourceExtractor.cleanup_temp()
        # print(self.string_manager.get("main.clearn_temp_file"))
        QApplication.quit()

    def to_show_select_window(self):
        if self.check_window is None:
            self.check_window = FavorListWindow()
            self.check_window.windowClosed.connect(lambda :self.on_window_close())
            self.check_window.open_memory.connect(lambda :self.to_show_current_memory())
        if self.check_window.isVisible():
            self.check_window.close()
        else:
            self.check_window.show()

    def on_window_close(self):
        if self.check_window is not None:
            self.check_window = None

# 主程序入口
if __name__ == "__main__":

    def on_complete_emit(is_complete:bool):
        if is_complete:
            on_login_ok()
        else:
            app.quit()

    def on_login_ok():
        # if window is not None:
        #     window.close()

        pet.show()

    app = QApplication(sys.argv)
    # 关键：关闭“最后一个窗口关闭时退出”的默认行为
    app.setQuitOnLastWindowClosed(False)
    strings = StringManager()
    # window = LoginWindow(on_complete_emit)
    pet = DesktopPet()
    # pet.hide()
    # window.setWindowTitle("用户登录/注册")
    # window.show()
    sys.exit(app.exec())