from typing import FrozenSet, Dict, Any, List, Iterator
import json
import attr
import logging

from bugzoo.util import indent
from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocationRange

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True)
class Statement(object):
    content = attr.ib(type=str)
    location = attr.ib(type=FileLocationRange)
    reads = attr.ib(type=FrozenSet[str])
    writes = attr.ib(type=FrozenSet[str])

    @staticmethod
    def from_dict(d: Dict[str, Any], snapshot: Snapshot) -> 'Statement':
        # FIXME
        location = FileLocationRange.from_string(d['location'])
        location = abs_to_rel_flocrange(snapshot.source_dir, location)
        return Statement(d['content'],
                         location,
                         frozenset(d['reads']),
                         frozenset(d['writes']))

    def to_dict(self, snapshot: Snapshot) -> Dict[str, Any]:
        loc = rel_to_abs_flocrange(snapshot.source_dir, self.location)
        return {'content': self.content,
                'location': str(loc),
                'reads': [v for v in self.reads],
                'writes': [v for v in self.writes]}


class StatementDB(object):
    @staticmethod
    def build(client_bugzoo: BugZooClient,
              snapshot: Snapshot,
              files: List[str],
              container: Container
              ) -> 'StatementDB':
        out_fn = "statements.json"
        logger.debug("building statement database for snapshot [%s]",
                     snapshot.name)
        logger.debug("fetching statements from files: %s", ', '.join(files))

        cmd = "kaskara-statement-finder {}".format(' '.join(files))
        workdir = snapshot.source_dir
        logger.debug("executing statement finder [%s]: %s", workdir, cmd)
        outcome = client_bugzoo.containers.exec(container, cmd, context=workdir)
        logger.debug("executed statement finder [%d]:\n%s",
                     outcome.code, indent(outcome.output, 2))

        if outcome.code != 0:
            msg = "kaskara-statement-finder exited with non-zero code: {}"
            msg = msg.format(outcome.code)
            raise BondException(msg)  # FIXME

        logger.debug("reading statement analysis results from file: %s", out_fn)
        output = client_bugzoo.files.read(container, out_fn)
        jsn = json.loads(output)  # type: List[Dict[str, Any]]
        db = StatementDB.from_dict(jsn)
        logger.debug("finished reading statement analysis results")
        return db

    @staticmethod
    def from_file(fn: str) -> 'StatementDB':
        logger.debug("reading statement database from file: %s", fn)
        with open(fn, 'r') as f:
            d = json.load(f)
        db = StatementDB.from_dict(d)
        logger.debug("read statement database from file: %s", fn)
        return db

    @staticmethod
    def from_dict(d: List[Dict[str, Any]],
                  snapshot: Snapshot
                  ) -> 'StatementDB':
        statements = [Statement.from_dict(dd, snapshot) for dd in d]
        return StatementDB(statements)

    def __init__(self, statements: List[Statement]) -> None:
        self.__statements = statements

    def __iter__(self) -> Iterator[Statement]:
        yield from self.__statements

    def to_dict(self, snapshot: Snapshot) -> List[Dict[str, Any]]:
        return [stmt.to_dict(snapshot) for stmt in self.__statements]

    def to_file(self, fn: str, snapshot: Snapshot) -> None:
        logger.debug("writing statement database to file: %s", fn)
        d = self.to_dict(snapshot)
        with open(fn, 'w') as f:
            json.dump(d, f)
        logger.debug("wrote statement database to file: %s", fn)
