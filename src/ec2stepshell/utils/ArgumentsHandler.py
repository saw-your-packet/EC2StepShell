import sys
import argparse
from colorama import init
from termcolor import cprint
from pyfiglet import figlet_format
from ec2stepshell.utils.constants import user_config


class ArgumentsHandler:
    def __init__(self, args):
        self.args = args
        self.auth_method = 'default'
        self.allGood = self.verify()
        self.change_config()

    def verify(self):
        # Persistent/Temporary Access Credentials
        isProfile = isPac = isTac = False

        if self.args.profile is not None:
            isProfile = True
            self.auth_method = 'profile'

        if self.args.access_key is not None and self.args.secret_key is not None:
            isPac = True
            self.auth_method = 'pac'

        if isPac == True and self.args.session_token is not None:
            isPac = False
            isTac = True
            self.auth_method = 'tac'

        if isProfile and (isPac or isTac):
            cprint(f'[!] Conflict between using profile "{self.args.profile}" and given access credentials. Run again with only one authentication method.', 'red')
            return False

        if isProfile == isPac == isTac == False:
            cprint('[~] No authentication was provided. The default profile from AWS CLI will be used.', 'yellow')

        return True

    def change_config(self):
        user_config['auth_method'] = self.auth_method

        if self.auth_method == 'profile':
            user_config['profile'] = self.args.profile
        elif self.auth_method == 'pac':
            user_config['access_key'] = self.args.access_key
            user_config['secret_key'] = self.args.secret_key
        elif self.auth_method == 'tac':
            user_config['access_key'] = self.args.access_key
            user_config['secret_key'] = self.args.secret_key
            user_config['session_token'] = self.args.session_token
        else:
            user_config['profile'] = 'default'

        if self.args.os is not None:
            user_config['os'] = self.args.os

        if self.args.delay is not None and self.args.delay > 0:
            user_config['base_sleep'] = self.args.delay

        if self.args.retry_delay is not None and self.args.retry_delay > 0:
            user_config['retry_sleep'] = self.args.retry_delay

        if self.args.max_retries is not None and self.args.max_retries > 0:
            user_config['max_retries'] = self.args.max_retries

        if self.args.region is not None and self.args.region != '':
            user_config['region'] = self.args.region

    @classmethod
    def initialize_args(self):
        init(strip=not sys.stdout.isatty())
        cprint(figlet_format('EC2StepShell', font='slant'), 'green')

        parser = argparse.ArgumentParser(
            description="Getting reverse shells into EC2 instances, even if you don't have network connectivity to them.",
            epilog="Additional commands are available after a shell is established. Once the shell started, type '!help' to access them.",
            prog="python3 -m ec2stepshell"
        )

        cprint("Author: Eduard Agavriloae\n\t@saw-your-packet\n\teduard@breakingbreakpoints.com\n", "magenta")

        parser.add_argument('instance', help='the ID of the target EC2 instance')

        profile = parser.add_argument_group()
        profile.add_argument("-p", "--profile", help="profile to use from AWS CLI")

        access_keys = parser.add_argument_group()
        access_keys.add_argument("--access-key", metavar="aws_access_key_id")
        access_keys.add_argument("--secret-key", metavar="aws_secret_access_key")
        access_keys.add_argument("--session-token", metavar="aws_session_token",
                                 help="session token is required only if the provided access keys are temporary access credentials")

        configurations = parser.add_argument_group()
        configurations.add_argument("--region", help="The region where the EC2 instance is", required=True)
        configurations.add_argument("--os", choices=["linux", "windows"], metavar="(linux|windows)",
                                    help="It is recommended to provided this if known, but it will be determined if not specified")
        configurations.add_argument("--delay", type=float, default=0.7,
                                    help="Number of seconds before trying to retrieve the command's output. Windows instances require bigger values. Default is 0.7")
        configurations.add_argument("--retry-delay", type=float, default=0.3,
                                    help="Number of seconds between retries for retrieving a command's output. Windows instances require bigger values. Default is 0.3")
        configurations.add_argument("--max-retries", type=int, default=3,
                                    help="Number of retries for retrieving a command's output. Default is 3")

        args = parser.parse_args()

        return args
