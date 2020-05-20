
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from modules.core import Core
from gui.login import LoginWindow


class MainFrame(QWidget):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        self.createTopGroupBox()
        self.createLeftGroupBox()
        self.createMiddleTabWidget()
        self.createProgressBar()
        self.createMenubar()
        self.createToolbar()

        mainLayout = QGridLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.toolbar, 0, 0, 1, 3)
        mainLayout.addLayout(self.topLayout, 1, 0, 1, 3)
        mainLayout.addWidget(self.leftGroupBox, 2, 0)
        mainLayout.addWidget(self.middleGroupBox, 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 3)
        mainLayout.setRowStretch(2, 2)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 3)
        self.setLayout(mainLayout)
        self.setWindowTitle("ISPAPI-CLI Tool")

        # set app gui style
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        # check user session upon start
        self.checkLogin()

    def checkLogin(self):
        coreLogic = Core()
        result = coreLogic.checkSession()
        if result == 'valid':
            self.sessionTime.setText("You session is valid. ")
            self.sessionTime.setStyleSheet("color:green")
            self.loginBtn.setIcon(QIcon("icons/logout.png"))
            self.loginBtn.setText('Logout')
            self.loginBtn.clicked.connect(self.logout)

        else:
            self.sessionTime.setText("Session expired! ")
            self.sessionTime.setStyleSheet("color:red")
            self.loginBtn.setIcon(QIcon("icons/login.png"))
            self.loginBtn.setText('Login')
            self.loginBtn.clicked.connect(self.openLoginWindow)
        # in bothcases check if the gui disabled or enabled
        self.disableEnableGui()

    def logout(self):
        print('called logout')
        coreLogic = Core()
        result, msg = coreLogic.logout()
        # check if logout success
        alert = QMessageBox()
        alert.setText(msg)
        alert.exec_()

    def disableEnableGui(self, status=''):
        # todo
        pass

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)

    def onMyToolBarButtonClick(self, s):
        print("click", s)

    def createToolbar(self):
        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(20, 20))
        saveAction = QAction(
            QIcon("icons/save.png"), "Save results to JSON file", self)
        saveAction.triggered.connect(self.onMyToolBarButtonClick)

        copyAction = QAction(
            QIcon("icons/copy.png"), "Copy the results to clipboard", self)
        copyAction.triggered.connect(self.onMyToolBarButtonClick)

        helpAction = QAction(
            QIcon("icons/help.png"), "See help documentation", self)
        helpAction.triggered.connect(self.onMyToolBarButtonClick)

        openAction = QAction(
            QIcon("icons/new.png"), "Open another window", self)
        openAction.triggered.connect(self.onMyToolBarButtonClick)

        self.sessionTime = QLabel("Checking your session... ")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.loginBtn = QPushButton("Login")
        self.loginBtn.setIcon(QIcon("icons/login.png"))
        self.loginBtn.setStyleSheet(
            "padding: 2px; padding-left: 6px")
        self.loginBtn.setIconSize(QSize(12, 12))
        self.loginBtn.setLayoutDirection(Qt.RightToLeft)

        seperator = QAction(self)
        seperator.setSeparator(True)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addAction(copyAction)
        self.toolbar.addAction(seperator)
        self.toolbar.addAction(helpAction)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.sessionTime)
        self.toolbar.addWidget(self.loginBtn)

    def createMenubar(self):

        self.menuBar = QMenuBar()
        file = self.menuBar.addMenu("File")
        new = QAction("New window", self)
        new.setShortcut("Ctrl+n")
        save = QAction("Save to file", self)
        save.setShortcut("Ctrl+S")
        quit = QAction("Quit", self)
        quit.setShortcut("Ctrl+q")

        file.addAction(new)
        file.addAction(save)
        file.addAction(quit)

        edit = self.menuBar.addMenu("Edit")
        copy = QAction("Copy", self)
        copy.setShortcut("Ctrl+c")

        edit.addAction(copy)

        help = self.menuBar.addMenu("Help")
        help.addAction("How to?")
        help.addAction("About ISPAPI tool")

        file.triggered[QAction].connect(self.processTrigger)

    def createTopGroupBox(self):
        executeBtn = QPushButton("Execute")
        executeBtn.setIcon(QIcon("icons/execute.png"))
        executeBtn.setIconSize(QSize(14, 14))
        executeBtn.setLayoutDirection(Qt.RightToLeft)

        clearBtn = QPushButton("Clear")
        clearBtn.setIcon(QIcon("icons/cross.png"))
        clearBtn.setIconSize(QSize(14, 14))
        clearBtn.setLayoutDirection(Qt.RightToLeft)

        cmdTxt = QLineEdit()
        cmdTxt.setPlaceholderText("Enter command here...")
        nameLabel = QLabel(self)
        nameLabel.setText('Command:')

        gridLayout = QGridLayout()
        gridLayout.addWidget(nameLabel,  0, 0, 1, 1)
        gridLayout.addWidget(cmdTxt,     0, 1, 1, 1)
        gridLayout.addWidget(executeBtn, 0, 2, 1, 1)
        gridLayout.addWidget(clearBtn,   0, 3, 1, 1)
        gridLayout.setRowStretch(1, 1)
        gridLayout.setContentsMargins(0, 5, 0, 10)
        self.topLayout = gridLayout

    def createLeftGroupBox(self):
        self.leftGroupBox = QGroupBox("Command extracted")

        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n"
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n"
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)

        self.leftGroupBox.setLayout(tab2hbox)

    def createMiddleTabWidget(self):
        self.middleGroupBox = QGroupBox("Results")
        middleTabWidget = QTabWidget()
        middleTabWidget.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n"
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n"
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)
        middleTabWidget.addTab(tab1, "Table")
        middleTabWidget.addTab(tab2, "Plain")

        layout = QGridLayout()
        layout.addWidget(middleTabWidget, 0, 0, 1, 1)

        self.middleGroupBox.setLayout(layout)

    def openLoginWindow(self):
        print('called login')
        loginGui = LoginWindow(self)
        loginGui.startGui()

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setTextVisible(False)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

    def processTrigger(self, q):
        print(q.text()+" is triggered")

    def closeApplication(self):
        print("exiting")
        sys.exit()

    def startGui(self):
        geo = QDesktopWidget().availableGeometry()

        screenWidth = geo.width()
        screenHeight = geo.height()
        width = int(screenWidth * 0.5)
        height = int(screenHeight * 0.5)
        self.resize(width, height)

        frameGeo = self.frameGeometry()
        cp = geo.center()
        frameGeo.moveCenter(cp)
        self.move(frameGeo.topLeft())

        # start gui
        self.show()
