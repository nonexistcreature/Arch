#!/usr/bin/env python3
"""Client FPS benchmark (docs/08_TESTING.md level 6, client side).
Runs the real client in singleplayer on a copy of the test world at a fixed spot and reports FPS.

Usage: bench_client.py VARIANT [VARIANT ...]     (see VARIANTS below)
Each variant = options.txt overrides + iris.properties + JVM args + mods to disable.
Results are appended to docs/reports/performance.md.
"""
import json, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "tests/client_run/game"
WORLD_SRC = ROOT / "tests/server_run/world"
RES = "2560x1377"  # the owner's maximised window

G1 = "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=37 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=16M -XX:G1ReservePercent=20 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:+AlwaysPreTouch"
ZGC = "-XX:+UseZGC -XX:+ZGenerational -XX:+AlwaysPreTouch -XX:+DisableExplicitGC"

VARIANTS = {
    # name: (options overrides, shaders on?, shader profile options, jvm, disabled mod globs)
    "baseline":      ({"renderDistance": 12}, True, {}, "-Xmx6G", []),
    "mem10_g1":      ({"renderDistance": 12}, True, {}, "-Xms10G -Xmx10G " + G1, []),
    "mem10_zgc":     ({"renderDistance": 12}, True, {}, "-Xms10G -Xmx10G " + ZGC, []),
    "noshader":      ({"renderDistance": 12}, False, {}, "-Xms10G -Xmx10G " + ZGC, []),
    "no_dh":         ({"renderDistance": 12}, True, {}, "-Xms10G -Xmx10G " + ZGC, ["DistantHorizons*"]),
    "lite_client":   ({"renderDistance": 12}, True, {}, "-Xms10G -Xmx10G " + ZGC,
                      ["DistantHorizons*", "visuality*", "particlerain*", "SubtleEffects*", "fallingleaves*", "AmbientSounds*", "PresenceFootsteps*", "pf-*"]),
    "rd8":           ({"renderDistance": 8, "simulationDistance": 6}, True, {}, "-Xms10G -Xmx10G " + ZGC, []),
}


def set_options(over):
    p = GAME / "options.txt"
    lines = p.read_text("utf8").splitlines() if p.exists() else []
    keys = {k: str(v) for k, v in {"maxFps": 260, "enableVsync": "false", "pauseOnLostFocus": "false", "fullscreen": "false", **over}.items()}
    out, seen = [], set()
    for l in lines:
        k = l.split(":", 1)[0]
        if k in keys:
            out.append(f"{k}:{keys[k]}"); seen.add(k)
        else:
            out.append(l)
    out += [f"{k}:{v}" for k, v in keys.items() if k not in seen]
    p.write_text("\n".join(out) + "\n", "utf8")


def set_iris(on):
    p = GAME / "config/iris.properties"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"enableShaders={'true' if on else 'false'}\nshaderPack=ComplementaryReimagined_r5.9.3.zip\ndisableUpdateMessage=true\n", "utf8")


def toggle_mods(globs, disable):
    moved = []
    for g in globs:
        for f in (GAME / "mods").glob(g if disable else g + ".disabled"):
            if disable and f.suffix == ".jar":
                f.rename(f.with_name(f.name + ".disabled")); moved.append(f.name)
            elif not disable:
                f.rename(f.with_name(f.name[: -len(".disabled")]))
    return moved


def prepare_world():
    dst = GAME / "saves/bench"
    if not dst.exists():
        shutil.copytree(WORLD_SRC, dst, ignore=shutil.ignore_patterns("session.lock"))
    (GAME / "kubejs/client_scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "tests/kubejs_client/zz_fps_probe.js", GAME / "kubejs/client_scripts/zz_fps_probe.js")


def run(name):
    over, shaders, _prof, jvm, off = VARIANTS[name]
    set_options(over)
    set_iris(shaders)
    moved = toggle_mods(off, True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(ROOT / "tools/launch_client.py"), "--world", "bench", "--res", RES, "--jvm", jvm,
                        "--fps-samples", "22", "--timeout", "1200"], capture_output=True, text=True, encoding="utf8", errors="replace")
    toggle_mods(off, False)
    m = re.search(r"FPS median=(\d+) min=(\d+) max=(\d+) avg=(\d+)", r.stdout)
    line = (f"| {time.strftime('%Y-%m-%d %H:%M')} | {name} | {m.group(1)} | {m.group(2)} | {m.group(3)} | {m.group(4)} | {RES} | {', '.join(moved) or '-'} |"
            if m else f"| {time.strftime('%Y-%m-%d %H:%M')} | {name} | FAILED | | | | {RES} | {r.stdout.strip().splitlines()[-1:] if r.stdout else ''} |")
    print(line, f"({time.time() - t0:.0f}s)")
    rep = ROOT / "docs/reports/performance.md"
    if not rep.exists():
        rep.write_text("# Производительность клиента (авто, tools/bench_client.py)\n\nПК теста: Ryzen 5 7500F, RX 6700 XT, 2560×1377, сервер выключен (одиночный мир).\n\n"
                       "| дата | вариант | медиана FPS | мин | макс | среднее | разрешение | выключено |\n|---|---|---|---|---|---|---|---|\n", "utf8")
    with open(rep, "a", encoding="utf8") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    prepare_world()
    for n in sys.argv[1:] or ["baseline"]:
        run(n)
