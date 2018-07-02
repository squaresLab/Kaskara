from typing import List, Optional, FrozenSet

import attr


class Project(object):
    pass

    # probably need access to source?

    # scope checking (where does it start and end?)
    # liveness checking
    # instruction scheduling

    # each file contains a number of scopes
    # - we need to map locations to scopes (scopes can also be virtual)

    # - types
    # - functions
    # - classes
    # - structs

    def determine_typ(self, loc: FileLocationRange) -> Typ:
        """
        Determines the type of an expression at a given location.
        """
        pass

    def determine_defs_reads_writes(self, loc: FileLocationRange) -> Typ:
        pass

    def determine_effects(self, loc: FileLocationRange) -> Effects:
        """
        - defines
        - writes to
        - reads from
        - I/O
        """
        pass

# scopes:
# - global
# - namespace?
# - class
# - function
# - local


@attr.s(frozen=True)
class Typ(object):
    name = attr.ib(type=str)


@attr.s(frozen=True)
class Var(object):
    name = attr.ib(type=str)
    typ = attr.ib(type=Typ)


@attr.s(frozen=True)
class Scope(object):
    parent = attr.ib(type=Optional[Scope], default=None)
    defs = attr.ib(type=FrozenSet[Var], default=frozenset())

    @property
    def vars(self) -> Iterator[Var]:
        """
        Returns an iterator over the variables that are visible from inside
        this scope.
        """


class TypDatabase(object):
    pass


@attr.s(frozen=True)
class Parameter(object):
    name = attr.ib(type=str)
    typ = attr.ib(type=Typ)


@attr.s
class Function(object):
    name = attr.ib(type=str)
    return_type = attr.ib(type=Typ)
    parameters = attr.ib(type=List[Parameter])
    pure = attr.ib(type=bool)
