
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from modules.core import Core
from gui.login import LoginWindow
import textwrap
import sys


class MainFrame(QWidget):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        # intialize the gui
        self.originalPalette = QApplication.palette()
        self.createTopGroupBox()
        self.createLeftGroupBox()
        self.createMiddleTabWidget()
        self.createProgressBar()
        self.createMenubar()
        self.createToolbar()

        # set gui layout
        mainLayout = QGridLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.toolbar, 0, 0, 1, 3)
        mainLayout.addWidget(self.topBox, 1, 0, 1, 3)
        mainLayout.addWidget(self.leftGroupBox, 2, 0)
        mainLayout.addWidget(self.middleGroupBox, 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 3)
        mainLayout.setRowStretch(2, 2)
        mainLayout.setColumnStretch(0, 2)
        mainLayout.setColumnStretch(1, 4)
        self.setLayout(mainLayout)
        self.setWindowTitle("ISPAPI-CLI Tool")

        # set app gui style
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        # create core login instnace
        self.coreLogic = Core()

        # check user session upon start
        self.checkLogin()

        # set focus on command input field
        self.cmdTxt.setFocus()

    def checkLogin(self):
        result = self.coreLogic.checkSession()
        if result == 'valid':
            self.sessionTime.setText("You session is valid. ")
            self.sessionTime.setStyleSheet("color:green")
            self.loginBtn.setIcon(QIcon("icons/logout.png"))
            self.loginBtn.setText('Logout')
            self.loginBtn.clicked.connect(self.logout)
            self.reconnectBtnAction(self.loginBtn.clicked, self.logout)
            # enable gui
            self.disableEnableGui('enable')

        else:
            self.sessionTime.setText("Session expired! ")
            self.sessionTime.setStyleSheet("color:red")
            self.loginBtn.setIcon(QIcon("icons/login.png"))
            self.loginBtn.setText('Login')
            self.reconnectBtnAction(
                self.loginBtn.clicked, self.openLoginWindow)
            # diable gui
            self.disableEnableGui('disable')

    def reconnectBtnAction(self, signal, newhandler=None, oldhandler=None):
        """
        Reconnecting login btn action to either login or logout
        """
        while True:
            try:
                if oldhandler is not None:
                    signal.disconnect(oldhandler)
                else:
                    signal.disconnect()
            except TypeError:
                break
        if newhandler is not None:
            signal.connect(newhandler)

    def logout(self):
        result, msg = self.coreLogic.logout()
        alert = QMessageBox()
        alert.setText(msg)
        alert.exec_()
        # update login
        self.checkLogin()

    def disableEnableGui(self, status=None):
        """
        If session is expired then disable gui
        """
        if status is not None:
            if status == 'enable':
                self.leftGroupBox.setEnabled(True)
                self.topBox.setEnabled(True)
                # focus on command input field
                self.cmdTxt.setFocus()
            else:
                self.leftGroupBox.setDisabled(True)
                self.topBox.setDisabled(True)
        else:
            pass

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        if curVal <= 99:
            self.progressBar.setValue(curVal + 1)
        else:
            self.timer.stop()
            self.progressBar.setValue(0)

    def createProgressBar(self, ):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setTextVisible(False)

        # call timer
        self.progressBarSpeed(5)

    def progressBarSpeed(self, speed):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advanceProgressBar)
        self.timer.start(speed)

    def onMyToolBarButtonClick(self, s):
        print("click", s)

    def executeCommand(self):
        # start progressbar
        self.progressBarSpeed(20)
        args = (self.cmdTxt.text()).split()
        cmdView = (self.commandText.toPlainText()).split()
        core_obj = Core()
        parser, splitted_args = core_obj.initParser(args)
        print(splitted_args)
        # overwrite defualt error function with our local function
        parser.error = self.errorFunction
        try:
            args = vars(parser.parse_args(splitted_args))
            reminderargs = args['args']
            # parse command args
            result, data = core_obj.parseArgs(args, reminderargs)
            # case gui started
            if result == 'gui':
                self.plainResponse.setText("GUI already started")
            # case of help command
            elif result == 'help':
                preHelp = textwrap.dedent('''\
                    ISPAPI - Commandline Tool
                    ------------------------------------------------------------
                    The tool can be used in two modes:
                    - By using '=' sign e.g. --command=QueryDomainList limit=5
                    - By using spaces e.g. --command QueryDomainList limit 5
                    ------------------------------------------------------------

                    ''')
                helpText = 'preHelp + parser.print_help()'
                parser.print_help()
                self.plainResponse.setText(sys.stdout)
            # show specific command help
            elif result == 'help_command':
                if type(data) == str:
                    self.plainResponse.setText(data)
                else:
                    infoText = '\nCommand info: \n'
                    infoText += data[0] + '\n'
                    infoText += data[1] + '\n'
                    self.plainResponse.setText(infoText)
            # other messages related to login and server side errors
            elif result == 'msg':
                self.plainResponse.setText(data)
            # case result return that command is ready to execute
            elif result == 'cmd':
                response = core_obj.request(data)
                result = core_obj.getResponse(response)
                self.plainResponse.setText(result)
            # case list of command
            elif result == 'list':
                self.plainResponse.setText(data)
            # case logout
            elif result == 'logout':
                status, msg = data
                self.plainResponse.setText(msg)
            # case unknown response or command
            else:
                self.plainResponse.setText("Unknown results")

            # end the progress bar
            self.progressBarSpeed(5)

        except Exception as e:
            self.plainResponse.setText("Command failed due to: " + str(e))

    def errorFunction(self, message):
        self.plainResponse.setText('An error happend: ' + message + '\n')

    def updateCommandView(self):
        self.commandText.setText(self.cmdTxt.text())

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
        self.topBox = QGroupBox((""))
        executeBtn = QPushButton("Execute")
        executeBtn.setIcon(QIcon("icons/execute.png"))
        executeBtn.clicked.connect(self.executeCommand)
        executeBtn.setIconSize(QSize(14, 14))
        executeBtn.setLayoutDirection(Qt.RightToLeft)

        clearBtn = QPushButton("Clear")
        clearBtn.setIcon(QIcon("icons/cross.png"))
        clearBtn.setIconSize(QSize(14, 14))
        clearBtn.setLayoutDirection(Qt.RightToLeft)

        self.cmdTxt = QLineEdit()
        self.cmdTxt.setPlaceholderText("Enter command here...")
        self.cmdTxt.textEdited.connect(self.updateCommandView)
        self.cmdTxt.returnPressed.connect(self.executeCommand)
        nameLabel = QLabel(self)
        nameLabel.setText('Command:')

        gridLayout = QGridLayout()
        #gridLayout.addWidget(nameLabel,  0, 0, 1, 1)
        gridLayout.addWidget(self.cmdTxt,     0, 1, 1, 1)
        gridLayout.addWidget(executeBtn, 0, 2, 1, 1)
        gridLayout.addWidget(clearBtn,   0, 3, 1, 1)
        gridLayout.setContentsMargins(5, 0, 5, 10)
        self.topLayout = gridLayout
        self.topBox.setLayout(gridLayout)

    def createLeftGroupBox(self):
        self.leftGroupBox = QGroupBox("Command extracted")
        self.commandText = QTextEdit()
        self.commandText.setPlaceholderText(
            "Or enter command here line by line")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(self.commandText)

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
        self.plainResponse = QTextEdit()

        self.plainResponse.setPlainText("Twinkle, twinkle, little star,\n"
                                        "How I wonder what you are.\n"
                                        "Up above the world so high,\n"
                                        "Like a diamond in the sky.\n"
                                        "Twinkle, twinkle, little star,\n"
                                        "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(self.plainResponse)
        tab2.setLayout(tab2hbox)
        middleTabWidget.addTab(tab2, "Plain")
        middleTabWidget.addTab(tab1, "Table")

        layout = QGridLayout()
        layout.addWidget(middleTabWidget, 0, 0, 1, 1)

        self.middleGroupBox.setLayout(layout)

    def openLoginWindow(self):
        """
        Start login window
        """
        loginGui = LoginWindow(self)
        loginGui.startGui()

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
