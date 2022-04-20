import logging
import sys
from contextlib import contextmanager
from typing import Optional

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask


def _get_log_path(task: BaseTask):
    return f'{task.get_log_path()}/exaslct.log'


class Tee(object):
    """
    Helper object which redirects calls to stdout/stderr to itself, prints to a given file and to real stdout/stderr
    """

    def __init__(self, task, mode):
        self.log_file_path = _get_log_path(task)
        self.file = open(self.log_file_path, mode)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def close(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.file.close()
        logging.info(f'Log can be found at:{self.log_file_path}')

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    @classmethod
    @contextmanager
    def log_redirector_task_creator_wrapper(cls, task_creator):
        # Provides redirection of ALL logs to exaslct.log in the tasks job directory

        _tee: Optional[cls] = None

        # Parameters:
        #   task_creator (function): creator function which creates task
        def create_task_creator_wrapper():
            task = task_creator()
            nonlocal _tee
            _tee = cls(task, "w")
            return task

        try:
            yield create_task_creator_wrapper
        finally:
            if _tee is not None:
                _tee.close()
