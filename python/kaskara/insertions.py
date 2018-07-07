from typing import FrozenSet, Iterable, Iterator

import attr
from bugzoo.core.location import FileLocationRange


@attr.s(frozen=True)
class InsertionPoint(object):
    location = attr.ib(type=FileLocationRange)
    visible = attr.ib(type=FrozenSet[str])

    @staticmethod
    def from_dict(d: Dict[str, str]) -> 'InsertionPoint':
        location = FileLocationRange.from_string(d['location'])
        visible = frozenset(d['visible'])
        return InsertionPoint(location, visible)

    def to_dict(self) -> Dict[str, str]:
        return {'location': str(self.location),
                'visible': [sym for sym in self.visible]}


class InsertionPointDatabase(Iterable[InsertionPoint]):
    def __init__(self, contents: List[InsertionPoint]) -> None:
        self.__contents = contents

    @staticmethod
    def from_dict(d: List[Dict[str, str]]) -> 'InsertionPointDatabase':
        contents = [InsertionPoint.from_dict(dd) for dd in d]
        return InsertionPointDatabase(contents)

    def __iter__(self) -> Iterator[InsertionPoint]:
        yield from self.__contents
