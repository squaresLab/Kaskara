# -*- coding: utf-8 -*-
__all__ = ('Analyser',)

import abc
from typing_extensions import final

from .analysis import Analysis
from .project import Project


class Analyser(abc.ABC):
    """Provides a means of analysing projects."""
    @abc.abstractmethod
    def analyse(self, project: Project) -> Analysis:
        """Performs an analysis of a given project."""
        ...

    @final
    def __call__(self, project: Project) -> Analysis:
        """Alias for :meth:`analyse`."""
        return self.analyse(project)
