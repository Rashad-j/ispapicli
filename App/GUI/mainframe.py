
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainFrame(QDialog):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        self.createTopGroupBox()
        self.createLeftGroupBox()
        self.createMiddleTabWidget()
        self.createRightGroupBox()
        self.createProgressBar()
        self.createMenubar()

        mainLayout = QGridLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addLayout(self.topLayout, 0, 0, 1, 3)
        mainLayout.addWidget(self.leftGroupBox, 1, 0)
        mainLayout.addWidget(self.middleGroupBox, 1, 1)
        mainLayout.addWidget(self.rightGroupBox, 1, 2)
        mainLayout.addWidget(self.progressBar, 2, 0, 1, 3)
        mainLayout.setRowStretch(1, 1)
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

    def createMenubar(self):

        self.menuBar = QMenuBar()
        file = self.menuBar.addMenu("File")
        file.addAction("New")
        save = QAction("Save", self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        quit = QAction("Quit", self)
        file.addAction(quit)

        edit = self.menuBar.addMenu("Edit")
        edit.addAction("copy")
        edit.addAction("paste")

        help = self.menuBar.addMenu("Help")
        help.addAction("How to?")
        help.addAction("About ISPAPI tool")

        file.triggered[QAction].connect(self.processtrigger)

    def processtrigger(self, q):
        print(q.text()+" is triggered")

    def close_application(self):
        print("exiting")
        sys.exit()

    def createTopGroupBox(self):
        executeBtn = QPushButton("Execute")
        clearBtn = QPushButton("Clear")
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
        gridLayout.setContentsMargins(0, 20, 0, 20)
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

        formLayout = QFormLayout()
        formLayout.addRow(self.tr("ID:"), userIDTxt)
        formLayout.addRow(self.tr("Pwd:"), passTxt)

        layout = QGridLayout()
        layout.addLayout(formLayout, 0, 0)

        self.rightGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = MainFrame()
    gallery.show()
    sys.exit(app.exec_())
