# -*- coding: utf-8 -*-
import os

from .core import FileLocationRange, FileLocation


def abs_to_rel_filename(prefix: str, filename: str) -> str:
    if prefix[-1] != '/':
        prefix = prefix + '/'
    assert filename.startswith(prefix)
    return filename[len(prefix):]


def abs_to_rel_floc(prefix: str, location: FileLocation) -> FileLocation:
    return FileLocation(abs_to_rel_filename(prefix, location.filename),
                        location.location)


def rel_to_abs_floc(prefix: str, location: FileLocation) -> FileLocation:
    return FileLocation(os.path.join(prefix, location.filename),
                        location.location)


def abs_to_rel_flocrange(prefix: str,
                         location: FileLocationRange
                         ) -> FileLocationRange:
    return FileLocationRange(abs_to_rel_filename(prefix, location.filename),
                             location.location_range)


def rel_to_abs_flocrange(prefix: str,
                         location: FileLocationRange
                         ) -> FileLocationRange:
    return FileLocationRange(os.path.join(prefix, location.filename),
                             location.location_range)
