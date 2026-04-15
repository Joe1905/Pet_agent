from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt, Signal

class SendTextEdit(QTextEdit):
    returnPressed = Signal()   # 自定义信号

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() == Qt.ShiftModifier:
                # Shift+Enter 换行
                super().keyPressEvent(event)
            else:
                # 回车 -> 发送消息
                text = self.toPlainText().strip()
                if text:
                    self.returnPressed.emit()
                    self.clear()
        else:
            super().keyPressEvent(event)
