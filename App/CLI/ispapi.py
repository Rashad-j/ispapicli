#!/usr/bin/python

import os
import sys
import argparse
from hexonet.apiconnector.response import Response
from pathlib import Path
from modules.core import Core
import textwrap


def main(args):

    core_obj = Core()
    parser, splitted_args = core_obj.initParser(args)
    # overwrite defualt error function with out local fuction
    parser.error = errorFunction
    args = vars(parser.parse_args(splitted_args))
    reminderargs = args['args']
    try:
        result, data = core_obj.parseArgs(args, reminderargs)
        if result == 'logout':
            print('Logged out successfully!')
        if result == 'gui':
            startGUI()
        if result == 'help':
            parser.print_help()
        if result == 'help_command':
            print('\nCommand info: \n')
            print(data[0])
            print(data[1])
        if result == 'msg':
            print(data)
        if result == 'cmd':
            response = core_obj.request(data)
            print(response.getPlain())
        sys.exit(0)

    except Exception as e:
        print("Command failed due to: " + str(e))


def startGUI():
    print("Gui Started")
    sys.exit(0)


def errorFunction(message):
    print('\nAn error happend: ' + message + '\n')
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
