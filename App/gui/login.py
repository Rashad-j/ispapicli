from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QLabel, QStyleFactory, QGroupBox, QPushButton, QFormLayout, QDesktopWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QMovie
from modules.core import Core
import time
import threading


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        self.createRightGroupBox()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.rightGroupBox, 0, 0)
        self.setLayout(mainLayout)
        self.setWindowTitle("Login Window")
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Login Info:")

        loginBox = QGridLayout()
        self.userIDTxt = QLineEdit()
        self.passTxt = QLineEdit()
        self.passTxt.setEchoMode(QLineEdit.Password)
        self.sysChoice = QComboBox()
        self.sysChoice.addItems(['ote', 'live'])
        self.loginMsg = QLabel("")
        self.loginMsg.setAlignment(Qt.AlignCenter)

        self.loginBtn = QPushButton("Login")
        self.loginBtn.clicked.connect(self.login)

        formLayout = QFormLayout()
        formLayout.addRow(self.tr("Your ID:"), self.userIDTxt)
        formLayout.addRow(self.tr("Password:"), self.passTxt)
        formLayout.addRow(self.tr("System:"), self.sysChoice)
        formLayout.addRow(self.tr(""), self.loginBtn)
        formLayout.addRow(self.tr(""), self.loginMsg)
        layout = QGridLayout()
        layout.addLayout(formLayout, 0, 0)

        self.rightGroupBox.setLayout(layout)

    def login(self):
        myMovie = QMovie("icons/loading.gif")
        myMovie.setScaledSize(QSize(18, 18))
        # self.loginBtn.setIcon(QIcon(myMovie.currentPixmap()))
        #self.loginBtn.setIconSize(QSize(14, 14))
        # self.loginBtn.setLayoutDirection(Qt.RightToLeft)
        self.loginMsg.setMovie(myMovie)
        myMovie.start()

        coreLogic = Core()
        args = {}
        args['userid'] = self.userIDTxt.text()
        args['password'] = self.passTxt.text()
        args['entity'] = self.sysChoice.currentText()

        result, msg = coreLogic.login(args)
        if result == True:
            alert = QMessageBox()
            alert.setText('You have successfully logged in!')
            alert.exec_()

            # update parent window = login and session message
            self.parent().checkLogin()

            # close window
            self.close()
        else:
            self.loginMsg.setMovie(None)
            self.loginMsg.setText(msg)
            self.loginMsg.setStyleSheet("color:red")

    def startGui(self):

        geo = QDesktopWidget().availableGeometry()
        screenWidth = geo.width()
        screenHeight = geo.height()
        width = int(screenWidth * 0.2)
        height = int(screenHeight * 0.2)
        self.resize(width, height)

        frameGeo = self.frameGeometry()
        cp = geo.center()
        frameGeo.moveCenter(cp)
        self.move(frameGeo.topLeft())

        self.show()
