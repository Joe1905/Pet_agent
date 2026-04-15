import sys
import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtWidgets import QListView, QWidget, QLabel, QProgressBar, QAbstractItemView, QStyledItemDelegate, \
    QHBoxLayout, QCheckBox, QLineEdit, QPushButton
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal, QFile

from file_load import ResourceExtractor
from link_model import ChatAgent, LocalLLM
from string_manager import StringManager
import ui.resource_rc
from ui.favor_ui import Ui_mainWidget   # 生成的类

# 判断是否为打包后的环境
if getattr(sys, 'frozen', False):
    # 打包后，ui文件在 sys._MEIPASS 目录下的 ui 文件夹中
    base_path = sys._MEIPASS
    ui_path = os.path.join(base_path, "ui", "favorDialog.ui")
else:
    # 开发环境，使用当前脚本的目录
    base_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(base_path, "favorDialog.ui")

class FavorListWindow(QWidget):
    on_selected_changed = Signal(int)
    windowClosed = Signal()
    open_memory = Signal()

    def __init__(self):
        super().__init__()
        # 加载 .ui 文件
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)  # 以只读方式打开 UI 文件
        loader = QUiLoader()
        # 将 UI 加载到当前窗口（self 是 QMainWindow 实例）
        self.ui = loader.load(ui_file, self)
        ui_file.close()  # 关闭文件
        if self.windowClosed is None:
            self.windowClosed = Signal()
        if self.open_memory is None:
            self.open_memory = Signal()
        self.list_view = self.findChild(QListView, "listView")
        self.btn1 = self.findChild(QPushButton, "btn1")
        self.btn2 = self.findChild(QPushButton, "btn2")
        self.lineEdit = self.findChild(QLineEdit, "lineEdit")
        self.is_edit = False
        self.lineEdit.setEnabled(False)
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.btn1.clicked.connect(lambda: self.on_button_clicked(1))
        self.btn2.clicked.connect(lambda: self.on_button_clicked(2))
        self.pushButton.clicked.connect(lambda: self.on_button_clicked(3))
        self.model = None
        self.pet_config = None
        self.set_config = ResourceExtractor.get_setting_config()
        self.lineEdit.setText(self.set_config["Url"]["server_url"])
        self.delegate = None
        self.init_list_view()
        self.to_add_pet_item()
        self.on_selected_changed.connect(lambda index:self.on_change(index))

    def on_button_clicked(self, type:int):
        if type == 1:
            self.open_memory.emit()
        elif type == 2:
            ResourceExtractor.reset_setting_config(None)
        else:
            self.is_edit = not self.is_edit
            self.lineEdit.setEnabled(self.is_edit)
            self.pushButton.setText("保存" if self.is_edit else "修改")
            url = self.lineEdit.text()

            if self.is_edit:
                self.lineEdit.setFocus()
            else:
                ResourceExtractor.set_setting_config({
                    "Url": {"server_url": url}
                }, None)

    def closeEvent(self, event):
        self.windowClosed.emit()
        self.windowClosed.disconnect()
        self.open_memory.disconnect()
        super().closeEvent(event)

    def init_list_view(self):
        if self.list_view is None:
            return

        self.list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 关键设置：允许项高度不同
        self.list_view.setUniformItemSizes(False)
        # 使用像素级滚动，确保滚动平滑
        self.list_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # 关键：禁用项尺寸缓存（避免布局计算错误）
        self.list_view.setUniformItemSizes(False)
        self.model:FavorListModel = FavorListModel()
        self.list_view.setModel(self.model)
        self.delegate = FavorItemDelegate(self.on_selected_changed, self.list_view)
        self.list_view.setItemDelegate(self.delegate)

    def to_add_pet_item(self):
        if self.model is None:
            return
        self.pet_config = ResourceExtractor.get_pet_config()
        index = 1
        self.model.clearAllItems()
        while True:
            section_name = f"Pet{index}"
            # 先检查section是否存在
            if not self.pet_config.has_section(section_name):
                break  # 不存在则退出循环

            # 存在则继续处理
            current_config = self.pet_config[section_name]
            self.model.addItem(current_config)
            index += 1
    def on_change(self, index):
        config = ResourceExtractor.get_setting_config()
        cur_index = config["General_Set"]["current_index"]
        if index == cur_index:
            return
        ResourceExtractor.set_setting_config(
            {
                "General_Set": {"current_index": index}
            }, None)

class FavorWidget(QWidget, Ui_mainWidget):
    head_width = 60
    head_height = 60
    img_width = 35
    img_height = 35

    max_favor = 100

    def __init__(self, parent, data):
        super().__init__(parent)
        self.on_selected_changed = None
        self.string_manager = StringManager()
        # 判断是否为打包后的环境
        # if getattr(sys, 'frozen', False):
        #     # 打包后，ui文件在 sys._MEIPASS 目录下的 ui 文件夹中
        #     base_path = sys._MEIPASS
        #     ui_path = os.path.join(base_path, "ui", "favor.ui")
        # else:
        #     # 开发环境，使用当前脚本的目录
        #     base_path = os.path.dirname(os.path.abspath(__file__))
        #     ui_path = os.path.join(base_path, "favor.ui")
        # # 加载 .ui 文件
        # ui_file = QFile(ui_path)
        # ui_file.open(QFile.ReadOnly)  # 以只读方式打开 UI 文件
        # loader = QUiLoader()
        # # 将 UI 加载到当前窗口（self 是 QMainWindow 实例）
        # self.ui = loader.load(ui_file, self)
        # ui_file.close()  # 关闭文件
        self.setupUi(self)
        self.set_config = ResourceExtractor.get_setting_config()
        self.pet_config = data
        self.pet_index = int(data["index"])
        self.image_path = self.pet_config["pet_head"]
        self.progressBar.setMaximum(self.max_favor)
        self.load_image(self.image_path, self.image_head, self.head_width, self.head_height)
        self.load_image(":/favor/aixin.png", self.image_favor, self.img_width, self.img_height)
        self.image_favor.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.is_edit = False
        self.lineEdit.setText(self.set_config["Nick_Name"][f"nickname{self.pet_index}"])
        self.lineEdit.setEnabled(False)
        self.pushButton.clicked.connect(lambda :self.on_edit_state_change())
        self.on_change_state()
        self.btn_choice.stateChanged.connect(lambda :self.on_favor_change())
        self.update_ui()


    def on_edit_state_change(self):
        self.is_edit = not self.is_edit
        self.on_change_state()
        if self.is_edit:
            self.lineEdit.setFocus()
        else:
            ResourceExtractor.set_setting_config({
                    "Nick_Name":
                        {
                            f"nickname{self.pet_index}": self.lineEdit.text(),
                        }
                }, None)

    def on_change_state(self):
        self.lineEdit.setEnabled(self.is_edit)
        self.pushButton.setText("保存" if self.is_edit else "修改")

    def mousePressEvent(self, event: QMouseEvent):
        """重写鼠标按下事件，响应点击"""
        # 忽略右键点击（可选）
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        self.btn_choice.setChecked(True)

        super().mousePressEvent(event)

    def update_ui(self):
        self.update_choice()
        self.on_prog_change()

    def set_change_signal(self,  on_selected_changed):
        self.on_selected_changed = on_selected_changed
        self.on_selected_changed.connect(lambda :self.update_choice())

    def load_image(self, image_path:str, image:QLabel, width, height):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                width,
                height,
                Qt.AspectRatioMode.KeepAspectRatio,  # 保持图片比例
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放
            )
            image.setPixmap(scaled_pixmap)
            image.adjustSize()
        else:
            image.setText(self.string_manager.get("messageUi.log_str1"))

    def update_choice(self, index = 0):
        if index == 0:
            config = ResourceExtractor.get_setting_config()
            index = int(config["General_Set"]["current_index"])
        self.btn_choice.setChecked(index == self.pet_index)

    def on_favor_change(self):
        if self.btn_choice is None:
            return
        index = self.pet_index if self.btn_choice.isChecked() else (self.pet_index - 1 if self.pet_index == 2 else 2)
        config = ResourceExtractor.get_setting_config()
        cur_index = int(config["General_Set"]["current_index"])
        if cur_index == index:
            return
        self.on_selected_changed.emit(index)
        ResourceExtractor.set_setting_config( {"General_Set":{"current_index":index}}, None)
        LocalLLM.request_clear_history()

    def on_prog_change(self):
        if self.progressBar is None:
            return
        config = ResourceExtractor.get_setting_config()
        self.progressBar.setValue(int(config["Talk_Times"][f"pet_{self.pet_index}"]))

class FavorListModel(QAbstractListModel):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data_list = data if data is not None else []  # 存储列表项数据

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.data_list):
            return None

        item = self.data_list[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return item  # 返回显示文本（实际使用时可存储更复杂数据）
        return None

    # 添加新项
    def addItem(self, text):
        length = len(self.data_list)
        self.beginInsertRows(QModelIndex(), length, length)
        self.data_list.append(text)
        self.endInsertRows()

    def clearAllItems(self):
        self.beginResetModel()  # 通知视图：模型即将“完全重置”
        self.data_list.clear()  # 清空内部数据
        self.endResetModel()  # 通知视图：模型已重置，视图会刷新

# 自定义代理（用于绘制Widget）
class FavorItemDelegate(QStyledItemDelegate):
    def __init__(self, on_selected_changed, parent=None):
        super().__init__(parent)
        self.signal = on_selected_changed
        self.current_widget = []

        # 创建自定义Widget
    def createEditor(self, parent, option, index):
        _data = index.data()
        widget = FavorWidget(parent, index.data())
        widget.set_change_signal(self.signal)
        self.set_widget(widget, index)
        return widget

    def paint(self, painter, option, index):
        # 触发createEditor创建Widget，实现自定义显示
        widget:FavorWidget = self.get_widget(index)
        if widget is None:
            self.parent().openPersistentEditor(index)
            return

    def set_widget(self, widget, index):
        row = index.row()
        # 确保列表长度足够，避免索引越界
        while len(self.current_widget) <= row:
            self.current_widget.append(None)
        self.current_widget[row] = widget

    def get_widget(self, index):
        row = index.row()
        if 0 <= row < len(self.current_widget):
            return self.current_widget[row]
        return None

    # 设置项的大小
    def sizeHint(self, option, index):
         return QSize(397, 100)

