import sys

from exasol_integration_test_docker_environment.lib.base.base_task import BaseTask


class _Tee(object):
    # Helper object which redirects calls to stdout/stderr to itself, prints to a given file and to real stdout/stderr
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def get_file(self):
        return self.file

    def __del__(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()


def log_redirector_task_creator_wrapper(task_creator):
    # Provides redirection of ALL logs to exaslct.log in the tasks job directory

    # Parameters:
    #   task_creator (function): creator function which creates task
    def create_task_creator_wrapper():
        task = task_creator()
        tee = _Tee(get_log_path(task), "w")
        return task

    return create_task_creator_wrapper


def get_log_path(task: BaseTask):
    return f'{task.get_log_path()}/exaslct.log'
