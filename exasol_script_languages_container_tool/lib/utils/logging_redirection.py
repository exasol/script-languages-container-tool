import sys


class _Tee(object):
    # Helper object which redirects calls to stdout/stderr to itself, prints to a give file and to real stdout/stderr
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


def create_docker_build_creator(task_creator):
    # Provides redirection of ALL logs to exaslct.log in the tasks job directory

    # Parameters:
    #   task_creator (function): creator function of the task
    def create_docker_build():
        task = task_creator()
        tee = _Tee(f'{task.get_log_path()}/exaslct.log', "w")
        print(f'Logging to :{tee.get_file().name}')
        return task

    return create_docker_build
