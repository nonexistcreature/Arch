#!/usr/bin/env python3
"""Pre-generate the test world around spawn so client benchmarks don't measure world generation.
Temporarily adds Chunky and removes Distant Horizons (they crash together) in tests/server_run only.
Usage: pregen_test_world.py [radius=320]"""
import shutil, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "tests/server_run"
J = next((ROOT / "tools/bin/jre").glob("*/bin/java.exe"))
RADIUS = int(sys.argv[1]) if len(sys.argv) > 1 else 320
CHUNKY = "https://cdn.modrinth.com/data/fALzjamp/versions/LuFhm4eU/Chunky-NeoForge-1.4.23.jar"

mods = RUN / "mods"
chunky = mods / "Chunky-NeoForge-1.4.23.jar"
urllib.request.urlretrieve(CHUNKY, chunky)
parked = RUN / "parked"
parked.mkdir(exist_ok=True)
dh = list(mods.glob("DistantHorizons*.jar"))
for f in dh:
    shutil.move(str(f), parked / f.name)
log = RUN / "pregen.log"
try:
    with open(log, "wb") as lf:
        p = subprocess.Popen([str(J), "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.259/win_args.txt", "nogui"],
                             cwd=RUN, stdin=subprocess.PIPE, stdout=lf, stderr=subprocess.STDOUT)
        while "Done (" not in log.read_text("utf8", "replace"):
            if p.poll() is not None:
                sys.exit("server died")
            time.sleep(3)
        for c in ["chunky world minecraft:overworld", "chunky center 0 0", f"chunky radius {RADIUS}", "chunky start"]:
            p.stdin.write((c + "\n").encode()); p.stdin.flush(); time.sleep(2)
        t0 = time.time()
        while time.time() - t0 < 1500:
            txt = log.read_text("utf8", "replace")
            if "Task finished for minecraft:overworld" in txt or "task finished" in txt.lower():
                break
            time.sleep(10)
        print(f"pregen took {time.time() - t0:.0f}s")
        p.stdin.write(b"stop\n"); p.stdin.flush()
        p.wait(180)
finally:
    chunky.unlink(missing_ok=True)
    for f in parked.glob("*.jar"):
        shutil.move(str(f), mods / f.name)
