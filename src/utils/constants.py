const = {
    'general':{
        'base_sleep': 0.3, # number of seconds before trying to get the output
        'intermediate_sleep': 0.15, # number of seconds between retries
        'max_retries': 3,
        'command_statuses':{
            'pending': 'Pending',
            'in_progress': 'InProgress',
            'success': 'Success',
            'timed_out': 'TimedOut',
            'cancelled': 'Cancelled',
            'failed': 'Failed',
            'execution_done': [
                'Success',
                'Failed',
                'TimedOut',
                'Cancelled'
            ]
        }
    },
    'linux':{
        'document': 'AWS-RunShellScript',
        'shell_display': 'root@{0}:{1}# ',
        'default_directory': '/tmp'
    },
    'windows':{
        'document': 'AWS-RunPowerShellScript',
        'shell_display': 'PS {1}> '
    }
}

user_config = {
    'os': '',
    'auth_method': '',
    'profile': '',
    'access_key': '',
    'secret_key': '',
    'session_token': '',
    'base_sleep': 0.3,
    'retry_sleep': 0.15,
    'max_retries': 3,
    'region': ''
    }
