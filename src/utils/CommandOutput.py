from utils.constants import const

class CommandOutput:
    def __init__(self, status, output):
        self._status = status
        self._output = output 

    @property
    def status(self):
        return self._status

    @property
    def output(self):
        return self._output

    def is_execution_finished(self):
        statuses = const['general']['command_statuses']

        if self._status in statuses['execution_done']:
            return True

        return False
