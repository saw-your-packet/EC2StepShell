import boto3
from utils.CommandOutput import CommandOutput

class SsmWrapper:
    def __init__(self, profile, access_key, secret_key, token, region):
        session = None

        if profile is not None and profile != '':
            session = boto3.Session(profile_name=profile, region_name=region)
        elif token is not None and token != '':
            session = boto3.Session(
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key,
                aws_session_token = token,
                region_name=region
            )
        else:
            session = boto3.Session(
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key,
                region_name = region
            )

        self.client = session.client('ssm')


    def launch_command(self, instance_id, document_name, command, directory):
        response = self.client.send_command(
            InstanceIds = [
                instance_id
            ],
            DocumentName = document_name,
            Parameters = {
                'commands': [
                    command
                ],
                'workingDirectory': [
                    directory
                ]
            }
        )

        command_id = response['Command']['CommandId']
        
        return command_id


    def get_execution_output(self, command_id):
        response = self.client.list_command_invocations(
            CommandId = command_id,
            Details = True
        )

        status = response['CommandInvocations'][0]['CommandPlugins'][0]['Status']
        output = response['CommandInvocations'][0]['CommandPlugins'][0]['Output']
        
        command_output = CommandOutput(status, output)

        return command_output
