from __future__ import annotations

__all__ = ("ClangAnalyser",)

import contextlib
import json
import os
import typing as t
from dataclasses import dataclass, field
from typing import Any

import dockerblade as _dockerblade
from loguru import logger
from overrides import overrides

from kaskara.analyser import Analyser
from kaskara.analysis import Analysis
from kaskara.clang.analysis import ClangFunction, ClangStatement
from kaskara.core import FileLocationRange
from kaskara.exceptions import KaskaraException
from kaskara.functions import ProgramFunctions
from kaskara.loops import ProgramLoops
from kaskara.statements import ProgramStatements
from kaskara.util import abs_to_rel_flocrange

if t.TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from kaskara.container import ProjectContainer
    from kaskara.project import Project

PATH_KASKARA_CLANG = "/opt/kaskara/scripts/kaskara-clang"


@dataclass
class ClangAnalyser(Analyser):
    _project: Project
    _container: ProjectContainer
    _workdir: str | None = field(default=None)

    @classmethod
    @contextlib.contextmanager
    @overrides
    def for_project(cls, project: Project) -> t.Iterator[t.Self]:
        with project.provision() as container:
            yield cls(project, container)

    @overrides
    def run(self) -> Analysis:
        loops = self._find_loops()
        functions = self._find_functions()
        statements = self._find_statements()
        insertions = statements.insertions()
        return Analysis(
            files=self._project.files,
            loops=loops,
            functions=functions,
            statements=statements,
            insertions=insertions,
        )

    def _execute_command(
        self,
        command_args: list[str],
        output_filename: str,
    ) -> t.Any:  # noqa: ANN401
        container = self._container
        project = self._project
        workdir = project.directory

        driver = PATH_KASKARA_CLANG
        assert os.path.isabs(driver)
        if not container.files.exists(driver):
            error_message = f"driver {driver} does not exist"
            raise KaskaraException(error_message)

        if not os.path.isabs(output_filename):
            output_filename = os.path.join(workdir, output_filename)

        # determine the type of the analysis from the first argument
        analysis_name = command_args[0]
        command_args = [driver, *command_args, "2>&1"]
        command = " ".join(command_args)

        logger.debug(f"executing {analysis_name} [{workdir}]: {command}")

        maybe_output: str | None = None
        maybe_error_message: str | None = None
        maybe_error: Exception | None = None
        try:
            maybe_output = container.shell.check_output(command, cwd=workdir, text=True)
        except _dockerblade.CalledProcessError as err:
            maybe_error = err
            err_message = err.output
            assert isinstance(err_message, str)
            maybe_error_message = f"failed with exit code {err.returncode}: {err_message}"

        if maybe_output:
            logger.debug(f"{analysis_name} output:\n{maybe_output}")

        analysis_completed = container.files.exists(output_filename)

        if not analysis_completed:
            message = f"{analysis_name}: failed to produce output"
            if maybe_error:
                message = f"{message}: {maybe_error_message}"
                raise KaskaraException(message) from maybe_error
            raise KaskaraException(message)

        if analysis_completed and maybe_error_message:
            message = f"{analysis_name}: completed with errors:\n{maybe_error_message}"
            logger.warning(message)

        output = container.files.read(output_filename)
        return json.loads(output)

    def _find_statements(self) -> ProgramStatements:
        project = self._project
        logger.debug(f"finding statements for project: {project}")

        command_args = ["statements"]
        command_args += sorted(project.files)
        output_filename = "statements.json"

        output_jsn: Sequence[Mapping[str, Any]] = self._execute_command(
            command_args=command_args,
            output_filename=output_filename,
        )
        statements = ProgramStatements.build(
            project.directory,
            (ClangStatement.from_dict(project, d) for d in output_jsn),
        )
        logger.debug("finished reading results")
        return statements

    def _find_loops(self) -> ProgramLoops:
        project = self._project
        command_args = ["loops"]
        command_args += sorted(project.files)
        output_filename = "loops.json"

        output_jsn = self._execute_command(
            command_args=command_args,
            output_filename=output_filename,
        )

        return self._read_loops_from_jsn(output_jsn)

    def _read_loops_from_jsn(
        self,
        jsn: Sequence[Mapping[str, str]],
    ) -> ProgramLoops:
        project = self._project
        loop_bodies: list[FileLocationRange] = []
        for loop_info in jsn:
            loc = FileLocationRange.from_string(loop_info["body"])
            loc = abs_to_rel_flocrange(project.directory, loc)
            loop_bodies.append(loc)
        logger.debug("finished reading loop analysis results")
        return ProgramLoops.from_body_location_ranges(
            project.directory,
            loop_bodies,
        )

    def _find_functions(self) -> ProgramFunctions:
        project = self._project
        output_filename = "functions.json"
        command_args = ["functions"]
        command_args += sorted(project.files)

        output_jsn = self._execute_command(
            command_args=command_args,
            output_filename=output_filename,
        )

        return ProgramFunctions.from_functions(
            project_directory=project.directory,
            functions=(ClangFunction.from_dict(project, d) for d in output_jsn),
        )
