#!/usr/bin/env python3
"""Announce the Arkhaven server on the local network the same way "Open to LAN" does:
UDP multicast 224.0.2.60:4445, payload "[MOTD]...[/MOTD][AD]port[/AD]" every 1.5 s.
The server then shows up in Multiplayer → "LAN" for everyone on the same network, and the
Arkhaven launcher's discovery step (launcher/Discover.java) finds it automatically.

Usage: lan_announce.py [port=25565] [motd="Arkhaven"]   (no dependencies, Python 3.8+)
"""
import socket
import sys
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 25565
MOTD = sys.argv[2] if len(sys.argv) > 2 else "Arkhaven"
GROUP = ("224.0.2.60", 4445)

payload = f"[MOTD]{MOTD}[/MOTD][AD]{PORT}[/AD]".encode("utf8")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
print(f"announcing {MOTD!r} on port {PORT} to {GROUP[0]}:{GROUP[1]}", flush=True)
while True:
    try:
        sock.sendto(payload, GROUP)
    except OSError as e:  # network briefly down — keep trying
        print("send failed:", e, flush=True)
    time.sleep(1.5)
