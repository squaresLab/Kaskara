# -*- coding: utf-8 -*-
__all__ = ('SpoonStatement',)

from typing import Any, FrozenSet, Mapping, Optional

import attr

from ..core import FileLocationRange
from ..statements import Statement


@attr.s(frozen=True, auto_attribs=True, slots=True)
class SpoonStatement(Statement):
    kind: str
    content: str
    canonical: str
    location: FileLocationRange

    @staticmethod
    def from_dict(dict_: Mapping[str, Any]) -> 'SpoonStatement':
        kind: str = dict_['kind']
        content: str = dict_['source']
        canonical: str = dict_['canonical']
        location = FileLocationRange.from_string(dict_['location'])
        return SpoonStatement(kind, content, canonical, location)

    @property
    def visible(self) -> Optional[FrozenSet[str]]:
        return None
