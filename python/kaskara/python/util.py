# -*- coding: utf-8 -*-
__all__ = ('ast_with_tokens', 'ast_location')

from typing import Sequence, Union
import os

from ..core import Location, FileLocationRange, LocationRange

from loguru import logger
import ast
import asttokens

from ..container import ProjectContainer


def ast_with_tokens(container: ProjectContainer,
                    filename: str
                    ) -> asttokens.ASTTokens:
    """Retrieves the AST (with tokens) for a given file in a container."""
    logger.debug(f'retrieving AST for file [{filename}] '
                 f'in project [{container.project}]')
    assert not os.path.isabs(filename)
    abs_filename = os.path.join(container.project.directory, filename)
    file_contents = container.files.read(abs_filename)
    return asttokens.ASTTokens(file_contents, filename=filename, parse=True)


def ast_location(atok: asttokens.ASTTokens,
                 node: Union[ast.AST, Sequence[ast.AST]]
                 ) -> FileLocationRange:
    """Determines the source location of a node in an AST."""
    # mypy doesn't know that AST nodes are dynamically instrumented to
    # include first_token and last_token
    if isinstance(node, list):
        start_location = ast_location(atok, node[0]).start
        end_location = ast_location(atok, node[-1]).stop
        location_range = LocationRange(start_location, end_location)
        return FileLocationRange(atok._filename, location_range)

    filename = atok._filename
    line_numbers = atok._line_numbers
    offset_start = node.first_token.startpos  # type: ignore
    offset_end = node.last_token.endpos  # type: ignore
    line_start, col_start = line_numbers.offset_to_line(offset_start)
    line_end, col_end = line_numbers.offset_to_line(offset_end)
    location_start = Location(line=line_start, column=col_start)
    location_end = Location(line=line_end, column=col_end)
    location_range = LocationRange(location_start, location_end)
    return FileLocationRange(filename, location_range)
