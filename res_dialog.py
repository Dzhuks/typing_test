# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'res_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(489, 300)
        Dialog.setStyleSheet("background-color: rgb(56, 56, 56);")
        self.button_box = QtWidgets.QDialogButtonBox(Dialog)
        self.button_box.setGeometry(QtCore.QRect(40, 240, 411, 51))
        self.button_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.button_box.setStyleSheet("color: rgb(240, 223, 28);\n"
"")
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setCenterButtons(True)
        self.button_box.setObjectName("button_box")
        self.image_label = QtWidgets.QLabel(Dialog)
        self.image_label.setGeometry(QtCore.QRect(30, 20, 191, 191))
        self.image_label.setText("")
        self.image_label.setObjectName("image_label")
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(230, 20, 241, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.comment_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.comment_label.setFont(font)
        self.comment_label.setStyleSheet("color: rgb(240, 223, 28);\n"
"")
        self.comment_label.setObjectName("comment_label")
        self.verticalLayout.addWidget(self.comment_label)
        self.cpm_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.cpm_label.setFont(font)
        self.cpm_label.setStyleSheet("color: rgb(240, 223, 28);\n"
"")
        self.cpm_label.setObjectName("cpm_label")
        self.verticalLayout.addWidget(self.cpm_label)
        self.time_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.time_label.setFont(font)
        self.time_label.setStyleSheet("color: rgb(240, 223, 28);\n"
"")
        self.time_label.setObjectName("time_label")
        self.verticalLayout.addWidget(self.time_label)

        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.comment_label.setText(_translate("Dialog", "Отличный результат!"))
        self.cpm_label.setText(_translate("Dialog", "Символов в минуту: 250"))
        self.time_label.setText(_translate("Dialog", "Общее время:1:20"))
