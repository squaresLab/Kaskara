from __future__ import annotations

__all__ = ("PythonFunction", "PythonStatement")

import typing as t

import attr
from overrides import overrides

from kaskara.functions import Function
from kaskara.statements import Statement

if t.TYPE_CHECKING:
    from kaskara.core import FileLocationRange


@attr.s(frozen=True, auto_attribs=True, slots=True)
class PythonFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange

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
        }

    @property
    def return_type(self) -> str | None:
        return None


@attr.s(frozen=True, auto_attribs=True, slots=True)
class PythonStatement(Statement):
    kind: str
    content: str
    canonical: str
    location: FileLocationRange

    @overrides
    def with_relative_locations(self, base: str) -> PythonStatement:
        return attr.evolve(
            self,
            location=self.location.with_relative_location(base),
        )

    @overrides
    def to_dict(self) -> dict[str, t.Any]:
        return {
            "kind": self.kind,
            "source": self.content,
            "canonical": self.canonical,
            "location": str(self.location),
        }

    @property
    def visible(self) -> frozenset[str] | None:
        return None
