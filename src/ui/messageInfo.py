from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize, QPoint
from PySide6.QtWidgets import QWidget, QStyledItemDelegate, QStyle

from string_manager import StringManager
from ui.messageUi import MessageWidget, MessageWidget2
from logger import SaveLogger

class MessageListModel(QAbstractListModel):
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

    def to_save_loger(self):
        if self.data_list is not None:
            SaveLogger.to_logger(self.data_list)

    def setData(self, index, value, role = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return False
        if role == Qt.ItemDataRole.DisplayRole:
            self.data_list[index.row()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

# 自定义代理（用于绘制Widget）
class MessageItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        self.string_manager = StringManager()
        print(self.string_manager.get("messageInfo.log_str1"))
        super().__init__(parent)
        self.current_widget = []

        # 创建自定义Widget
    def createEditor(self, parent, option, index):
        # 这里的Editor实际作为显示Widget（因为我们不需要编辑功能）
        print(self.string_manager.get("messageInfo.log_str2"), index.row())
        _data = index.data()
        if _data[2] == 2:
            widget = MessageWidget2(parent, index.data())
        else:
            widget = MessageWidget(parent, index.data())
        widget.row = index.row()
        widget.height_changed.connect(lambda idx=index: self.on_height_changed(idx))
        self.set_widget(widget, index)
        return widget

    # 更新Widget显示
    def setEditorData(self, editor, index):
        widget = self.get_widget(index)
        if widget is not None:
            widget.adjust_text_browser_size(index.data())

    # 绘制Widget
    def paint(self, painter, option, index):
        # 触发createEditor创建Widget，实现自定义显示
        widget = self.get_widget(index)
        if widget is None:
            print(self.string_manager.get("messageInfo.log_str3"),index.row())
            self.parent().openPersistentEditor(index)
            return

    def set_widget(self, widget, index):
        self.current_widget.insert(index.row(), widget)

    def get_widget(self, index):
        row = index.row()
        if 0 <= row < len(self.current_widget):  # 检查索引有效性
            return self.current_widget[row]
        return None  # 索引无效时返回None

    # 设置项的大小
    def sizeHint(self, option, index):
        widget:QWidget = self.get_widget(index)
        if widget is not None:
            return  QSize(widget.width(), widget.height())
        else:
            return QSize(410, 188)

    def on_height_changed(self, index):
        self.parent().update_scroll_range()