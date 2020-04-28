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


class Core:
    def __init__(self):
        # create private config list
        self.command = ''
        self.cl = AC()

    def login(self, args):
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
                self.saveSession(loginSession)
                msg = "Login success. Your session valid for one hour max of idle time"
                # save session
                return True, msg
            else:
                desc = r.getDescription()
                code = r.getCode()
                msg = "Server error: " + str(code) + " " + desc
                return False, msg
        else:
            msg = "Please login by entering all login information: userid, password and entity"
            return False, msg

    def logout(self):
        pass

    def request(self, commands):
        # get commands in dictionary format
        response = self.cl.request(commands)
        return response

    def getResponse(self, response, mode):
        code = response.getCode()
        if code == 200:
            print(response.getPlain())
        else:
            description = response.getDescription()
            message = "Server error: " + str(code) + " " + description
            print(message)

    def parseArgs(self, args, parameters):
        # if logged in, and there is a session, then check for the command and the args
        if self.checkSession(args) == True:
            if args['command'] is not None:
                cmd_struct = {}
                cmd_struct['command'] = args['command']
                # append parameters with the command
                params_list = self.parseParameters(parameters)
                cmd_struct.update(params_list)
                return cmd_struct
            else:
                raise Exception('No command entered!')
        # if not logged in, perform login, needed = user, pass, entity
        else:
            result, msg = self.login(args)
            if result == True:
                return msg
            else:
                return msg

    def checkSession(self, args):
        data = {}
        # check if there is a session already exist
        try:
            path = Path(__file__).parent / "../Config/session.json"
            with path.open('r') as f:
                data = json.load(f)
                f.close()
            time_format = "%Y-%m-%d %H:%M:%S"
            t_now = datetime.now().strftime(time_format)
            t_now_object = datetime.strptime(t_now, time_format)
            t_old = data['ts']
            t_old_object = datetime.strptime(t_old, time_format)
            t_new = t_now_object - timedelta(hours=1)
            if t_new < t_old_object:
                result = self.cl.setSession(str(data['session']))
                return True
            # Do something with the file
        except IOError:
            return False

    def saveSession(self, loginSession):
        time_format = "%Y-%m-%d %H:%M:%S"
        ts = datetime.now().strftime(time_format)
        data = {}
        data['session'] = loginSession
        data['ts'] = ts
        # write session and current time to local file
        path = Path(__file__).parent / "../Config/session.json"
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

    def parseResponse(self, response):
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
         Please do not mess up this text!
         --------------------------------
             I have indented it
             exactly the way
             I want it
         '''))
    parser.add_argument(
        '--command', '-c', help='Enter a command e.g. -c=CheckDomain or -c CheckDomain')
    parser.add_argument(
        '--entity', '-e', help="set entity to either live or ote system e.g. -e=ote", choices={'live', 'ote'})
    parser.add_argument('--userid', '-u', help='Your login user ID')
    parser.add_argument('--password', '-p', help="Your login password")
    parser.add_argument('--gui', '-g', help="Start graphical application")
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help='All additional args e.g. limit=5')

    # original_args = '-l login -p pass XX YY ZZ kk'
    original_args = ' '.join(sys.argv[1:])
    # remove spaces around the = cases ' =', '= ', ' = '
    original_args = original_args.replace(" = ", "=")
    original_args = original_args.replace(" =", "=")
    original_args = original_args.replace("= ", "=")
    splitted_args = (original_args.split())
    args = vars(parser.parse_args(splitted_args))
    print(args)
    reminderargs = args['args']
    coreObj = Core()
    try:
        parsed_params = coreObj.parseArgs(args, reminderargs)
        print(parsed_params)
        response = coreObj.request(parsed_params)
    except Exception as e:
        print("Command failed due to: " + str(e))
    # print(reminderargs)
