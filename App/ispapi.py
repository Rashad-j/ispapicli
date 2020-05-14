#!/usr/bin/python

import os
import sys
import argparse
from hexonet.apiconnector.response import Response
from pathlib import Path
from modules.core import Core
from gui.mainframe import MainFrame
import textwrap
from PyQt5.QtWidgets import QApplication


def main(args):

    core_obj = Core()
    parser, splitted_args = core_obj.initParser(args)
    # overwrite defualt error function with our local function
    parser.error = errorFunction
    args = vars(parser.parse_args(splitted_args))
    reminderargs = args['args']
    try:
        result, data = core_obj.parseArgs(args, reminderargs)
        if result == 'gui':
            startGUI()
        if result == 'help':
            print('\n')
            print(textwrap.dedent('''\
                ISPAPI - Commandline Tool
                ------------------------------------------------------------
                The tool can be used in two modes:
                 - By using '=' sign e.g. --command=QueryDomainList limit=5
                 - By using spaces e.g. --command QueryDomainList limit 5
                ------------------------------------------------------------

                '''))
            parser.print_help()
        if result == 'help_command':
            if type(data) == str:
                print(data)
            else:
                print('\nCommand info: \n')
                print(data[0])
                print(data[1])
        if result == 'msg':
            print(data)
        if result == 'cmd':
            response = core_obj.request(data)
            result = core_obj.getResponse(response)
            print(result)
        if result == 'list':
            print((data))
        sys.exit(0)

    except Exception as e:
        print("Command failed due to: " + str(e))


def startGUI():
    app = QApplication(sys.argv)
    appGui = MainFrame()
    appGui.startGui()
    sys.exit(app.exec_())


def errorFunction(message):
    print('\nAn error happend: ' + message + '\n')
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
