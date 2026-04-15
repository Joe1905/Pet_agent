import sys
import os
from PySide6.QtGui import QFontMetrics, QPixmap, QMovie, QAction, QGuiApplication, QCursor
from PySide6.QtWidgets import QApplication, QTextBrowser, QWidget, QTextEdit, QLabel, QDialog, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QEvent, QPoint
from PySide6.QtUiTools import QUiLoader
from datetime import datetime
from file_load import ResourceExtractor
from string_manager import StringManager
from ui.message_ui import Ui_Form
import ui.resource_rc

class ImagePreviewWindow(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片预览")
        # 无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        # 设置背景透明或半透明黑色，提升预览体验
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        # 隐藏滚动条
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 安装事件过滤器以拦截滚轮事件
        self.scroll_area.viewport().installEventFilter(self)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background: transparent;")
        
        self.original_pixmap = QPixmap(image_path)
        self.scale_factor = 1.0
        self.dragging = False
        self.last_mouse_position = QPoint()
        
        if not self.original_pixmap.isNull():
            self.init_window_size()
            self.update_image()
        else:
            self.image_label.setText("图片加载失败")
            self.resize(400, 300)
            self.center_on_screen()
            
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

    def init_window_size(self):
        # 直接设置为全屏
        self.showFullScreen()
        
        # 获取屏幕尺寸
        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_w = screen.width()
        screen_h = screen.height()
        
        img_w = self.original_pixmap.width()
        img_h = self.original_pixmap.height()
        
        # 目标尺寸：屏幕的 1/4 (即宽高各为屏幕的 1/2)
        target_w = screen_w // 2
        target_h = screen_h // 2
        
        # 如果图片原尺寸小于目标尺寸，使用原尺寸
        if img_w < target_w and img_h < target_h:
            self.scale_factor = 1.0
        else:
            # 否则缩放到目标尺寸
            self.scale_factor = min(target_w / img_w, target_h / img_h)

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_image(self):
        if self.original_pixmap.isNull():
            return
            
        scaled_w = int(self.original_pixmap.width() * self.scale_factor)
        scaled_h = int(self.original_pixmap.height() * self.scale_factor)
        
        self.image_label.setPixmap(self.original_pixmap.scaled(
            scaled_w, scaled_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.image_label.adjustSize()

    def do_scale(self, delta):
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor *= 0.9
            
        # 限制最小缩放比例
        self.scale_factor = max(0.1, self.scale_factor)
        self.update_image()

    def eventFilter(self, obj, event):
        if obj == self.scroll_area.viewport() and event.type() == QEvent.Type.Wheel:
            self.do_scale(event.angleDelta().y())
            return True # 拦截事件，防止滚动
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_position = event.globalPosition().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.last_mouse_position
            self.last_mouse_position = event.globalPosition().toPoint()
            
            # 移动滚动条
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()
        super().mouseDoubleClickEvent(event)


class MessageWidget(QWidget, Ui_Form):
    """高度会动态变化的QWidget，高度变化时发射信号"""
    height_changed = Signal()  # 高度变化信号

    add_times = 1
    message_type = 1
    text_browser_max_width = 280
    text_bg_start_x = 20
    text_bg_max_width = 320
    head_width = 80
    head_height = 80
    font_point_size = 18
    style_text = " border-image:  url(:/input/img_bubble.png) 50 50 50 50 stretch stretch;  \n    border-width: 50;"

    origin_height = 188
    row = -1

    def __init__(self, parent, data):
        super().__init__(parent)
        self.movie = None
        self.setupUi(self)
        self.setFixedSize(410, 188)
        self.is_show_thinking = False
        self.string_manager = StringManager()
        self.hide_thinking()

        self.text_info.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_info.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 设置背景透明，以便截图时只截取内容
        # 关键修改：设置无边框
        self.text_info.setStyleSheet("background: transparent; border: none;")
        
        # 安装事件过滤器以捕获双击事件
        # 关键修改：将事件过滤器安装到 viewport 上
        self.text_info.viewport().installEventFilter(self)

        self.load_image()
        self.image_text.setStyleSheet(self.style_text)

        self.init_text_browser()
        self.info_data = data
        self.image_path_str = None # 存储图片路径
        
        if data is not None:
            self.adjust_text_browser_size(data)
        else:
            self.adjust_text_browser_size(["这是一条默认文本", datetime.now(), 1, 1])

    def eventFilter(self, obj, event):
        # 关键修改：检查 obj 是否为 viewport
        if obj == self.text_info.viewport() and event.type() == QEvent.Type.MouseButtonDblClick:
            if self.image_path_str:
                self.show_image_preview()
                return True
        return super().eventFilter(obj, event)

    def show_image_preview(self):
        if self.image_path_str:
            preview_window = ImagePreviewWindow(self.image_path_str, self)
            preview_window.exec()

    def image_path(self)->str:
        return ":/head/head1.png"

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.image_head.geometry().contains(pos):
                self.on_image_clicked()
                event.accept()
                return
        super().mousePressEvent(event)

    def on_image_clicked(self):
        #todo 点击头像函数
        # print("on_image_clicked")
        pass

    def load_image(self):
        pixmap = QPixmap(self.image_path())
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.head_width,
                self.head_height,
                Qt.AspectRatioMode.KeepAspectRatio,  # 保持图片比例
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放
            )
            self.image_head.setPixmap(scaled_pixmap)
            self.image_head.adjustSize()
        else:
            self.image_head.setText(self.string_manager.get("messageUi.log_str1"))

    def init_text_browser(self):
        font = self.text_info.font()
        font.setPointSize(self.font_point_size)
        self.text_info.setFont(font)

    def adjust_time_text(self, _time):
        self.text_time.setText(_time)
        font_metrics = QFontMetrics(self.text_time.font())
        text_width = font_metrics.horizontalAdvance(self.text_time.text())

        # 设置固定宽度（留出边距）
        self.text_time.setFixedWidth(text_width + 20)

    def show_thinking(self):
        self.is_show_thinking = True
        if self.thinking is not None:
            self.thinking.setVisible(True)
            self.thinking_text.setVisible(True)
            self.text_time.setVisible(False)

            self.movie = QMovie(":/load/thinking.gif")  # 替换为你的GIF路径
            self.movie.setScaledSize(QSize(60, 60))
            if self.movie.isValid():
                # 设置GIF缩放模式
                self.thinking.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.thinking.setMovie(self.movie)
                self.movie.start()


    def hide_thinking(self):
        self.is_show_thinking = False
        if self.thinking is not None:
            self.thinking.setVisible(False)
            self.thinking_text.setVisible(False)
            self.text_time.setVisible(True)

    def get_info_data(self):
        return self.info_data

    def animate_resize(self, text_rect, bg_rect, text_pixmap=None):
        if hasattr(self, 'anim_group') and self.anim_group.state() == QParallelAnimationGroup.State.Running:
            self.anim_group.stop()
            # 如果有正在进行的动画，清理临时组件
            if hasattr(self, 'temp_text_label'):
                self.temp_text_label.deleteLater()
                del self.temp_text_label

        # 解除固定尺寸限制
        self.text_info.setMinimumSize(0, 0)
        self.text_info.setMaximumSize(16777215, 16777215)
        self.image_text.setMinimumSize(0, 0)
        self.image_text.setMaximumSize(16777215, 16777215)

        self.anim_group = QParallelAnimationGroup(self)

        # 计算起始矩形（左下角展开）
        # 文本框起始点：左下角 (x, y + height)
        start_text_rect = QRect(
            text_rect.x(),
            text_rect.y() + text_rect.height(),
            0, 0
        )
        # 背景图起始点：左下角 (x, y + height)
        start_bg_rect = QRect(
            bg_rect.x(),
            bg_rect.y() + bg_rect.height(),
            0, 0
        )

        # 文本动画处理
        if text_pixmap:
            # 创建临时 Label 显示截图
            self.temp_text_label = QLabel(self)
            self.temp_text_label.setPixmap(text_pixmap)
            self.temp_text_label.setScaledContents(True) # 允许内容缩放
            self.temp_text_label.show()
            self.temp_text_label.raise_() # 确保在最上层
            
            # 对临时 Label 进行动画
            anim_text = QPropertyAnimation(self.temp_text_label, b"geometry")
            anim_text.setDuration(400)
            anim_text.setStartValue(start_text_rect)
            anim_text.setEndValue(text_rect)
            anim_text.setEasingCurve(QEasingCurve.OutBack)
            
            # 动画结束后清理
            def on_anim_finished():
                if hasattr(self, 'temp_text_label'):
                    self.temp_text_label.deleteLater()
                    del self.temp_text_label
                self.text_info.setVisible(True) # 显示真实的文本框
                
            self.anim_group.finished.connect(on_anim_finished)
        else:
            # 如果没有截图（例如思考中），直接对 text_info 动画
            anim_text = QPropertyAnimation(self.text_info, b"geometry")
            anim_text.setDuration(400)
            anim_text.setStartValue(start_text_rect)
            anim_text.setEndValue(text_rect)
            anim_text.setEasingCurve(QEasingCurve.OutBack)

        # 背景图动画
        anim_bg = QPropertyAnimation(self.image_text, b"geometry")
        anim_bg.setDuration(400)
        anim_bg.setStartValue(start_bg_rect)
        anim_bg.setEndValue(bg_rect)
        anim_bg.setEasingCurve(QEasingCurve.OutBack)

        self.anim_group.addAnimation(anim_text)
        self.anim_group.addAnimation(anim_bg)
        self.anim_group.start()

    def adjust_text_browser_size(self, _data):
        self.info_data = _data
        _text = ""
        _time = datetime.now()
        is_image = False
        self.image_path_str = None # 重置图片路径
        
        if _data is not None:
            _text = _data[0]
            _time = _data[1].strftime(self.string_manager.get("messageUi.time_table"))
            if _data[3] == 0:
                _text = ""
            else:
                self.hide_thinking()
            
            # 检查是否为图片消息
            if _text.startswith("image:"):
                is_image = True
                self.image_path_str = _text[6:] # 去掉 "image:" 前缀
                
        self.adjust_time_text(str(_time))
        
        if is_image:
            # 处理图片显示
            # 使用 HTML 插入图片
            # 限制图片最大宽度
            max_img_width = 200
            
            # 加载图片获取尺寸
            pixmap = QPixmap(self.image_path_str)
            if not pixmap.isNull():
                img_w = pixmap.width()
                img_h = pixmap.height()
                
                # 缩放图片
                if img_w > max_img_width:
                    ratio = max_img_width / img_w
                    img_w = max_img_width
                    img_h = int(img_h * ratio)
                
                # 生成 HTML
                html = f"<img src='{self.image_path_str}' width='{img_w}' height='{img_h}'>"
                self.text_info.setHtml(html)
                
                # 设置尺寸
                width = img_w + 20 # 加上一些边距
                height = img_h + 20
                
                # 设置文本框大小
                self.text_info.setFixedSize(width, height)
                
                # 计算位置
                if isinstance(self, MessageWidget2):
                    new_x = self.text_bg_start_x
                else:
                    new_x = self.current_browser_x(width)
                    
                bg_width = width + 40
            else:
                # 图片加载失败
                self.text_info.setText("图片加载失败")
                self.text_info.document().adjustSize()
                width = int(self.text_info.document().idealWidth()) + 20
                height = int(self.text_info.document().size().height()) + 5
                if isinstance(self, MessageWidget2):
                    new_x = self.text_bg_start_x
                else:
                    new_x = self.current_browser_x(width)
                bg_width = width + 40
                
        else:
            # 原有的文本处理逻辑
            self.text_info.setText(_text)
            # 临时禁用换行以计算完整宽度
            self.text_info.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            full_width = int(self.text_info.document().idealWidth()) + 20

            # 判断是否需要换行
            current_x = self.text_info.x()
            need_wrap = full_width > self.text_browser_max_width
            bg_width = self.text_bg_max_width

            if need_wrap:
                # 设置按组件宽度换行
                self.text_info.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                width = self.text_browser_max_width
                self.text_info.setFixedWidth(width)

                # 关键修改2：强制文档重新计算换行后的高度
                self.text_info.document().setTextWidth(width)  # 明确设置文档宽度（用于换行计算）
                # self.text_browser.document().adjustSize()  # 强制更新文档尺寸
                height = int(self.text_info.document().size().height()) + 5  # +5 预留边距
                new_x = self.text_bg_start_x
            elif self.is_show_thinking:
                new_x = self.text_bg_start_x
                width = 120
                bg_width = 181
                height = 56
            else:
                # 不换行，使用实际宽度
                self.text_info.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

                # 计算背景图尺寸
                bg_width = max(100, min(self.text_bg_max_width, full_width + 40))
                width = bg_width - 40
                self.text_info.setFixedWidth(width)
                # 计算高度
                self.text_info.document().adjustSize()
                height = int(self.text_info.document().size().height()) + 5
                new_x = self.current_browser_x(width)

        # 限制最小高度
        clamp_height = max(height, 28)

        bg_height = max(70, clamp_height + 25)

        # 更新组件位置和尺寸
        
        # 重新计算布局逻辑：
        base_y = 10 # 基础Y坐标，可以根据头像位置调整
        
        if isinstance(self, MessageWidget2):
            bg_y = 50
            text_y = 65
        else:
            # MessageWidget (用户) 的默认位置
            # 用户反馈“用户发送的气泡框过于偏上”
            # 之前的设置是 bg_y = 10
            # 让我们尝试下移一点，比如 bg_y = 50，与机器人回复保持一致
            bg_y = 50
            text_y = 65
            
        target_bg_rect = QRect(
            self.current_bg_image_x(new_x),
            bg_y,
            bg_width,
            bg_height
        )
        
        target_text_rect = QRect(
            new_x,
            bg_y + 12, # 文本相对于背景下移 12 像素
            width,
            clamp_height
        )

        # 如果 is_show_thinking，我们调整了 text_info 的大小，但没有调整 thinking 的位置。
        # thinking 应该位于气泡内部。
        if self.is_show_thinking:
            # 确保 thinking 组件在气泡内
            if self.thinking:
                self.thinking.setGeometry(target_text_rect)
                self.thinking.raise_() # 确保在最上层
            self.animate_resize(target_text_rect, target_bg_rect)
        else:
            # 截图方案：
            # 1. 设置 text_info 为最终大小和位置
            self.text_info.setGeometry(target_text_rect)
            # 2. 截图
            text_pixmap = self.text_info.grab()
            # 3. 隐藏 text_info
            self.text_info.setVisible(False)
            # 4. 执行动画
            self.animate_resize(target_text_rect, target_bg_rect, text_pixmap)

        # 调整父组件尺寸
        all_height = max(
            target_bg_rect.y() + target_bg_rect.height() + 15,
            self.image_head.pos().y() + self.head_height
        )
        self.setFixedSize(self.width(), all_height)

        print(f"第{self.row}个all_height", all_height)
        print(f"第{self.row}个位置", self.pos().y())
        self.origin_height = all_height
        self.add_times += 1
        # 关键修改3：强制父组件和布局更新
        self.text_info.updateGeometry()
        self.updateGeometry()
        # 延迟发射信号，确保高度已更新完成
        QTimer.singleShot(0, self.height_changed.emit)

    def sizeHint(self):
        return QSize(410, self.origin_height)  # 或者根据内容动态计算

    def resizeEvent(self, event):
        """捕获自身大小变化，发射高度变化信号"""
        if event.oldSize().height() != self.height():
            self.height_changed.emit()  # 高度变化时发射信号
        super().resizeEvent(event)

    def get_current_height(self):
        return self.text_info.height()

    def current_bg_image_x(self, new_x):
        return new_x - 10

    def current_browser_x(self, full_width):
        return self.text_browser_max_width - full_width + self.text_bg_start_x

class MessageWidget2(MessageWidget):

    message_type = 2
    text_bg_start_x = 130
    style_text = " border-image:  url(:/input/img_bubble2.png) 50 50 50 50 stretch stretch;  \n    border-width: 50;"

    def __init__(self, parent, data):
        super().__init__(parent, data)
        self.image_head.move(10, 50)
        self.text_info.move(self.text_bg_start_x, 65)
        self.image_text.move(self.current_bg_image_x(self.text_bg_start_x), 50)

        self.show_thinking()
        self.adjust_text_browser_size(data)

    def current_bg_image_x(self, new_x):
        return new_x - 40

    def current_browser_x(self, full_width):
        return self.text_bg_start_x


    def image_path(self)->str:
        pet_config = ResourceExtractor.get_pet_config()
        config = ResourceExtractor.get_setting_config()
        pet_index = int(config["General_Set"]["current_index"])
        return pet_config[f"Pet{pet_index}"]["pet_head"]


if __name__ == "__main__":
    app = QApplication([])
    window = MessageWidget(None, None)
    window.show()
    app.exec()
