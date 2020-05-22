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
    try:
        # get command and its args
        args = vars(parser.parse_args(splitted_args))
        reminderargs = args['args']
        # parse command args
        result, data = core_obj.parseArgs(args, reminderargs)
        if result == 'gui':
            startGUI()
        elif result == 'help':
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
        elif result == 'help_command':
            if type(data) == str:
                print(data)
            else:
                print('\nCommand info: \n')
                print(data[0])
                print(data[1])
        elif result == 'msg':
            print(data)
        elif result == 'cmd':
            response = core_obj.request(data)
            result = core_obj.getResponse(response)
            print(result)
        elif result == 'list':
            print((data))

        elif result == 'logout':
            status, msg = data
            print(msg)

        else:
            print('unknown results')

        sys.exit(0)

    except Exception as e:
        print("Command failed due to: " + str(e))


def startGUI():
    app = QApplication(sys.argv)
    appGui = MainFrame()
    appGui.startGui()
    sys.exit(app.exec_())


def errorFunction(message):
    print('\nAn error occured: ' + message + '\n')
    sys.exit(0)


if __name__ == "__main__":

    argsLen = len(sys.argv)
    # if gui triggred
    # if argsLen == 0: # after finishing debugging mode
    if argsLen == 1:  # only in debugging mode
        startGUI()
    else:
        print(sys.argv)
        main(sys.argv[1:])
