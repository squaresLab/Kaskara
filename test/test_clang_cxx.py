import os

import docker as _docker
import dockerblade as _dockerblade
import pytest

import kaskara
from kaskara.clang.analyser import ClangAnalyser
from kaskara.clang.post_install import post_install as install_clang_backend
from kaskara.core import FileLocation

DIR_HERE = os.path.dirname(__file__)


@pytest.fixture()
def bt_project():
    # make sure that the clang analyser backend has been built
    install_clang_backend()

    docker_url: str = os.environ.get("DOCKER_HOST")
    docker = _docker.from_env()
    docker_image_name = "kaskara/examples:BehaviorTree.CPP"
    docker_directory = os.path.join(DIR_HERE, "examples/BehaviorTree.CPP")

    # build the Docker image
    docker.images.build(path=docker_directory, tag=docker_image_name, rm=True)

    with _dockerblade.DockerDaemon(docker_url) as dockerblade:
        files = {
            "/workspace/src/blackboard.cpp",
        }
        project = kaskara.Project(
            dockerblade=dockerblade,
            image=docker_image_name,
            directory="/workspace",
            files=files,
        )
        yield project


@pytest.fixture()
def bt_clang(bt_project):
    with ClangAnalyser.for_project(bt_project) as analyzer:
        yield analyzer


@pytest.mark.xfail(reason="unresolved bug")
def test_find_loops(bt_clang) -> None:
    analyzer = bt_clang
    loops = analyzer._find_loops()

    def assert_in_loop(location_str: str) -> None:
        location = FileLocation.from_string(location_str)
        assert loops.is_within_loop(location)

    def assert_not_in_loop(location_str: str) -> None:
        location = FileLocation.from_string(location_str)
        assert not loops.is_within_loop(location)

    assert_in_loop("/workspace/src/blackboard.cpp@54:1")
    assert_in_loop("/workspace/src/blackboard.cpp@84:1")
    assert_not_in_loop("/workspace/src/blackboard.cpp@86:1")


def test_find_functions(bt_clang) -> None:
    analyzer = bt_clang
    functions = analyzer._find_functions()

    functions_in_file = list(functions.in_file("/workspace/src/blackboard.cpp"))
    assert len(functions) == 5
    assert len(functions_in_file) == 5


def test_find_statements(bt_clang) -> None:
    analyzer = bt_clang
    statements = analyzer._find_statements()

    statements_in_file = list(statements.in_file("/workspace/src/blackboard.cpp"))
    assert len(statements_in_file) > 0
