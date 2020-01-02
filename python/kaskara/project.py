# -*- coding: utf-8 -*-
__all__ = ('Project',)

import typing
from typing import FrozenSet, Iterator

import contextlib

import attr
import docker as _docker
import dockerblade as _dockerblade

from .container import ProjectContainer

KASKARA_IMAGE = 'squareslab/kaskara'


@attr.s(frozen=True, slots=True, auto_attribs=True)
class Project:
    """Describes a project under analysis.

    Attributes
    ----------
    image: str
        The name of the Docker image for this project.
    directory: str
        The absolute path of the root directory that holds the source code
        for this project.
    files: FrozenSet[str]
        The set of source code files for this project.
    ignore_errors: bool
        Indicates whether or not the analysis should proceed in the face of
        errors. If set to :code:`True`, the analysis will return partial
        results; if set to :code:`False`, an exception will be thrown instead.
    """
    _dockerblade: _dockerblade.DockerDaemon
    image: str
    directory: str
    files: FrozenSet[str]
    ignore_errors: bool = attr.ib(default=True)

    @contextlib.contextmanager
    def provision(self) -> Iterator[ProjectContainer]:
        """Provisions a Docker container for the project."""
        create = self._dockerblade.client.containers.create
        launch = self._dockerblade.client.containers.run
        with contextlib.ExitStack() as stack:
            docker_kaskara = create(KASKARA_IMAGE)
            stack.callback(docker_kaskara.remove, force=True)

            docker_project = launch(self.image, '/bin/sh',
                                    stdin_open=True,
                                    volumes_from=[docker_kaskara.id],
                                    detach=True)
            stack.callback(docker_project.remove, force=True)

            dockerblade = self._dockerblade.attach(docker_project.id)
            yield ProjectContainer(project=self, dockerblade=dockerblade)
