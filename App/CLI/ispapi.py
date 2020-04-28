#!/usr/bin/python

import os
import sys
import argparse
# from Modules.core import Core
from hexonet.apiconnector.response import Response


def main(args):
    # initialise our main logic class
    core = Core()
    n_args = len(args)
    # get parsed args
    parsedArgs = core.parseArgs(args, n_args)

    #
    if type(parsedArgs) is str:
        if parsedArgs == 'start_gui':
            startGUI()
        elif parsedArgs == 'show_help':
            print(showHelp())
        else:  # case of show version
            print(showVersion())

    elif type(parsedArgs) is list:
        # case a command requested
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


def startGUI():
    print("Gui Started")
    sys.exit(0)


def showHelp():
    return """
    
        ISPAPI - Commandline Tool
        Version: v 2.0.1 

        usage: ispapi [arguments] [command] [Properties]
        
        Arguments:
        
        --help    | -h    ..................... Open the help
        --version | -v    ..................... Returns the software version
        --gui     | empty    .................. Open the graphical user interface
        --password=<password>    .............. Choose your password
        --login=<login>     ................... Choose your login
        --entity=<entity> ..................... Choose your entity (1234: OTE, 54cd: LIVE)

        
        Commands:
        
        CheckDomain <domain>    ............ Check the availability of the domain
        StatusDomain <domain>    ........... Returns the current status of the domain with a lot of informations
        QueryDomainList    ................. Returns a list of all your domains
        ...
        
        Properties:
        
        limit = <number> ................... Set limit of returned results
        orderby = <text> ................... Order returned results, e.g. orderby = DOMAIN
        * = *  ............................. Any other option of your choice 
        ...
        
        All API Commands are detailed at: https://wiki.hexonet.net

    """


def showVersion():
    return 'v 2.0.1'


if __name__ == "__main__":
    # main(sys.argv[0:])
    print(' '.join(sys.argv[1:]))
    # parser = argparse.ArgumentParser(
    #    description="Our CLI Tool"
    # )

    # add parameters positional/optional
    # parser.add_argument('arg1', help="this is argument 1", type=str)
    # parser.add_argument('arg2', nargs="?", default="2",help = "this is argument 1", type = str)
    # parse the arguments
    # args = parser.parse_args()
    # print(args)
