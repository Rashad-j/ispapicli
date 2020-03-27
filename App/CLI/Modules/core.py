from hexonet.apiconnector.apiclient import APIClient as AC
from hexonet.apiconnector.response import Response
import re
from .exceptions import NoLoginPass


class Core:
    def __init__(self):
        self.commandList = []
        # create private config list
        self.__config = {}
        self.cl = AC()
        self.cl.useOTESystem()
        self.loginSession = ''

    def login(self):
        try:
            login = self.__config['login']
            password = self.__config['password']
            self.cl.setCredentials(login, password)
            r = self.cl.login()
            if r.isSuccess():
                # get login session
                self.loginSession = self.cl.getSession()
                self.cl.saveSession
                return True
            else:
                return False
        except Exception:
            return 'Missing Login Credentials'

    def logout(self):
        pass

    def request(self):
        # set user session
        self.cl.setSession(str(self.loginSession))
        # check if commands provided previously
        if len(self.commandList) > 0:
            # get commands in dictionary format
            commands = self.parseCommand(self.commandList)
            # request command
            response = self.cl.request(commands)
            return response
        else:
            return 'No commands provided'

    def getResponse(self, response, mode):
        print(response.getPlain())

    def parseArgs(self, args, nb_args):
        # case no arguments provided
        if nb_args == 1:
            return 'start_gui'
        # get commands and arguments
        for i in range(1, nb_args):
            arg = args[i]
            if re.match(r'^-', arg):

                # case gui is called
                m = re.match(r'^--gui', arg)
                if m:
                    return 'start_gui'

                # case user
                m = re.match(r'^-u([^ ]*)?', arg) or re.match(r'^--user\=(.+)', arg)
                if m:
                    if m.group(1):
                        self.__config["user"] = m.group(1)
                        # print m.group(1)
                    continue

                # case login
                m = re.match(r'^-l([^ ]*)?',
                             arg) or re.match(r'^--login\=(.+)', arg)
                if m:
                    if m.group(1):
                        self.__config["login"] = m.group(1)
                    continue
                ####
                m = re.match(r'^--password\=(.+)', arg)
                if m:
                    if m.group(1):
                        self.__config["password"] = m.group(1)
                    continue
                ####
                m = re.match(r'^-e([^ ]*)?', arg) or re.match(r'^--entity\=(.+)', arg)
                if m:
                    if m.group(1):
                        self.__config["entity"] = m.group(1)
                    continue
                ####
                m = re.match(r'^-h([^ ]*)?', arg) or re.match(r'^--help', arg)
                if m:
                    showhelp = True
                    continue
                ####
                if re.match(r'^-v([^ ]*)?', arg) or re.match(r'^--version', arg):
                    return 'show_version'
                ####
                if re.match(r'^-p(.*)', arg):
                    if m.group(1):
                        property_string = m.group(1)
                    continue
                ####
            else:
                self.commandList.append(arg)

        return self.commandList

    def parseCommand(self, cmds):
        c_len = len(cmds)
        # output command dictionary
        struct_cmds = {}
        for i in range(c_len):
            # if user provided command keyword
            if i == 0 and cmds[i] != "command":
                struct_cmds['COMMAND'] = cmds[i]
            else:
                key, value = cmds[i].split('=')
                struct_cmds[key] = value
        # return result
        return struct_cmds

    def parseResponse(self, response):
        pass


# if __name__ == "__main__":
#    obj = Core()
