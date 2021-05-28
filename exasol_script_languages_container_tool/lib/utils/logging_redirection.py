import sys


def create_docker_build_creator(task_creator):
    # Provides redirection of ALL logs to exaslct.log in the tasks job directory

    # Parameters:
    #   task_creator (function): creator function of the task
    def create_docker_build():
        task = task_creator()
        logging_redirection_file = open(f'{task.get_log_path()}/exaslct.log', "w")
        print(f'Logging to :{logging_redirection_file.name}')
        sys.stdout = logging_redirection_file
        sys.stderr = logging_redirection_file
        return task

    return create_docker_build
