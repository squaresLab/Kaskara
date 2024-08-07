import os

import docker as _docker
import dockerblade as _dockerblade
import pytest

import kaskara
from kaskara.core import FileLine
from kaskara.functions import ProgramFunctions
from kaskara.loops import ProgramLoops
from kaskara.statements import ProgramStatements

DIR_HERE = os.path.dirname(__file__)


@pytest.fixture()
def flask():
    docker_url: str = os.environ.get("DOCKER_HOST")
    docker = _docker.from_env()
    docker_image_name = "kaskara/examples:flask"
    docker_directory = os.path.join(DIR_HERE, "examples/flask")

    docker.images.build(
        path=docker_directory,
        tag=docker_image_name,
        rm=True,
    )

    with _dockerblade.DockerDaemon(docker_url) as dockerblade:
        files = {
            "flask/signals.py",
            "flask/helpers.py",
        }
        yield kaskara.Project(
            dockerblade=dockerblade,
            image=docker_image_name,
            directory="/opt/flask/src",
            files=files,
        )


def test_collect_statements(flask):
    def line(num: int) -> FileLine:
        return FileLine("flask/signals.py", num)

    with flask.provision() as container:
        filename = "flask/signals.py"
        visitor = kaskara.python.statements.CollectStatementsVisitor(container)
        visitor.collect(filename)
        statements = ProgramStatements.build(
            container.project.directory,
            visitor.statements,
        )

        statements_at_line = list(statements.at_line(line(21)))
        assert len(statements_at_line) == 1
        actual = statements_at_line[0]
        assert actual.content == "return _FakeSignal(name, doc)"


def test_collect_functions(flask):
    with flask.provision() as container:
        filename = "flask/signals.py"
        visitor = kaskara.python.functions.CollectFunctionsVisitor(container)
        visitor.collect(filename)
        functions = ProgramFunctions.from_functions(
            project_directory=container.project.directory,
            functions=visitor.functions,
        )

        assert len(functions) == 4
        assert set(f.name for f in functions) == {
            "signal",
            "__init__",
            "send",
            "_fail",
        }


def test_collect_loops(flask):
    with flask.provision() as container:
        filename = "flask/helpers.py"
        visitor = kaskara.python.loops.CollectLoopsVisitor(container)
        visitor.collect(filename)
        loops = ProgramLoops.from_body_location_ranges(
            container.project.directory,
            visitor.locations,
        )
        body_locations = list(loops._covered_by_loop_bodies)

        assert len(body_locations) == 3
