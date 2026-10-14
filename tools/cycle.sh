#!/bin/bash
# resolve -> refresh -> check -> boot -> missing deps
cd "$(dirname "$0")/.." || exit 1
export PYTHONIOENCODING=utf-8
python tools/resolve_pack.py | head -${1:-8}
(cd pack && ../tools/bin/packwiz.exe refresh | tail -1)
python tools/check_pack.py || exit 1
python tools/server_boot_test.py --timeout 480 2>&1 | cut -c1-300 | tail -${2:-14}
python tools/missing_deps.py
