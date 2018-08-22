import os

from .core import FileLocationRange, FileLocation


def abs_to_rel_filename(prefix: str, filename: str) -> str:
    if prefix[-1] != '/':
        prefix = prefix + '/'
    assert filename.startswith(prefix)
    return filename[len(prefix):]


def abs_to_rel_floc(prefix: str, l: FileLocation) -> FileLocation:
    return FileLocation(abs_to_rel_filename(prefix, l.filename),
                        l.location)


def rel_to_abs_floc(prefix: str, l: FileLocation) -> FileLocation:
    return FileLocation(os.path.join(prefix, l.filename), l.location)


def abs_to_rel_flocrange(prefix: str,
                         l: FileLocationRange
                         ) -> FileLocationRange:
    return FileLocationRange(abs_to_rel_filename(prefix, l.filename),
                             l.location_range)

def rel_to_abs_flocrange(prefix: str,
                         l: FileLocationRange
                         ) -> FileLocationRange:
    return FileLocationRange(os.path.join(prefix, l.filename),
                             l.location_range)
