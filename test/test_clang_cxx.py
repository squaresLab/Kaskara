# -*- coding: utf-8 -*-
import pytest

import os

import docker as _docker
import dockerblade as _dockerblade

import kaskara
from kaskara.clang import ClangAnalyser
from kaskara.clang.post_install import post_install as install_clang_backend

DIR_HERE = os.path.dirname(__file__)


@pytest.fixture
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
            '/workspace/src/action_node.cpp',
        }
        project = kaskara.Project(
            dockerblade=dockerblade,
            image=docker_image_name,
            directory='/workspace',
            files=files,
        )
        yield project


def test_find_functions(bt_project) -> None:
    with bt_project.provision() as container:
        analyzer = ClangAnalyser()
        loops = analyzer._find_loops(container)








