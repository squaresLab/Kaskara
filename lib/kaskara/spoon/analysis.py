# -*- coding: utf-8 -*-
__all__ = ('SpoonStatement',)

from typing import Any, FrozenSet, Mapping, Optional

import attr

from ..core import FileLocationRange
from ..functions import Function
from ..statements import Statement


@attr.s(frozen=True, slots=True, auto_attribs=True)
class SpoonFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange
    return_type: str

    @staticmethod
    def from_dict(dict_: Mapping[str, Any]) -> 'SpoonFunction':
        name: str = dict_['name']
        location = FileLocationRange.from_string(dict_['location'])
        body_location = FileLocationRange.from_string(dict_['body'])
        return_type = dict_['return-type']
        return SpoonFunction(name, location, body_location, return_type)


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
