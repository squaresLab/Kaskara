from __future__ import annotations

__all__ = ("Project",)

import contextlib
import typing as t

import attr

from kaskara.clang.common import VOLUME_LOCATION as KASKARA_CLANG_VOLUME_LOCATION
from kaskara.clang.common import VOLUME_NAME as KASKARA_CLANG_VOLUME_NAME
from kaskara.container import ProjectContainer
from kaskara.spoon.common import VOLUME_LOCATION as KASKARA_SPOON_VOLUME_LOCATION
from kaskara.spoon.common import VOLUME_NAME as KASKARA_SPOON_VOLUME_NAME
from kaskara.util import dockerblade_from_env

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    import dockerblade as _dockerblade


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
    _dockerblade: _dockerblade.DockerDaemon = attr.ib(repr=False)
    image: str
    directory: str
    files: frozenset[str]
    ignore_errors: bool = attr.ib(default=True)

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "image": self.image,
            "directory": self.directory,
            "files": list(self.files),
            "ignore-errors": self.ignore_errors,
        }

    @classmethod
    @contextlib.contextmanager
    def load(
        cls,
        image: str,
        directory: str,
        files: t.Iterable[str],
        *,
        ignore_errors: bool = True,
    ) -> t.Iterator[Project]:
        with dockerblade_from_env() as daemon:
            project = Project(
                dockerblade=daemon,
                image=image,
                directory=directory,
                files=frozenset(files),
                ignore_errors=ignore_errors,
            )
            yield project

    @contextlib.contextmanager
    def provision(
        self,
        *,
        mount_kaskara_clang: bool = True,
        mount_kaskara_spoon: bool = False,
    ) -> Iterator[ProjectContainer]:
        """Provisions a Docker container for the project."""
        launch = self._dockerblade.client.containers.run
        with contextlib.ExitStack() as stack:
            volumes: dict[str, t.Any] = {}
            if mount_kaskara_clang:
                volumes[KASKARA_CLANG_VOLUME_NAME] = {
                    "bind": KASKARA_CLANG_VOLUME_LOCATION,
                    "mode": "ro",
                }

            if mount_kaskara_spoon:
                volumes[KASKARA_SPOON_VOLUME_NAME] = {
                    "bind": KASKARA_SPOON_VOLUME_LOCATION,
                    "mode": "ro",
                }

            docker_project = launch(
                self.image,
                "/bin/sh",
                stdin_open=True,
                volumes=volumes,
                detach=True,
            )

            stack.callback(docker_project.remove, force=True)
            assert docker_project.id is not None
            yield self.attach(docker_project.id)

    def attach(self, id_or_name: str) -> ProjectContainer:
        """Attaches to a running Docker container for the project.

        All necessary kaskara binaries must be installed in the container.
        """
        dockerblade = self._dockerblade.attach(id_or_name)
        return ProjectContainer(project=self, dockerblade=dockerblade)
