from ec2stepshell.utils.constants import const,user_config
from termcolor import cprint
import os.path

class TerminalEmulator:
    def __init__(self, hostname, pwd):
        self.hostname = hostname
        self.pwd = pwd
        self.shell_display = str.format(const[user_config['os']]['shell_display'], hostname, pwd)
        self.cd_executed = False

    def change_directory(self, pwd, strip=False):
        if strip == True:
            pwd = pwd[3:]
        
        if self.cd_executed == False:
            cprint('[ec2s2] When executing "cd" the operation is not sent to the instance, but kept locally for the next commands.\n\tThe directory name is extracted by removing "cd " from the command.\n\tFor example:\n\t\t"cd /home/ec2-user" will set the directory to "/home/ec2-user"\n\t\t"cd /home/ec2-user; whoami" will set the directory to "/home/ec2-user; whoami"\n', 'blue')
            self.cd_executed = True

        pwd = pwd.strip()

        if user_config['os'] == 'linux':
            if pwd.startswith('/'):
                self.pwd = pwd
            else:
                self.pwd += '/' + pwd
        else:
            if pwd[1:].startswith(':\\') or pwd[1:].startswith(':/'):
                self.pwd = pwd
            else:
                self.pwd += '/' + pwd
        
        self.pwd = os.path.normpath(self.pwd)

        if user_config['os'] == 'linux':
            self.pwd = self.pwd.replace('\\','/')
        else:
            self.pwd = self.pwd.replace('/','\\')

        self.shell_display = str.format(const[user_config['os']]['shell_display'], self.hostname, self.pwd)
