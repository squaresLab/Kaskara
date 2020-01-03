# -*- coding: utf-8 -*-
__all__ = ('ClangFunction', 'ClangStatement')

from typing import Any, FrozenSet, Mapping

import attr

from ..core import FileLocationRange
from ..functions import Function
from ..project import Project
from ..statements import Statement
from ..util import abs_to_rel_flocrange


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ClangFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange
    return_type: str
    is_global: bool
    is_pure: bool

    @staticmethod
    def from_dict(project: Project, d: Mapping[str, Any]) -> 'ClangFunction':
        name = d['name']
        location = FileLocationRange.from_string(d['location'])
        location = abs_to_rel_flocrange(project.directory, location)
        body = FileLocationRange.from_string(d['body'])
        body = abs_to_rel_flocrange(project.directory, body)
        return_type = d['return-type']
        is_global = d['global']
        is_pure = d['pure']
        return ClangFunction(name=name,
                             location=location,
                             body_location=body,
                             return_type=return_type,
                             is_global=is_global,
                             is_pure=is_pure)


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ClangStatement(Statement):
    content: str
    canonical: str
    kind: str
    location: FileLocationRange
    reads: FrozenSet[str]
    writes: FrozenSet[str]
    visible: FrozenSet[str]
    declares: FrozenSet[str]
    live_before: FrozenSet[str]
    requires_syntax: FrozenSet[str]

    @staticmethod
    def from_dict(project: Project, d: Mapping[str, Any]) -> 'ClangStatement':
        location = FileLocationRange.from_string(d['location'])
        location = abs_to_rel_flocrange(project.directory, location)
        return ClangStatement(d['content'],
                              d['canonical'],
                              d['kind'],
                              location,
                              frozenset(d.get('reads', [])),
                              frozenset(d.get('writes', [])),
                              frozenset(d.get('visible', [])),
                              frozenset(d.get('decls', [])),
                              frozenset(d.get('live_before', [])),
                              frozenset(d.get('requires_syntax', [])))
