import unittest

import utils as exaslct_utils
from exasol_integration_test_docker_environment.testing import utils


class DockerRunDBTestExternalDBTest(unittest.TestCase):

    def setUp(self):
        print(f"SetUp {self.__class__.__name__}")
        self.test_environment = exaslct_utils.ExaslctTestEnvironmentWithCleanUp(self, exaslct_utils.EXASLCT_DEFAULT_BIN)
        self.test_environment.clean_images()
        self.docker_environment_name = self.__class__.__name__
        self.docker_environments = self.test_environment.spawn_docker_test_environments(self.docker_environment_name)
        # localhost gets translated in exaslct to the Gateway address of the docker environment network, because thats typically the IP Adress of the bridge to the host, for google cloud this means it should be able to connect to the db via the port forwards from the test container
        # TODO check alternative of ip address on default bridge
        self.docker_environment = self.docker_environments.on_host_docker_environment

    def tearDown(self):
        utils.close_environments(self.docker_environments, self.test_environment)

    def test_run_db_tests_external_db(self):
        arguments = " ".join([
            f"--environment-type external_db",
            f"--external-exasol-db-host {self.docker_environment.database_host}",
            f"--external-exasol-db-port {self.docker_environment.ports.database}",
            f"--external-exasol-bucketfs-port {self.docker_environment.ports.bucketfs}",
            f"--external-exasol-ssh-port {self.docker_environment.ports.ssh}",
            f"--external-exasol-db-user {self.docker_environment.db_username}",
            f"--external-exasol-db-password {self.docker_environment.db_password}",
            f"--external-exasol-bucketfs-write-password {self.docker_environment.bucketfs_password}",
            exaslct_utils.get_full_test_container_folder_parameter()
        ])
        command = f"{self.test_environment.executable} run-db-test {arguments}"
        self.test_environment.run_command(
            command, track_task_dependencies=True)


if __name__ == '__main__':
    unittest.main()
