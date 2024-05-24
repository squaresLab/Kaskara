__all__ = ("ClangFunction", "ClangStatement")

from collections.abc import Mapping
from typing import Any

import attr
from loguru import logger

from kaskara.core import FileLocationRange
from kaskara.functions import Function
from kaskara.project import Project
from kaskara.statements import Statement
from kaskara.util import abs_to_rel_flocrange


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ClangFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange
    return_type: str
    is_global: bool
    is_pure: bool

    @staticmethod
    def from_dict(project: Project, d: Mapping[str, Any]) -> "ClangFunction":
        name = d["name"]
        location = FileLocationRange.from_string(d["location"])
        location = abs_to_rel_flocrange(project.directory, location)
        body = FileLocationRange.from_string(d["body"])
        body = abs_to_rel_flocrange(project.directory, body)
        return_type = d["return-type"]
        is_global = d["global"]
        is_pure = d["pure"]
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
    reads: frozenset[str]
    writes: frozenset[str]
    visible: frozenset[str]
    declares: frozenset[str]
    live_before: frozenset[str]
    live_after: frozenset[str]
    requires_syntax: frozenset[str]

    @staticmethod
    def from_dict(project: Project, d: Mapping[str, Any]) -> "ClangStatement":
        location = FileLocationRange.from_string(d["location"])
        location = abs_to_rel_flocrange(project.directory, location)
        statement = ClangStatement(d["content"],
                                   d["canonical"],
                                   d["kind"],
                                   location,
                                   frozenset(d.get("reads", [])),
                                   frozenset(d.get("writes", [])),
                                   frozenset(d.get("visible", [])),
                                   frozenset(d.get("decls", [])),
                                   frozenset(d.get("live_before", [])),
                                   frozenset(d.get("live_after", [])),
                                   frozenset(d.get("requires_syntax", [])))
        logger.debug(f"loaded statement: {statement}")
        return statement
