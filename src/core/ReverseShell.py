import os
import re
import traceback
from termcolor import cprint
from time import sleep
from ssm.SsmWrapper import SsmWrapper
from utils.constants import const, user_config
from utils.terminal.TerminalEmulator import TerminalEmulator


class ReverseShell:
    def __init__(self, profile, access_key, secret_key, token, region):
        self.ssm_wrapper = SsmWrapper(
            profile=profile,
            access_key=access_key,
            secret_key=secret_key,
            token=token,
            region=region
        )
        self.queue = {}

    def start_shell(self, instance_id):
        cprint('[x] Starting reverse shell on EC2 instance ' + instance_id, 'blue')
        self.determine_os(instance_id, user_config['os'])

        terminal_emulator = self.get_shell_display(instance_id, user_config['os'])

        while True:
            command = input(terminal_emulator.shell_display)

            if command.strip().startswith('!'):
                try:
                    self.handle_ec2s2_command(command)
                except IndexError:
                    cprint(f'[!] \'{command}\' failed. Check command ID and try again.', 'red')
                finally:
                    continue

            if command == '' or command.isspace():
                continue

            if command.strip() == 'clear' or command.strip() == 'cls':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            if command.startswith('cd '):
                terminal_emulator.change_directory(pwd=command, strip=True)
                print(end='')
                continue

            if command.strip() == 'exit':
                cprint('[x] Exit...', 'blue')
                exit()

            try:
                output = self.send_command_and_get_output(
                    document=const[user_config['os']]['document'],
                    command=command,
                    instance_id=instance_id,
                    directory=terminal_emulator.pwd,
                )

                if output is not None:
                    print(output.output, end='')
            except Exception as e:
                cprint(f'[!] An unknown local error occurred when running the given command. Help me improve the tool by creating an issue on GitHub with the error message.', 'red')
                traceback.print_exc()
  

    def get_shell_display(self, instance_id, os):
        cprint('\n[x] Retrieving hostname', 'light_blue')

        hostname_obj = self.send_command_and_get_output(
            document=const[os]['document'],
            command='hostname',
            instance_id=instance_id,
            directory='.'
        )

        hostname = hostname_obj.output.replace('\n', '')
        cprint('\t Hostname: ' + hostname, 'light_blue')

        cprint('[x] Retrieving working directory', 'light_blue')

        pwd_obj = self.send_command_and_get_output(
            document=const[os]['document'],
            command='pwd',
            instance_id=instance_id,
            directory='.'
        )

        pwd = pwd_obj.output.replace('\n', '')

        if os == 'windows':
            matches = re.findall(r".:\\.+(?=\r)", pwd_obj.output, re.MULTILINE)
            pwd = matches[0]

        cprint('\t Working directory: ' + pwd + '\n', 'light_blue')

        terminal_emulator = TerminalEmulator(hostname=hostname, pwd=pwd)

        status_in_progress = const['general']['command_statuses']['in_progress']
        if hostname_obj.status == status_in_progress or pwd_obj.status == status_in_progress:
            cprint('[~] Not all initialization information was retrieved. It is recommended to restart the shell with increased delays or number of retries.', 'yellow')

        return terminal_emulator

    def send_command_and_get_output(self, document, command, instance_id, directory):
        execution_finished = False
        output_command = None

        command_id = self.ssm_wrapper.launch_command(
            instance_id=instance_id,
            document_name=document,
            command=command,
            directory=directory
        )

        sleep(user_config['base_sleep'])

        retries = 0
        while execution_finished == False:
            if retries >= user_config['max_retries']:
                cprint(f'[!] Maximum number of retries reached for command id {command_id}', 'red')
                cprint(f'[x] You can manually retry to get the output with \'!retry {command_id}\'', 'blue')
                cprint('[x] To view all commands that were not finished: \'!showqueue\'', 'blue')
                self.queue[command_id] = command
                break

            output_command = self.ssm_wrapper.get_execution_output(command_id=command_id)
            execution_finished = output_command.is_execution_finished()

            if execution_finished == False:
                sleep(user_config['retry_sleep'])
                retries += 1
                continue

            return output_command

    def handle_ec2s2_command(self, raw_command):
        raw_command = raw_command.strip()[1:]
        params = raw_command.split(' ')

        if len(params) == 0:
            cprint('[!] Command can\'t be interpreted', 'red')
            return

        command = params[0]

        if command == 'help':
            cprint('[x] !showqueue', 'blue')
            cprint('\t Display commands in queue. For these commands the output was not retrieved using the configured number of retries')
            cprint('[x] !clearqueue', 'blue')
            cprint('\t Clears the commands in queue without retrieving the output.')
            cprint('[x] !retry command_id', 'blue')
            cprint('\t Retry to get the output of a command. Example: \'!retry 6712a779-2ec2-4514-a946-9ab06861457f\'')
            return

        if command == 'retry':
            if len(params) != 2:
                cprint('[!] \'retry\' command needs to have the structure \'!retry command_id\'', 'red')
                return

            output_command = self.ssm_wrapper.get_execution_output(
                command_id=params[1])

            if output_command.is_execution_finished() == False:
                cprint(f'[x] Command execution not finished. Current status: {output_command.status}', 'blue')
                return

            cprint(f'[x] Command execution finished with status \'{output_command.status}\'', 'blue')
            cprint(f'[x] Output:', 'blue')
            cprint(output_command.output, 'green')

            if params[1] in self.queue.keys():
                self.queue.pop(params[1])

            return

        if command == 'showqueue':
            if len(self.queue.keys()) == 0:
                cprint('[x] No commands in queue', 'blue')
                return

            cprint('[x] Commands in queue:', 'blue')

            for k, v in self.queue.items():
                cprint(f'\t{k}: {v}', 'blue')

            cprint(f'[x] Retry to get the output for a command with \'!retry command_id\'', 'blue')

            return

        if command == 'clearqueue':
            self.queue = {}
            cprint(f'[x] Queue cleared', 'blue')

            return

        cprint('[!] Command unknown', 'red')

    def determine_os(self, instance_id, os):
        if os == '':
            cprint('[~] OS not specified. Trying to determine...', 'yellow')
            os = 'linux'

        try:
            output = self.send_command_and_get_output(
                document=const[os]['document'],
                command='whoami',
                instance_id=instance_id,
                directory='.',
            )
 
            if output.status == const['general']['command_statuses']['failed']:
                raise Exception('OS')
            if output.status == const['general']['command_statuses']['success']:
                cprint(f'[x] Instance\'s OS is {os}', 'blue')
                user_config['os'] = os
            else:
                cprint('[!] Can\'t determine OS. Try increasing the maximum retries, the retry delay or take a guess.', 'red')
                exit()
        except Exception as e:
            if e.args[0] == 'OS' or e.response['Error']['Code'] == 'UnsupportedPlatformType':
                cprint(f'[~] Instance\'s OS is not {os.upper()}', 'yellow')
                os = 'linux' if os == 'windows' else 'windows'
                self.determine_os(instance_id, os)
                return

            if e.response['Error']['Code'] == 'InvalidInstanceId':
                cprint(f'[!] Instance id is wrong or can\'t communicate with SSM', 'red')
                exit()


        