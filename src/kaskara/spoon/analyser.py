__all__ = ("SpoonAnalyser",)

import contextlib
import json
import os
import typing as t
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import dockerblade
from loguru import logger
from overrides import overrides

from kaskara.analyser import Analyser
from kaskara.analysis import Analysis
from kaskara.container import ProjectContainer
from kaskara.core import FileLocationRange
from kaskara.functions import ProgramFunctions
from kaskara.loops import ProgramLoops
from kaskara.project import Project
from kaskara.spoon.analysis import SpoonFunction, SpoonStatement
from kaskara.spoon.common import (
    JAR_PATH,
    JAVA_PATH,
)
from kaskara.statements import ProgramStatements


@dataclass
class SpoonAnalyser(Analyser):
    _project: Project
    _container: ProjectContainer
    _workdir: str | None = field(default=None)

    @classmethod
    @contextlib.contextmanager
    @overrides
    def for_project(
        cls,
        project: Project,
        *,
        mount_binaries: bool = True,
    ) -> t.Iterator[t.Self]:
        with project.provision(mount_kaskara_spoon=mount_binaries) as container:
            yield cls(project, container)

    @overrides
    def run(self) -> Analysis:
        container = self._container
        dir_source = Path(self._project.directory)
        assert dir_source.is_absolute()

        container_output_dir = container.files.mktemp()
        container.files.remove(container_output_dir)
        container.files.makedirs(container_output_dir)

        paths_to_index: list[Path]
        if self._project.files:
            paths_to_index = [Path(filename) for filename in self._project.files]
            paths_to_index = [
                path if path.is_absolute() else dir_source / path
                for path in paths_to_index
            ]
        else:
            paths_to_index = [dir_source]

        workdir = self._workdir or "/"
        paths_to_index_arg = " ".join(str(path) for path in paths_to_index)
        command_args = [
            JAVA_PATH,
            "-jar",
            JAR_PATH,
            paths_to_index_arg,
            "-o",
            container_output_dir,
            "2>&1",
        ]
        command = " ".join(command_args)
        logger.info(f"running kaskara-spoon: {command}")
        try:
            output = container.shell.check_output(
                command,
                text=True,
                cwd=workdir,
            )
            logger.debug(f"kaskara-spoon output: {output}")
        except dockerblade.exceptions.CalledProcessError as err:
            logger.error(f"kaskara-spoon failed:\n{err.output}")
            raise

        # load statements
        filename_statements = os.path.join(container_output_dir, "statements.json")
        statements_dict = json.loads(container.files.read(filename_statements))
        statements = self._load_statements_from_dict(
            container,
            statements_dict,
        )

        # load functions
        filename_functions = os.path.join(container_output_dir, "functions.json")
        functions_dict = json.loads(container.files.read(filename_functions))
        functions = self._load_functions_from_dict(
            container,
            functions_dict,
        )

        # load loops
        filename_loops = os.path.join(container_output_dir, "loops.json")
        loops_dict = json.loads(container.files.read(filename_loops))
        loops = self._load_loops_from_dict(
            container,
            loops_dict,
        )

        # find insertion points
        insertions = statements.insertions()

        return Analysis(
            files=self._project.files,
            loops=loops,
            functions=functions,
            statements=statements,
            insertions=insertions,
        )

    def _load_statements_from_dict(
        self,
        container: ProjectContainer,
        dict_: Sequence[Mapping[str, t.Any]],
    ) -> ProgramStatements:
        """Loads the statement database from a given dictionary."""
        logger.debug("parsing statements database")
        statements = ProgramStatements.build(
            container.project.directory,
            (SpoonStatement.from_dict(d) for d in dict_),
        )
        logger.debug(f"parsed {len(statements)} statements")
        return statements

    def _load_functions_from_dict(
        self,
        container: ProjectContainer,
        dict_: Sequence[Mapping[str, t.Any]],
    ) -> ProgramFunctions:
        """Loads the function database from a given dictionary."""
        logger.debug("parsing function database")
        functions = ProgramFunctions.from_functions(
            container.project.directory,
            (SpoonFunction.from_dict(d) for d in dict_),
        )
        logger.debug(f"parsed {len(functions)} functions")
        return functions

    def _load_loops_from_dict(
        self,
        container: ProjectContainer,
        dict_: Sequence[Mapping[str, t.Any]],
    ) -> ProgramLoops:
        """Loads the loops database from a given dictionary."""
        logger.debug("parsing loop database")
        loop_bodies: list[FileLocationRange] = []
        for loop_info in dict_:
            loc = FileLocationRange.from_string(loop_info["body"])
            loop_bodies.append(loc)
        loops = ProgramLoops.from_body_location_ranges(
            container.project.directory,
            loop_bodies,
        )
        logger.debug("parsed loops")
        return loops
