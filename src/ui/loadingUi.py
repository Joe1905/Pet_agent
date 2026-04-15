from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QMainWindow


class TransparentOverlay(QWidget):
    """半透明覆盖层窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置为无边框窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowStaysOnTopHint  # 始终在顶层
        )
        # 设置半透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")  # 黑色半透明

        # 创建GIF显示标签
        self.gif_label = QLabel(self)
        # 加载GIF
        self.movie = QMovie(":/load/loading.gif")  # 替换为你的GIF路径
        self.movie.setScaledSize(QSize(240, 240))
        if self.movie.isValid():
            # 设置GIF缩放模式
            self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        # 布局管理
        layout = QVBoxLayout(self)
        layout.addWidget(self.gif_label)
        self.setLayout(layout)

        # 跟随父窗口大小变化
        if parent:
            self.resize(parent.size())
            parent.resizeEvent = self.on_parent_resize

    def on_parent_resize(self, event):
        """父窗口大小改变时，调整覆盖层大小"""
        self.resize(event.size())
        # 调用原始的resizeEvent确保父窗口正常工作
        QMainWindow.resizeEvent(self.parent(), event)

    def mousePressEvent(self, event):
        """阻止鼠标事件穿透到下层窗口"""
        event.accept()