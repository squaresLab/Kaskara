from __future__ import annotations

__all__ = ("Analyser",)

import abc
import contextlib
import typing as t

if t.TYPE_CHECKING:
    from .analysis import Analysis
    from .project import Project


class Analyser(abc.ABC):
    """Provides a means of analysing projects."""
    @classmethod
    @abc.abstractmethod
    @contextlib.contextmanager
    def for_project(cls, project: Project) -> t.Iterator[t.Self]:
        """Creates an analyser for a given project."""
        ...

    @abc.abstractmethod
    def run(self) -> Analysis:
        """Runs the analysis."""
        ...

    @t.final
    def __call__(self) -> Analysis:
        """Alias for :meth:`run`."""
        return self.run()
