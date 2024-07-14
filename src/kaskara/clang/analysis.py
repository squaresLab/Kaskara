from __future__ import annotations

__all__ = ("ClangFunction", "ClangStatement")

import typing as t

import attr
from loguru import logger
from overrides import overrides

from kaskara.core import FileLocationRange
from kaskara.functions import Function
from kaskara.statements import Statement
from kaskara.util import abs_to_rel_flocrange

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from kaskara.project import Project


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ClangFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange
    return_type: str
    is_global: bool
    is_pure: bool

    @overrides
    def with_relative_locations(self, base: str) -> t.Self:
        return attr.evolve(
            self,
            location=self.location.with_relative_location(base),
            body_location=self.body_location.with_relative_location(base),
        )

    @overrides
    def to_dict(self) -> dict[str, t.Any]:
        return {
            "name": self.name,
            "location": str(self.location),
            "body": str(self.body_location),
            "return-type": self.return_type,
            "global": self.is_global,
            "pure": self.is_pure,
        }

    @classmethod
    def from_dict(
        cls,
        project: Project,
        d: Mapping[str, t.Any],
    ) -> t.Self:
        name = d["name"]
        location = FileLocationRange.from_string(d["location"])
        location = abs_to_rel_flocrange(project.directory, location)
        body = FileLocationRange.from_string(d["body"])
        body = abs_to_rel_flocrange(project.directory, body)
        return_type = d["return-type"]
        is_global = d["global"]
        is_pure = d["pure"]
        return cls(
            name=name,
            location=location,
            body_location=body,
            return_type=return_type,
            is_global=is_global,
            is_pure=is_pure,
        )


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ClangStatement(Statement):
    content: str
    canonical: str = attr.ib(repr=False)
    kind: str = attr.ib(repr=False)
    location: FileLocationRange
    reads: frozenset[str] = attr.ib(repr=False)
    writes: frozenset[str] = attr.ib(repr=False)
    visible: frozenset[str] = attr.ib(repr=False)
    declares: frozenset[str] = attr.ib(repr=False)
    live_before: frozenset[str] = attr.ib(repr=False)
    live_after: frozenset[str] = attr.ib(repr=False)
    requires_syntax: frozenset[str] = attr.ib(repr=False)

    @overrides
    def with_relative_locations(self, base: str) -> t.Self:
        return attr.evolve(
            self,
            location=self.location.with_relative_location(base),
        )

    @overrides
    def to_dict(self) -> dict[str, t.Any]:
        return {
            "content": self.content,
            "canonical": self.canonical,
            "kind": self.kind,
            "location": str(self.location),
            "reads": list(self.reads),
            "writes": list(self.writes),
            "visible": list(self.visible),
            "decls": list(self.declares),
            "live_before": list(self.live_before),
            "live_after": list(self.live_after),
            "requires_syntax": list(self.requires_syntax),
        }

    @classmethod
    def from_dict(
        cls,
        project: Project,
        d: Mapping[str, t.Any],
    ) -> t.Self:
        location = FileLocationRange.from_string(d["location"])
        location = abs_to_rel_flocrange(project.directory, location)
        statement = cls(
            content=d["content"],
            canonical=d["canonical"],
            kind=d["kind"],
            location=location,
            reads=frozenset(d.get("reads", [])),
            writes=frozenset(d.get("writes", [])),
            visible=frozenset(d.get("visible", [])),
            declares=frozenset(d.get("decls", [])),
            live_before=frozenset(d.get("live_before", [])),
            live_after=frozenset(d.get("live_after", [])),
            requires_syntax=frozenset(d.get("requires_syntax", [])),
        )
        logger.trace(f"loaded statement: {statement}")
        return statement
