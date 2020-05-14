
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from modules.core import Core


class MainFrame(QWidget):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        self.createTopGroupBox()
        self.createLeftGroupBox()
        self.createMiddleTabWidget()
        self.createRightGroupBox()
        self.createProgressBar()
        self.createMenubar()
        self.createToolbar()

        mainLayout = QGridLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.toolbar, 0, 0, 1, 3)
        mainLayout.addLayout(self.topLayout, 1, 0, 1, 3)
        mainLayout.addWidget(self.leftGroupBox, 2, 0)
        mainLayout.addWidget(self.middleGroupBox, 2, 1)
        mainLayout.addWidget(self.rightGroupBox, 2, 2)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 3)
        mainLayout.setRowStretch(2, 2)
        mainLayout.setColumnStretch(0, 2)
        mainLayout.setColumnStretch(1, 3)
        mainLayout.setColumnStretch(2, 2)
        self.setLayout(mainLayout)
        self.setWindowTitle("ISPAPI-CLI Tool")
        self.changeStyle('Fusion')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        # self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

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

        sessionTime = QLabel("Session time: 00:00:00")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        seperator = QAction(self)
        seperator.setSeparator(True)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addAction(copyAction)
        self.toolbar.addAction(seperator)
        self.toolbar.addAction(helpAction)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(sessionTime)

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

        file.triggered[QAction].connect(self.processtrigger)

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

    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Quick access")

        loginBox = QGridLayout()
        userIDTxt = QLineEdit()
        passTxt = QLineEdit()
        passTxt.setEchoMode(QLineEdit.Password)
        sysChoice = QComboBox()
        sysChoice.addItems(['live', 'ote'])
        loginMsg = QLabel("Your session expired!")
        loginMsg.setAlignment(Qt.AlignCenter)

        loginBtn = QPushButton("Login")
        loginBtn.clicked.connect(self.login)
        loginBtn.setIcon(QIcon("icons/login.png"))
        loginBtn.setIconSize(QSize(14, 14))
        loginBtn.setLayoutDirection(Qt.RightToLeft)

        formLayout = QFormLayout()
        formLayout.addRow(self.tr("Your ID:"), userIDTxt)
        formLayout.addRow(self.tr("Password:"), passTxt)
        formLayout.addRow(self.tr("System:"), sysChoice)
        formLayout.addRow(self.tr(""), loginBtn)
        formLayout.addRow(self.tr("Status:"), loginMsg)
        layout = QGridLayout()
        layout.addLayout(formLayout, 0, 0)

        self.rightGroupBox.setLayout(layout)

    def login(self):
        print("ok")

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setTextVisible(False)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

    def processtrigger(self, q):
        print(q.text()+" is triggered")

    def close_application(self):
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

        self.show()
