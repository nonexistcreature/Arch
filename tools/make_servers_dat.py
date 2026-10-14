#!/usr/bin/env python3
"""Write pack/servers.dat (NBT, uncompressed) with the Arkhaven entry: make_servers_dat.py HOST[:PORT]"""
import struct, sys
from pathlib import Path
host = sys.argv[1] if len(sys.argv) > 1 else "arkhaven.example.invalid"
def s(x): b = x.encode(); return struct.pack(">H", len(b)) + b
def tag(t, name, payload): return bytes([t]) + s(name) + payload
entry = (tag(8, "ip", s(host)) + tag(8, "name", s("Arkhaven")) + tag(1, "hidden", b"\0") + b"\0")
servers = tag(9, "servers", bytes([10]) + struct.pack(">i", 1) + entry)
data = bytes([10]) + s("") + servers + b"\0"
Path(__file__).resolve().parent.parent.joinpath("pack/servers.dat").write_bytes(data)
print("servers.dat ->", host)
