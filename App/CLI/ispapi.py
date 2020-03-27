#!/usr/bin/python

import os
import sys
import argparse
from Modules.core import Core
from hexonet.apiconnector.response import Response


def main(args):
    # initialise our main logic class
    core = Core()
    n_args = len(args)
    # get parsed args
    parsedArgs = core.parseArgs(args, n_args)

    #
    if type(parsedArgs) is str:
        if(parsedArgs == 'start_gui'):
            print('start gui')
        else:  # case of show version
            print('show version')

    elif type(parsedArgs) is list:
        # case a command requested
        print(parsedArgs)
        if core.login():
            response = core.request()
            if type(response) is Response:
                core.getResponse(response, 'list')
            else:
                # print returned description
                print(response)
        else:
            print('Login Failed')
    else:
        print('Bad Command')


def start_gui():
    print("Gui Started")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[0:])

    # parser = argparse.ArgumentParser(
    #    description="Our CLI Tool"
    # )

    # add parameters positional/optional
    # parser.add_argument('arg1', help="this is argument 1", type=str)
    # parser.add_argument('arg2', nargs="?", default="2",help = "this is argument 1", type = str)
    # parse the arguments
    # args = parser.parse_args()
    # print(args)
