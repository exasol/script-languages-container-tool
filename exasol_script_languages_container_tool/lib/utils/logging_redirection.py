import logging
import sys
from contextlib import contextmanager

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask


def _get_log_path(task: BaseTask):
    return f'{task.get_log_path()}/exaslct.log'


class _Tee(object):
    """
    Helper object which redirects calls to stdout/stderr to itself, prints to a given file and to real stdout/stderr
    """

    def __init__(self):
        self.is_open = False

    def open(self, task, mode):
        self.log_file_path = _get_log_path(task)
        self.file = open(self.log_file_path, mode)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        self.is_open = True

    def close(self):
        if self.is_open:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            self.file.close()
            logging.info(f'Log can be found at:{self.log_file_path}')

    def write(self, data):
        if self.is_open:
            self.file.write(data)
            self.stdout.write(data)
        else:
            raise RuntimeError("_Tee object used but not initialized.")


@contextmanager
def log_redirector_task_creator_wrapper(task_creator):
    # Provides redirection of ALL logs to exaslct.log in the tasks job directory

    _tee = _Tee()

    # Parameters:
    #   task_creator (function): creator function which creates task
    def create_task_creator_wrapper():
        task = task_creator()
        _tee.open(task, "w")
        return task

    try:
        yield create_task_creator_wrapper
    finally:
        _tee.close()
