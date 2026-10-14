#!/usr/bin/env python3
"""Announce the Arkhaven server on the local network the same way "Open to LAN" does:
UDP multicast 224.0.2.60:4445, payload "[MOTD]...[/MOTD][AD]port[/AD]" every 1.5 s.
The server then shows up in Multiplayer → "LAN" for everyone on the same network, and the
Arkhaven launcher's discovery step (launcher/Discover.java) finds it automatically.
Sends on every IPv4 interface (home network and ZeroTier alike), re-read every minute.

Usage: lan_announce.py [port=25565] [motd="Arkhaven"]   (no dependencies, Python 3.8+)
"""
import socket
import subprocess
import sys
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 25565
MOTD = sys.argv[2] if len(sys.argv) > 2 else "Arkhaven"
GROUP = ("224.0.2.60", 4445)


def local_ipv4():
    """IPv4 addresses of all non-loopback interfaces (Linux `ip`; falls back to the default route)."""
    try:
        out = subprocess.run(["ip", "-o", "-4", "addr", "show", "up"], capture_output=True, text=True, timeout=5).stdout
        ips = [line.split()[3].split("/")[0] for line in out.splitlines()]
        ips = [ip for ip in ips if not ip.startswith("127.") and not ip.startswith("172.17.")]  # skip docker0
        if ips:
            return ips
    except (OSError, IndexError, subprocess.SubprocessError):
        pass
    return [None]


def make_socket(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    if ip:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
    return s


payload = f"[MOTD]{MOTD}[/MOTD][AD]{PORT}[/AD]".encode("utf8")
socks, refreshed = {}, 0.0
while True:
    if time.time() - refreshed > 60:
        ips = local_ipv4()
        for ip in list(socks):
            if ip not in ips:
                socks.pop(ip).close()
        for ip in ips:
            if ip not in socks:
                try:
                    socks[ip] = make_socket(ip)
                    print(f"announcing {MOTD!r} port {PORT} via {ip or 'default'}", flush=True)
                except OSError as e:
                    print("socket failed:", ip, e, flush=True)
        refreshed = time.time()
    for ip, s in socks.items():
        try:
            s.sendto(payload, GROUP)
        except OSError:  # interface briefly down — keep trying
            pass
    time.sleep(1.5)
