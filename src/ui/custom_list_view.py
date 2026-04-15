from PySide6.QtCore import Qt, QModelIndex, QRect
from PySide6.QtWidgets import QListView, QAbstractItemView, QStyleOptionViewItem, QStyle

from string_manager import StringManager


class CustomListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.string_manager = StringManager()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 关键设置：允许项高度不同
        self.setUniformItemSizes(False)
        # 使用像素级滚动，确保滚动平滑
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # 关键：禁用项尺寸缓存（避免布局计算错误）
        self.setUniformItemSizes(False)
        self.viewOptions = self.get_view_options()

    def update_scroll_range(self):
        """手动计算总高度，更新滚动条最大范围"""
        self.doItemsLayout()
        total_height = 0
        count = self.model().rowCount()
        for row in range(count):
            # 获取每项的实际高度（通过委托的sizeHint）
            index = self.model().index(row, 0)
            size = self.itemDelegate().sizeHint(self.viewOptions, index)
            total_height += size.height()

        # 计算滚动条最大范围（总高度 - 视口高度）
        viewport_height = self.viewport().height()
        max_scroll = max(0, total_height - viewport_height)
        self.verticalScrollBar().setMaximum(max_scroll)
        self.verticalScrollBar().setValue(max_scroll)

    def get_view_options(self):
        """正确构造视图样式选项（替代viewOptions()）"""
        # 手动构造QStyleOptionViewItem并初始化
        option = QStyleOptionViewItem()
        option.initFrom(self)  # 从视图初始化选项（包含字体、颜色等）
        option.state |= QStyle.StateFlag.State_Enabled  # 启用状态
        return option


