
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from modules.core import Core
from gui.login import LoginWindow
import textwrap
import sys
from io import StringIO
from collections import defaultdict


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
        mainLayout.setColumnStretch(1, 6)
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

        # initilaize command line completer
        self.initialiseCommandCompleter()

    def checkLogin(self):
        result = self.coreLogic.checkSession()
        if result == 'valid':
            self.sessionTime.setText("Your session is valid. ")
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
        self.progressBar.setMaximumHeight(5)
        self.progressBar.setTextVisible(False)

        # create a timer for the progress bar

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advanceProgressBar)

        # call timer with speed of 5
        self.progressBarSpeed(5)

    def progressBarSpeed(self, speed):
        self.timer.start(speed)

    def onMyToolBarButtonClick(self, s):
        print("click", s)

    def executeCommand(self):
        # start progressbar
        self.progressBarSpeed(5)

        # get args from the GUI
        splitted_args = (self.commandText.toPlainText()).split()

        # intialize the parser
        core_obj = self.coreLogic
        parser = core_obj.initParser()
        # overwrite defualt error function with our local function to show on the GUI
        parser.error = self.errorFunction

        try:
            args = vars(parser.parse_args(splitted_args))
            reminderargs = args['args']
            # parse command args
            result, data = core_obj.parseArgs(args)
            # case gui started
            if result == 'gui':
                self.plainResponse.setText("GUI already started")
            # case of help command
            elif result == 'help':
                helpText = ''
                preHelp = textwrap.dedent('''\
                    ISPAPI - Commandline Tool
                    ------------------------------------------------------------
                    The tool can be used in two modes:
                    - By using '=' sign e.g. --command=QueryDomainList limit=5
                    - By using spaces e.g. --command QueryDomainList limit 5
                    ------------------------------------------------------------

                    ''')
                # redirect stdout
                stringio = StringIO()
                previous_stdout = sys.stdout
                sys.stdout = stringio

                # trigger parser help
                parser.print_help()

                # set back stdout
                sys.stdout = previous_stdout
                stdoutValue = stringio.getvalue()

                # show output on the GUI
                helpText = preHelp + stdoutValue
                self.plainResponse.setText(helpText)
            # show specific command help
            elif result == 'help_command':
                if type(data) == str:
                    self.plainResponse.setText(data)
                else:
                    infoText = 'Command info: \n'
                    infoText += data[0] + '\n'
                    infoText += data[1] + '\n'
                    self.plainResponse.setText(infoText)
            # other messages related to login and server side errors
            elif result == 'msg':
                self.plainResponse.setText(data)
            # case result return that command is ready to execute
            elif result == 'cmd':
                # append reminder args with the command
                params_list = core_obj.parseParameters(reminderargs)
                cmd = data
                # add them to data which is the command list
                cmd.update(params_list)
                response = core_obj.request(cmd)
                # set reult values to gui
                self.populateResults(response)

            # self.tableResponse.inser(propertiesResult)
            # case list of command
            elif result == 'list':
                self.plainResponse.setText(data)
            # case logout
            elif result == 'logout':
                status, msg = data
                self.plainResponse.setText(msg)
            # case unknown response or command
            else:
                self.plainResponse.setText(data)

            # 1 end the progress bar
            # self.progressBarSpeed(5)
            # 2
            # check user session, in case of sesssion is expired
            self.checkLogin()
        except Exception as e:
            self.plainResponse.setText("Command failed due to: " + str(e))

    def errorFunction(self, message):
        self.plainResponse.setText('An error happend: ' + message + '\n')

    def updateCommandView(self):
        cmdTxt = self.cmdTxt.text()
        # check if the command is related to other actions
        if cmdTxt.startswith('-', 0, 1) or cmdTxt.startswith('--', 0, 2):
            self.commandText.setText(cmdTxt)
            return 0
        else:
            args = '--command '
            args += self.cmdTxt.text()
            args = args.split()
            # show min paramters suggestions
            try:
                minParams = self.coreLogic.getMinParameters(self.cmdTxt.text())
                self.cmdTxt.setText(args[1] + ' ' + minParams[0] + '=')
                print(minParams)
            except:
                pass
            # clean extra spaces, leave only single spaces among commands
            original_args = ' '.join(args)
            # remove extra spaces around the = cases are ' =', '= ', ' = '
            original_args = original_args.replace(" = ", "=")
            original_args = original_args.replace(" =", "=")
            original_args = original_args.replace("= ", "=")
            # split args in an array
            parameters = original_args.split()
            # split commands if = used
            params_len = len(parameters)
            params = {}
            try:
                if params_len > 1:
                    i = 0
                    while i < params_len:
                        if '=' in parameters[i]:
                            key, value = parameters[i].split('=')
                            params[key] = value
                        else:
                            key = parameters[i]
                            i += 1
                            value = parameters[i]
                            params[key] = value
                        i += 1
                    self.commandText.setText()
            except Exception as e:
                pass
            commandView = "\n".join(("{}={}".format(*i)
                                     for i in params.items()))
            self.commandText.setText(commandView)

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
        clearBtn.clicked.connect(self.__clearCMDfield)

        self.cmdTxt = QLineEdit()
        self.cmdTxt.setPlaceholderText("Enter command here...")
        self.cmdTxt.textEdited.connect(self.updateCommandView)
        self.cmdTxt.returnPressed.connect(self.executeCommand)
        # set command completer
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.cmdTxt.setCompleter(self.completer)

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
        self.plainResponse = QTextEdit()
        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(self.plainResponse)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        self.tableResponse = QTableWidget(1, 2)
        self.tableResponse.setHorizontalHeaderLabels(['Property', 'Value'])
        self.tableResponse.horizontalHeader().setStretchLastSection(True)
        tableLayout = QGridLayout()
        tableLayout.setContentsMargins(5, 5, 5, 5)
        tableLayout.addWidget(self.tableResponse, 0, 0)
        tab2.setLayout(tableLayout)

        tab3 = QWidget()
        self.listResponse = QTextEdit()
        tab3hbox = QHBoxLayout()
        tab3hbox.addWidget(self.listResponse)
        tab3.setLayout(tab3hbox)

        middleTabWidget.addTab(tab1, "Plain")
        middleTabWidget.addTab(tab2, "Properties")
        middleTabWidget.addTab(tab3, 'List')

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

    def initialiseCommandCompleter(self):
        model = QStringListModel()
        # get all possible autocomplete strings
        stringsSuggestion = []
        stringsSuggestion = (self.coreLogic.getCommandList()).splitlines()
        # set suggestion to the model
        model.setStringList(stringsSuggestion)
        # set model to the completer
        self.completer.setModel(model)

    def __clearCMDfield(self):
        self.cmdTxt.clear()
        self.cmdTxt.setFocus(True)

    def populateResults(self, response):
        # get reulsts
        plainResult = response.getPlain()
        listResult = response.getListHash()

        # set plain results
        self.plainResponse.setText(plainResult)

        # set properties and list
        resultLists = listResult['LIST']
        counter = 0
        for row in resultLists:
            for col in row:
                counter += 1
        # set the number of rows
        self.tableResponse.setRowCount(counter)

        # populate the table
        rownumber = 0
        for row in resultLists:
            for i, (key, value) in enumerate(row.items()):
                keyWidget = QTableWidgetItem(key)
                valueWidget = QTableWidgetItem(value)
                self.tableResponse.setItem(rownumber, 0, keyWidget)
                self.tableResponse.setItem(rownumber, 1, valueWidget)
                # update the list
                if key not in ('TOTAL', 'FIRST', 'LAST', 'LIMIT', 'COUNT'):
                    self.listResponse.append(value)
                # incerate rownumber
                rownumber += 1
        # order table content
        self.tableResponse.sortItems(Qt.AscendingOrder)
