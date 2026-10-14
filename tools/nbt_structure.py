#!/usr/bin/env python3
"""Minimal vanilla structure NBT writer (gzip): an n*n*n box of air with a stone floor. Used for the GameTest template."""
import gzip
import struct
from pathlib import Path

END = b"\x00"


def _s(x):
    b = x.encode()
    return struct.pack(">H", len(b)) + b


def _tag(t, name, payload):
    return bytes([t]) + _s(name) + payload


def _i(v):
    return struct.pack(">i", v)


def _ilist(vals):
    return bytes([3]) + _i(len(vals)) + b"".join(_i(v) for v in vals)


def write_empty_structure(path: Path, n: int):
    palette = bytes([10]) + _i(2) + _tag(8, "Name", _s("minecraft:air")) + END + _tag(8, "Name", _s("minecraft:stone")) + END
    blocks, count = b"", 0
    for x in range(n):
        for z in range(n):
            blocks += _tag(9, "pos", _ilist([x, 0, z])) + _tag(3, "state", _i(1)) + END
            count += 1
    blocks = bytes([10]) + _i(count) + blocks
    root = (_tag(3, "DataVersion", _i(3955)) + _tag(9, "size", _ilist([n, n, n])) + _tag(9, "palette", palette)
            + _tag(9, "blocks", blocks) + _tag(9, "entities", bytes([10]) + _i(0)))
    data = bytes([10]) + _s("") + root + END
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(data))
