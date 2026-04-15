import sys
from symtable import Function

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QStackedWidget
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
import requests


API_BASE = "http://proxy.cn-south-1.gpu-instance.ppinfra.com:32181"  # 改成你的域名或公网IP


class LoginPage(QWidget):
    is_login_ok = False

    def __init__(self, switch_to_register, is_complete):
        super().__init__()
        self.setFixedSize(320, 200)
        self.is_complete = is_complete
        # 用户名行
        user_icon = QLabel()
        user_icon.setPixmap(QPixmap("user.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请输入用户名")

        user_layout = QHBoxLayout()
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.user_input)

        # 密码行
        pass_icon = QLabel()
        pass_icon.setPixmap(QPixmap("lock.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("请输入密码")
        self.pass_input.setEchoMode(QLineEdit.Password)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(pass_icon)
        pass_layout.addWidget(self.pass_input)

        # 按钮
        login_button = QPushButton("登录")
        login_button.clicked.connect(self.login_user)

        register_button = QPushButton("去注册")
        register_button.clicked.connect(switch_to_register)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(user_layout)
        main_layout.addLayout(pass_layout)
        main_layout.addWidget(login_button, alignment=Qt.AlignCenter)
        main_layout.addWidget(register_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def login_user(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        try:
            resp = requests.post(
                f"{API_BASE}/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if resp.status_code == 200:
                QMessageBox.information(self, "成功", "登录成功！")
                self.is_login_ok = True
                if self.is_complete is not None:
                    self.is_complete(True)
            else:
                QMessageBox.warning(self, "失败", resp.json().get("detail", "用户名或密码错误"))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法连接服务器: {e}")


class RegisterPage(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.setFixedSize(320, 200)

        # 用户名行
        user_icon = QLabel()
        user_icon.setPixmap(QPixmap("user.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请输入用户名")

        user_layout = QHBoxLayout()
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.user_input)

        # 密码行
        pass_icon = QLabel()
        pass_icon.setPixmap(QPixmap("lock.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("请输入密码")
        self.pass_input.setEchoMode(QLineEdit.Password)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(pass_icon)
        pass_layout.addWidget(self.pass_input)

        # 按钮
        register_button = QPushButton("注册")
        register_button.clicked.connect(self.register_user)

        login_button = QPushButton("去登录")
        login_button.clicked.connect(switch_to_login)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(user_layout)
        main_layout.addLayout(pass_layout)
        main_layout.addWidget(register_button, alignment=Qt.AlignCenter)
        main_layout.addWidget(login_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def register_user(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        try:
            resp = requests.post(
                f"{API_BASE}/register",
                json={"username": username, "password": password},
                timeout=5
            )
            if resp.status_code == 200:
                QMessageBox.information(self, "成功", "注册成功！")
            else:
                QMessageBox.warning(self, "失败", resp.json().get("detail", "未知错误"))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法连接服务器: {e}")


class LoginWindow(QStackedWidget):
    def __init__(self, on_complete_emit):
        super().__init__()
        self.on_complete_emit = on_complete_emit
        self.login_page = LoginPage(self.show_register, on_complete_emit)
        self.register_page = RegisterPage(self.show_login)

        self.addWidget(self.login_page)
        self.addWidget(self.register_page)

        self.setCurrentWidget(self.login_page)

    def show_login(self):
        self.setCurrentWidget(self.login_page)

    def show_register(self):
        self.setCurrentWidget(self.register_page)

    def closeEvent(self, event, /):
        if self.login_page and not self.login_page.is_login_ok:
            self.on_complete_emit(False)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.setWindowTitle("用户登录/注册")
    window.show()
    sys.exit(app.exec())
