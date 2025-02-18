from pathlib import Path

from exasol_integration_test_docker_environment.lib.models.data.test_container_content_description import (
    TestContainerBuildMapping,
    TestContainerContentDescription,
    TestContainerRuntimeMapping,
)

TEST_DATA_TARGET = "/tests_data"


def build_test_container_content(
    test_container_folder: str,
) -> TestContainerContentDescription:
    test_container_path = Path(test_container_folder)
    test_container_build_path = test_container_path / "build"
    test_container_build_deps_path = test_container_path / "build" / "deps"
    test_container_test_data_path = test_container_path / "test_data"
    test_container_tests_path = test_container_path / "tests"
    return TestContainerContentDescription(
        docker_file=str(test_container_build_path / "Dockerfile"),
        build_files_and_directories=[
            TestContainerBuildMapping(
                source=test_container_build_deps_path, target="deps"
            )
        ],
        runtime_mappings=[
            TestContainerRuntimeMapping(
                source=test_container_tests_path,
                target="/tests_src",
                deployment_target="/tests",
            ),
            TestContainerRuntimeMapping(
                source=test_container_test_data_path, target=TEST_DATA_TARGET
            ),
        ],
    )
