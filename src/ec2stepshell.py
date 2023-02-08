from utils.ArgumentsHandler import ArgumentsHandler
from core.ReverseShell import ReverseShell
from utils.constants import user_config

if __name__ == '__main__':
    args = ArgumentsHandler.initialize_args()
    argumentsHandler = ArgumentsHandler(args)

    if argumentsHandler.allGood == False:
        exit()

    ec2s2 = ReverseShell(
        profile=user_config['profile'],
        access_key=user_config['access_key'],
        secret_key=user_config['secret_key'],
        token=user_config['session_token'],
        region=user_config['region']
    )

    ec2s2.start_shell(args.instance)
