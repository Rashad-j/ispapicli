#!/usr/bin/python

import os
import sys
import argparse
from hexonet.apiconnector.response import Response
from pathlib import Path
from modules.core import Core
import textwrap


def main(args):
    parser = argparse.ArgumentParser(
        prog='ispapi',
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
                ISPAPI - Commandline Tool
            ---------------------------------------------
                You can use the tool in two different ways:
                One is by using '=' sign e.g. --command=QueryDomainList
                Or by using spaces e.g. --command QueryDomainList
            ----------------------------------------------

            '''),
        epilog=textwrap.dedent('''
            You can use the command '--define <command>' to know everything about a specific command
            You can also visit our documentation on https://github.com/hexonet/hexonet-api-documentation
        ''')
    )
    parser.add_argument('--command', '-c', metavar='<command>',
                        help='Enter a command e.g. -c=CheckDomain or -c CheckDomain')
    parser.add_argument('--entity', '-e', choices={'live', 'ote'},
                        help="set entity to either live or ote system e.g. -e=ote")
    parser.add_argument('--userid', '-u', metavar='<user id>',
                        help='Your login user ID')
    parser.add_argument('--password', '-p', metavar='<your password>',
                        help="Your login password")
    parser.add_argument('--gui', '-g', const='gui', nargs='?', metavar='',
                        help="Start graphical application")
    parser.add_argument('--help', '-h', const='all', nargs='?', metavar='<command>',
                        help="Show detailed use of a command")
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help='All additional args, e.g. limit=5')
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s 2.0')
    parser.error = errorFunction
    original_args = ' '.join(args)
    # remove spaces around the = cases ' =', '= ', ' = '
    original_args = original_args.replace(" = ", "=")
    original_args = original_args.replace(" =", "=")
    original_args = original_args.replace("= ", "=")
    splitted_args = original_args.split()
    args = vars(parser.parse_args(splitted_args))
    print(args)
    reminderargs = args['args']
    core_obj = Core()
    try:
        parsed_params = core_obj.parseArgs(args, reminderargs)
        if type(parsed_params) == str:
            if parsed_params == 'gui':
                startGUI()
            elif parsed_params == 'help':
                parser.print_help()
                pass
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
