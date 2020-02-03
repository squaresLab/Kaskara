# -*- coding: utf-8 -*-
__all__ = ('SpoonAnalyser',)

from typing import Iterator
import contextlib

from dockerblade import DockerDaemon as DockerBladeDockerDaemon
from loguru import logger
import attr

from .post_install import IMAGE_NAME as SPOON_IMAGE_NAME
from ..analyser import Analyser
from ..analysis import Analysis
from ..container import ProjectContainer
from ..project import Project


@attr.s
class SpoonAnalyser(Analyser):
    _dockerblade: DockerBladeDockerDaemon = attr.ib(repr=False)

    @contextlib.contextmanager
    def _container(self, project: Project) -> Iterator[ProjectContainer]:
        """Provisions an ephemeral container for a given project."""
        create = self._dockerblade.client.containers.create
        launch = self._dockerblade.client.containers.run
        with contextlib.ExitStack() as stack:
            docker_project = create(project.image)
            stack.callback(docker_project.remove, force=True)

            docker_analyser = launch(SPOON_IMAGE_NAME, '/bin/sh',
                                     stdin_open=True,
                                     volumes_from=[docker_project.id],
                                     detach=True)
            stack.callback(docker_analyser.remove, force=True)

            dockerblade = self._dockerblade.attach(docker_analyser.id)
            yield ProjectContainer(project=project, dockerblade=dockerblade)

    def analyse(self, project: Project) -> Analysis:
        logger.debug(f"analysing Spoon project: {project}")
        with self._container(project) as container:
            return self._analyse_container(container)

    def _analyse_container(self, container: ProjectContainer) -> Analysis:
        raise NotImplementedError
