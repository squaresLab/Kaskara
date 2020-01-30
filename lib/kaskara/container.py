# -*- coding: utf-8 -*-
__all__ = ('ProjectContainer',)

import typing

import attr
import dockerblade as _dockerblade

if typing.TYPE_CHECKING:
    from .project import Project


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProjectContainer:
    """Provides access to a container for a project under analysis.

    Attributes
    ----------
    project: Project
        The project under analysis.
    dockerblade: dockerblade.Container
        The underlying DockerBlade container for the project.
    shell: dockerblade.Shell
        Provides access to an executable shell for this container.
    files: dockerblade.FileSystem
        Provides root-level access to the filesystem for this container.
    """
    project: 'Project'
    dockerblade: _dockerblade.Container
    shell: _dockerblade.Shell = attr.ib(init=False)
    files: _dockerblade.FileSystem = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, 'shell', self.dockerblade.shell('/bin/sh'))
        object.__setattr__(self, 'files', self.dockerblade.filesystem())
