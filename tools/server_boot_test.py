#!/usr/bin/env python3
"""Level-2: sync server mods from pack/, boot NeoForge locally (offline, 127.0.0.1 only), wait for Done, stop.
Usage: server_boot_test.py [--timeout 600]. Exit 0 = booted cleanly."""
import re, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
J = next((ROOT / "tools/bin/jre").glob("*/bin/java.exe"))
RUN = ROOT / "tests/server_run"
timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 600
subprocess.run([str(J), "-jar", "pwbs.jar", "-g", "-s", "server", (ROOT / "pack/pack.toml").as_uri()], cwd=RUN, check=True, capture_output=True)
import shutil
sd = RUN / "kubejs/server_scripts"; sd.mkdir(parents=True, exist_ok=True)
for f in (ROOT / "tests/kubejs").glob("*.js"): shutil.copy(f, sd / f.name)
args = ["@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.259/win_args.txt", "nogui"]
log = RUN / "boot.log"
with open(log, "wb") as lf:
    p = subprocess.Popen([str(J), *args], cwd=RUN, stdin=subprocess.PIPE, stdout=lf, stderr=subprocess.STDOUT)
    t0, ok = time.time(), False
    while time.time() - t0 < timeout and p.poll() is None:
        txt = log.read_text("utf8", "replace")
        if re.search(r"Done \(", txt): ok = True; break
        time.sleep(5)
    if p.poll() is None:
        try: p.stdin.write(b"stop\n"); p.stdin.flush()
        except Exception: pass
        try: p.wait(120)
        except Exception: p.kill()
txt = log.read_text("utf8", "replace")
print("BOOT", "OK" if ok else "FAILED", f"{time.time()-t0:.0f}s")
bad = [l for l in txt.splitlines() if re.search(r"/(ERROR|FATAL)\]|Mixin apply failed|Missing registry|Exception", l)]
for l in bad[:40]: print("  ", l[:300])
print(f"{len(bad)} suspicious lines")
sys.exit(0 if ok else 1)
