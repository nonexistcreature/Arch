#!/usr/bin/env python3
"""End-to-end test (docs/08_TESTING.md levels 4–5): local offline server + real client that joins it,
then scripted console commands while the player is online. 127.0.0.1 only, online-mode=false.

Usage: e2e_test.py [--hold 240] [--cmds "cmd1;cmd2;..."]
Default commands exercise arkhaven-core (forecast, rift, shower, strike) and FTB Teams.
Writes tests/out/e2e.log (server console) and prints a short verdict.
"""
import re, subprocess, sys, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
J = next((ROOT / "tools/bin/jre").glob("*/bin/java.exe"))
RUN = ROOT / "tests/server_run"
args = sys.argv[1:]
HOLD = int(args[args.index("--hold") + 1]) if "--hold" in args else 240
DEFAULT = [
    "op ArkhavenTest", "arkhaven status", "arkhaven forecast", "arkhaven zone",
    "execute as ArkhavenTest run arkhaven zone",
    "arkhaven event rift ArkhavenTest", "arkhaven event shower", "arkhaven event strike ArkhavenTest",
    "ftbteams list", "arkhaven kit demo ArkhavenTest", "arkhaven status",
]
CMDS = args[args.index("--cmds") + 1].split(";") if "--cmds" in args else DEFAULT


def main():
    subprocess.run([str(J), "-jar", "pwbs.jar", "-g", "-s", "server", (ROOT / "pack/pack.toml").as_uri()], cwd=RUN, check=True, capture_output=True)
    import shutil
    cs = ROOT / "tests/client_run/game/kubejs/client_scripts"; cs.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "tests/kubejs_client/zz_screenshot_probe.js", cs / "zz_screenshot_probe.js")
    log = RUN / "boot.log"
    lf = open(log, "wb")
    srv = subprocess.Popen([str(J), "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.259/win_args.txt", "nogui"],
                           cwd=RUN, stdin=subprocess.PIPE, stdout=lf, stderr=subprocess.STDOUT)
    t0 = time.time()
    while "Done (" not in log.read_text("utf8", "replace"):
        if srv.poll() is not None or time.time() - t0 > 600:
            print("SERVER FAILED TO START"); sys.exit(1)
        time.sleep(3)
    print(f"server up in {time.time() - t0:.0f}s")
    client = subprocess.Popen([sys.executable, str(ROOT / "tools/launch_client.py"), "--join", "127.0.0.1:25565", "--hold", str(HOLD), "--timeout", "900"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf8", errors="replace")
    out = []
    threading.Thread(target=lambda: out.extend(client.stdout), daemon=True).start()
    t1 = time.time()
    joined = False
    while time.time() - t1 < 900 and client.poll() is None:
        if re.search(r"ArkhavenTest joined the game", log.read_text("utf8", "replace")):
            joined = True
            break
        time.sleep(3)
    print("client joined:", joined)
    if joined:
        time.sleep(20)
        for c in CMDS:
            srv.stdin.write((c + "\n").encode()); srv.stdin.flush()
            time.sleep(4)
        time.sleep(5)
        if "--quests" in args:  # open the quest book; the in-game probe (tests/kubejs_client) takes the screenshot
            srv.stdin.write(b"ftbquests open_book ArkhavenTest\n"); srv.stdin.flush()
            time.sleep(15)
        time.sleep(int(args[args.index("--after") + 1]) if "--after" in args else 60)
    client.wait()
    srv.stdin.write(b"stop\n"); srv.stdin.flush()
    try:
        srv.wait(120)
    except subprocess.TimeoutExpired:
        srv.kill()
    lf.close()
    txt = log.read_text("utf8", "replace")
    (ROOT / "tests/out").mkdir(exist_ok=True)
    (ROOT / "tests/out/e2e.log").write_text(txt, "utf8")
    print("".join(out[-5:]))
    for pat in ["joined the game", "Event rift started", "Event shower started", "Event strike started", "Meteor .* impact",
                "Demo kit", "Выдан демо", "lost connection", "Exception"]:
        hits = [l for l in txt.splitlines() if re.search(pat, l)]
        print(f"{pat!r}: {len(hits)}", (hits[0][:200] if hits else ""))
    sys.exit(0 if joined else 1)


if __name__ == "__main__":
    main()
