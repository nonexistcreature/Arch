#!/usr/bin/env python3
"""Download vanilla assets for a version json into <mcdir>/assets (8 threads, retries). Usage: fetch_assets.py MCDIR VERSION"""
import concurrent.futures, hashlib, json, sys, urllib.request
from pathlib import Path
mc, ver = Path(sys.argv[1]), sys.argv[2]
vj = json.loads((mc / "versions" / ver / f"{ver}.json").read_text())
idx = vj["assetIndex"]
ip = mc / "assets/indexes" / f"{idx['id']}.json"
ip.parent.mkdir(parents=True, exist_ok=True)
if not ip.exists(): urllib.request.urlretrieve(idx["url"], ip)
objs = json.loads(ip.read_text())["objects"]
def get(h):
    p = mc / "assets/objects" / h[:2] / h
    if p.exists(): return 0
    p.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(5):
        try:
            data = urllib.request.urlopen(f"https://resources.download.minecraft.net/{h[:2]}/{h}", timeout=30).read()
            if hashlib.sha1(data).hexdigest() == h: p.write_bytes(data); return 1
        except Exception: pass
    return -1
with concurrent.futures.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, {o["hash"] for o in objs.values()}))
print("downloaded", res.count(1), "failed", res.count(-1), "total", len(res))
