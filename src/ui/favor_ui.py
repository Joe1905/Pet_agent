# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'favor.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QLineEdit,
    QProgressBar, QPushButton, QSizePolicy, QWidget)
import ui.resource_rc

class Ui_mainWidget(object):
    def setupUi(self, mainWidget):
        if not mainWidget.objectName():
            mainWidget.setObjectName(u"mainWidget")
        mainWidget.resize(397, 110)
        self.image_head = QLabel(mainWidget)
        self.image_head.setObjectName(u"image_head")
        self.image_head.setGeometry(QRect(9, 22, 65, 65))
        self.image_head.setMinimumSize(QSize(65, 65))
        self.image_head.setMaximumSize(QSize(65, 65))
        self.pushButton = QPushButton(mainWidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(300, 10, 50, 24))
        self.pushButton.setMaximumSize(QSize(50, 16777215))
        self.image_favor = QLabel(mainWidget)
        self.image_favor.setObjectName(u"image_favor")
        self.image_favor.setGeometry(QRect(82, 43, 35, 35))
        self.image_favor.setMinimumSize(QSize(35, 35))
        self.image_favor.setMaximumSize(QSize(35, 35))
        self.image_favor.setStyleSheet(u"")
        self.progressBar = QProgressBar(mainWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(123, 49, 251, 23))
        self.progressBar.setStyleSheet(u"")
        self.progressBar.setValue(24)
        self.lineEdit = QLineEdit(mainWidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(182, 13, 100, 20))
        self.lineEdit.setMinimumSize(QSize(0, 20))
        self.lineEdit.setMaximumSize(QSize(100, 20))
        self.btn_choice = QCheckBox(mainWidget)
        self.btn_choice.setObjectName(u"btn_choice")
        self.btn_choice.setGeometry(QRect(89, 13, 47, 20))
        self.btn_choice.setMaximumSize(QSize(80, 16777215))
        self.btn_choice.setChecked(False)

        self.retranslateUi(mainWidget)

        QMetaObject.connectSlotsByName(mainWidget)
    # setupUi

    def retranslateUi(self, mainWidget):
        mainWidget.setWindowTitle(QCoreApplication.translate("mainWidget", u"Form", None))
        self.image_head.setText("")
        self.pushButton.setText(QCoreApplication.translate("mainWidget", u"\u4fee\u6539", None))
        self.image_favor.setText("")
        self.progressBar.setFormat(QCoreApplication.translate("mainWidget", u"%p", None))
        self.btn_choice.setText(QCoreApplication.translate("mainWidget", u"\u9009\u62e9", None))
    # retranslateUi

