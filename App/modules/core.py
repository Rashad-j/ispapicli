from hexonet.apiconnector.apiclient import APIClient as AC
from hexonet.apiconnector.response import Response
import re
import argparse
import textwrap
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import time
import os
from tabulate import tabulate
from textwrap import TextWrapper


class Core:
    def __init__(self):
        # create private config list
        self.cl = AC()
        self.command_path = Path(__file__).parent / "../commands/"
        self.session_path = Path(__file__).parent / "../config/session.json"

    def initParser(self, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.prog = 'ispapi'
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        #parser.description = textwrap.dedent()
        parser.epilog = textwrap.dedent('''
                ------------------------------------------------------------
                - You must login first to start requesting commands
                - You can use the command '--help <command>' to know everything about a specific command,
                - Or visit our documentation on: https://github.com/hexonet/hexonet-api-documentation
                ------------------------------------------------------------
            ''')
        parser.add_argument('args', nargs=argparse.REMAINDER,
                            help='All additional args, e.g. limit=5')
        parser.add_argument('--command', '-c', metavar='<command>',
                            help='Enter a command e.g. -c=CheckDomain or -c CheckDomain')
        parser.add_argument('--userid', '-u', metavar='<user id>',
                            help='Your login user ID')
        parser.add_argument('--password', '-p', metavar='<your password>',
                            help="Your login password")
        parser.add_argument('--entity', '-e', choices={'live', 'ote'},
                            help="Set entity to either live or ote system e.g. -e=ote")
        parser.add_argument('--gui', '-g', const='gui', nargs='?', metavar='<>',
                            help="Start graphical application")
        parser.add_argument('--help', '-h', const='all', nargs='?', metavar='<command>,<>',
                            help="Show detailed use of a 'command' OR use --help to show help")
        parser.add_argument('--list', '-li', const='list', nargs='?', metavar='<>',
                            help="List all commands' names")
        parser.add_argument('--logout', '-l', const='logout', nargs='?', metavar='<>',
                            help="Destroy your current session")
        parser.add_argument('--update', '-up', const='update', nargs='?', metavar='<>',
                            help="Update local command list")
        parser.add_argument('--version', '-v', action='version',
                            version='%(prog)s 2.0')
        # clean extra spaces, leave only single spaces among commands
        original_args = ' '.join(args)
        # remove extra spaces around the = cases are ' =', '= ', ' = '
        original_args = original_args.replace(" = ", "=")
        original_args = original_args.replace(" =", "=")
        original_args = original_args.replace("= ", "=")
        # split args in an array
        splitted_args = original_args.split()
        return parser, splitted_args

    def parseArgs(self, args, parameters):
        if args['logout'] is not None:
            result, msg = self.logout()
            return 'logout', {result, msg}
        if args['gui'] is not None:
            return 'gui', {}
        if args['help'] is not None:
            if args['help'] == 'all':
                return 'help', {}
            else:
                command_help = args['help']
                help_info = self.getCommandHelp(command_help)
                return 'help_command', help_info
        if args['list'] is not None:
            commands_list = self.getCommandList()
            return 'list', commands_list
        # if logged in, and there is a session, then check for the command and the args
        session_status = self.checkSession(args)
        if session_status == 'valid':
            if args['command'] is not None:
                cmd_struct = {}
                cmd_struct['COMMAND'] = args['command']
                # append parameters with the command
                params_list = self.parseParameters(parameters)
                cmd_struct.update(params_list)
                return 'cmd', cmd_struct
            # case user trying to log in while his session is valid
            elif None not in (args['userid'], args['password'], args['entity']):
                msg = 'You are already logged in, your session is valid.'
                return 'msg', msg
            else:
                msg = 'Command is not recognized!'
                return 'cmd_unknown', msg
        # case of first time use or session expired
        else:
            result, msg = self.login(args, session_status)
            return 'msg', msg

    def login(self, args, session_status=''):
        user = args['userid']
        password = args['password']
        entity = args['entity']
        # check if login credentials provided
        if None not in (user, password, entity):
            # check which system to use, live of test
            if entity == 'ote':
                # case ote is set, otherwise by default the system is live
                self.cl.useOTESystem()
            self.cl.setCredentials(user, password)
            r = self.cl.login()
            if r.isSuccess():
                # save login session
                loginSession = self.cl.getSession()
                # save session
                self.saveLocalSession(loginSession, entity)
                msg = "Login success. Your session valid for one hour max of idle time"
                return True, msg
            else:
                desc = r.getDescription()
                code = r.getCode()
                msg = "Server error: " + str(code) + " " + desc
                return False, msg
        # initial code running
        elif session_status == 'init':
            msg = "First you need to login: you can use the command: -u = <your user id> -p = <your password> -e = {ote,live} "
            return False, msg
        # case sessin expired
        elif session_status == 'expired':
            msg = "Your session expired. Please login again: you can use the command: -u = <your user id> -p = <your password> -e = {ote,live}"
            return False, msg

    def checkSession(self, args=''):
        data = {}
        # check if there is a session already exist
        try:
            with self.session_path.open('r') as f:
                data = json.load(f)
                f.close()
            entity = data['entity']
            time_format = "%Y-%m-%d %H:%M:%S"
            t_now = datetime.now().strftime(time_format)
            t_now_object = datetime.strptime(t_now, time_format)
            t_old = data['ts']
            t_old_object = datetime.strptime(t_old, time_format)
            t_new = t_now_object - timedelta(hours=1)
            if t_new < t_old_object:
                result = self.cl.setSession(data['session'])
                if entity == 'ote':
                    self.cl.useOTESystem()
                return 'valid'
            else:
                return 'expired'
            # Do something with the session file
        except IOError:
            return 'init'

    def logout(self):
        try:
            msg = ''
            with self.session_path.open('r') as f:
                data = json.load(f)
                f.close()
            entity = data['entity']
            if entity == 'ote':
                self.cl.useOTESystem()
            # delete remote session
            self.cl.setSession(str(data['session']))
            r = self.cl.logout()
            if r.isSuccess():
                flag = True
            else:
                flag = False

            # delete local session
            path = Path(__file__).parent / "../config/session.json"
            if os.path.exists(path):
                os.remove(path)  # delete local session
                if flag:
                    return True, 'Successfully logged out!'
                else:
                    return True, 'Local session deleted but remote session was not!'
            else:
                return True, 'Session already deleted'

        except Exception as e:
            msg = "Couldn't delete remote session due to: " + str(e)
            return False, msg

    def request(self, commands):
        # get commands in dictionary format
        response = self.cl.request(commands)
        return response

    def getResponse(self, response, mode=''):
        code = response.getCode()
        if code == 200:
            # check mode = {hash, plain, list}
            return response.getPlain()
        else:
            description = response.getDescription()
            message = "Server error: " + str(code) + " " + description
            return message

    def getCommandHelp(self, command_name):
        command_name = command_name.lower()
        path = Path(__file__).parent / "../commands/"
        data = {}
        files = os.listdir(path)
        for file in files:
            file_name, ext = file.split('.')
            file_name_lower_case = file_name.lower()
            if file_name_lower_case == command_name:
                file_path = os.path.join(path, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    f.close()
                    command = data['command']
                    description = data['description']
                    availability = data['availability']
                    paramaters = data['paramaters']
                    basic_info = f'Command: {command} \nDescription: {description} \nAvailability: {availability}\nParameters:'
                    headers = ['Parameter', 'Min', 'Definition', 'Type']
                    table = []
                    t = TextWrapper(width=30)
                    for row in paramaters:
                        row_data = []
                        for key in row:
                            if key == 'Definition':
                                row_data.append(t.fill(row[key]))
                            else:
                                row_data.append(row[key])
                        table.append(row_data)

                    paramaters_table = tabulate(
                        table, headers, tablefmt="fancy_grid")
                    return basic_info, paramaters_table
        else:
            return f"Command '{command_name}' not found!"

    def saveLocalSession(self, loginSession, entity):
        time_format = "%Y-%m-%d %H:%M:%S"
        ts = datetime.now().strftime(time_format)
        data = {}
        data['session'] = loginSession
        data['ts'] = ts
        data['entity'] = entity
        # write session and current time to local file
        path = Path(__file__).parent / "../config/session.json"
        with path.open('w') as f:
            json.dump(data, f)
            f.close
        return True

    def parseParameters(self, parameters):
        params_len = len(parameters)
        params = {}
        i = 0
        while i < (params_len):
            if '=' in parameters[i]:
                key, value = parameters[i].split('=')
                params[key] = value
            else:
                key = parameters[i]
                i += 1
                value = parameters[i]
                params[key] = value
            i += 1
        # return result
        return params

    def getCommandList(self):
        path = Path(__file__).parent / "../commands/"
        data = {}
        c_names = os.listdir(path)
        return_list = ''
        for name in sorted(c_names):
            file_name, ext = name.split('.')
            return_list += file_name + '\n'
        return return_list

    def parseResponse(self, response):
        pass
