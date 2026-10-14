#!/usr/bin/env python3
"""Serve pack/ over http://127.0.0.1:8765 (big listen backlog; packwiz-installer is highly parallel)."""
import functools, http.server, sys
from pathlib import Path
class S(http.server.ThreadingHTTPServer):
    request_queue_size = 512
    daemon_threads = True
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
root = Path(__file__).resolve().parent.parent / "pack"
S(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8765), functools.partial(H, directory=str(root))).serve_forever()
