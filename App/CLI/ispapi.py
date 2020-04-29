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
        parsed_params = core_obj.parseArgs(args, reminderargs)
        if type(parsed_params) == str:
            if parsed_params == 'gui':
                startGUI()
            elif parsed_params == 'help':
                parser.print_help()
            else:
                print(parsed_params)
        else:
            response = core_obj.request(parsed_params)
            print(response.getPlain())

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
