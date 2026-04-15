# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'chat.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QWidget)

from ui.custom_list_view import CustomListView
from ui.send_text_edit import SendTextEdit
import ui.resource_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(468, 832)
        self.btn_plus = QPushButton(Form)
        self.btn_plus.setObjectName(u"btn_plus")
        self.btn_plus.setGeometry(QRect(400, 760, 64, 60))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_plus.sizePolicy().hasHeightForWidth())
        self.btn_plus.setSizePolicy(sizePolicy)
        self.btn_plus.setStyleSheet(u"border:none")
        icon = QIcon()
        icon.addFile(u":/btn/btn_plus.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.btn_plus.setIcon(icon)
        self.btn_plus.setIconSize(QSize(60, 60))
        self.btn_plus.setAutoDefault(False)
        self.btn_send = QPushButton(Form)
        self.btn_send.setObjectName(u"btn_send")
        self.btn_send.setGeometry(QRect(330, 760, 64, 60))
        sizePolicy.setHeightForWidth(self.btn_send.sizePolicy().hasHeightForWidth())
        self.btn_send.setSizePolicy(sizePolicy)
        self.btn_send.setStyleSheet(u"border:none;\n"
"scale:0.6")
        icon1 = QIcon()
        icon1.addFile(u":/btn/btn_send.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon1.addFile(u":/btn/btn_send_hover.png", QSize(), QIcon.Mode.Active, QIcon.State.On)
        self.btn_send.setIcon(icon1)
        self.btn_send.setIconSize(QSize(60, 60))
        self.btn_send.setAutoDefault(False)
        self.textEdit = SendTextEdit(Form)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(18, 760, 309, 60))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy1)
        self.textEdit.setMinimumSize(QSize(309, 60))
        self.textEdit.setMaximumSize(QSize(309, 60))
        self.textEdit.setStyleSheet(u"\n"
"border-image: url(:/input/img_input.png) 10 10 10 10 stretch stretch;\n"
"        border-width: 10px;\n"
"        padding: 5px;")
        self.listView = CustomListView(Form)
        self.listView.setObjectName(u"listView")
        self.listView.setGeometry(QRect(17, 9, 440, 741))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy2)
        self.listView.setMinimumSize(QSize(440, 741))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_plus.setText("")
#if QT_CONFIG(shortcut)
        self.btn_plus.setShortcut(QCoreApplication.translate("Form", u"Enter", None))
#endif // QT_CONFIG(shortcut)
        self.btn_send.setText("")
        self.textEdit.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
    # retranslateUi

