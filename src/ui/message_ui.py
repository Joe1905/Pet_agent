# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'message.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QTextBrowser,
    QWidget)
import ui.resource_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(410, 188)
        self.text_info = QTextBrowser(Form)
        self.text_info.setObjectName(u"text_info")
        self.text_info.setGeometry(QRect(20, 65, 280, 110))
        self.text_info.setStyleSheet(u"background-color: transparent;\n"
"        border: none; /* \u53ef\u9009\uff1a\u53bb\u6389\u8fb9\u6846 */")
        self.image_text = QWidget(Form)
        self.image_text.setObjectName(u"image_text")
        self.image_text.setGeometry(QRect(10, 50, 320, 131))
        self.image_text.setStyleSheet(u" border-image:  url(:/input/img_bubble.png) 50 50 50 50 stretch stretch;  \n"
"    border-width: 50;")
        self.text_time = QLabel(Form)
        self.text_time.setObjectName(u"text_time")
        self.text_time.setGeometry(QRect(160, 20, 41, 21))
        self.text_time.setStyleSheet(u" border-image:  url(:/input/bg.png) 5 5 5 5 stretch stretch;  \n"
"text-align: center;")
        self.text_time.setAlignment(Qt.AlignCenter)
        self.image_head = QLabel(Form)
        self.image_head.setObjectName(u"image_head")
        self.image_head.setGeometry(QRect(330, 50, 80, 80))
        self.thinking = QLabel(Form)
        self.thinking.setObjectName(u"thinking")
        self.thinking.setGeometry(QRect(130, 60, 60, 60))
        self.thinking.setMinimumSize(QSize(60, 60))
        self.thinking.setMaximumSize(QSize(60, 60))
        self.thinking_text = QLabel(Form)
        self.thinking_text.setObjectName(u"thinking_text")
        self.thinking_text.setGeometry(QRect(190, 60, 60, 60))
        self.thinking_text.setMinimumSize(QSize(60, 60))
        self.thinking_text.setMaximumSize(QSize(60, 60))
        font = QFont()
        font.setPointSize(15)
        self.thinking_text.setFont(font)
        self.image_text.raise_()
        self.text_info.raise_()
        self.text_time.raise_()
        self.image_head.raise_()
        self.thinking.raise_()
        self.thinking_text.raise_()

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.text_info.setMarkdown(QCoreApplication.translate("Form", u"\u4f60\u597d\n"
"\n"
"", None))
        self.text_info.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt;\">\u4f60\u597d</span></p></body></html>", None))
        self.text_time.setText(QCoreApplication.translate("Form", u"10:30", None))
        self.image_head.setText("")
        self.thinking.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.thinking_text.setText(QCoreApplication.translate("Form", u"\u601d\u8003\u4e2d", None))
    # retranslateUi

