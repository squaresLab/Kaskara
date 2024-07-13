from __future__ import annotations

__all__ = ("PythonAnalyser",)

import contextlib
import typing as t
from dataclasses import dataclass

from loguru import logger

from kaskara.analyser import Analyser
from kaskara.analysis import Analysis
from kaskara.python.functions import collect_functions
from kaskara.python.loops import collect_loops
from kaskara.python.statements import collect_statements

if t.TYPE_CHECKING:
    from kaskara.container import ProjectContainer
    from kaskara.project import Project


@dataclass
class PythonAnalyser(Analyser):
    _project: Project
    _container: ProjectContainer

    @classmethod
    @contextlib.contextmanager
    def for_project(cls, project: Project) -> t.Iterator[t.Self]:
        logger.debug(f"analysing Python project: {project}")
        with project.provision() as container:
            yield cls(project, container)

    def run(self) -> Analysis:
        functions = collect_functions(self._container)
        statements = collect_statements(self._container)
        loops = collect_loops(self._container)
        insertions = statements.insertions()
        return Analysis(
            files=self._project.files,
            functions=functions,
            statements=statements,
            insertions=insertions,
            loops=loops,
        )
