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
RES = "2560x1377"
WARMUP = 4    # 20 s discarded (owner: every run <= 3 minutes)
SAMPLES = 4 + 10  # the owner's maximised window

MEDIUM = "\n".join([
    "SHADOW_QUALITY=2", "shadowDistance=128.0", "WATER_REFLECT_QUALITY=2", "BLOCK_REFLECT_QUALITY=1",
    "LIGHTSHAFT_QUALI_DEFINE=1", "SSAO_QUALI_DEFINE=2", "FXAA_DEFINE=1", "DETAIL_QUALITY=2", "CLOUD_QUALITY=2",
    "ANISOTROPIC_FILTER=0", "COLORED_LIGHTING=0", "WORLD_SPACE_REFLECTIONS=-1", "ENTITY_SHADOW=-1", "RAIN_PUDDLES=0"]) + "\n"

G1 = "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=50 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=16M -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15"
ZGC = "-XX:+UseZGC -XX:+ZGenerational -XX:+AlwaysPreTouch -XX:+DisableExplicitGC"

DH_TUNED = [(r"lodChunkRenderDistanceRadius = \d+", "lodChunkRenderDistanceRadius = 128"),
            (r'maxHorizontalResolution = "\w+"', 'maxHorizontalResolution = "TWO_BLOCKS"'),
            (r'verticalQuality = "\w+"', 'verticalQuality = "LOW"'),
            (r"enableSsao = true", "enableSsao = false")]
DH_DEFAULT = [(r"lodChunkRenderDistanceRadius = \d+", "lodChunkRenderDistanceRadius = 256"),
              (r'maxHorizontalResolution = "\w+"', 'maxHorizontalResolution = "BLOCK"'),
              (r'verticalQuality = "\w+"', 'verticalQuality = "MEDIUM"'),
              (r"enableSsao = false", "enableSsao = true")]


def set_dh(rules):
    p = GAME / "config/DistantHorizons.toml"
    if not p.exists():
        return
    t = p.read_text("utf8")
    for a, b in rules:
        t = re.sub(a, b, t)
    p.write_text(t, "utf8")


VARIANTS = {
    # name: (options overrides, shaders on?, shader profile options, jvm, disabled mod globs)
    "baseline":      ({"renderDistance": 12}, True, {}, "-Xms4G -Xmx12G " + G1, []),
    "mem10_g1":      ({"renderDistance": 12}, True, {}, "-Xms12G -Xmx12G " + G1, []),
    "current":       ({"renderDistance": 12}, True, {}, "-Xms4G -Xmx12G " + G1, []),
    "noshader":      ({"renderDistance": 12}, False, {}, "-Xms4G -Xmx12G " + G1, []),
    "no_dh":         ({"renderDistance": 12}, True, {}, "-Xms4G -Xmx12G " + G1, ["DistantHorizons*"]),
    "lite_client":   ({"renderDistance": 12}, True, {}, "-Xms4G -Xmx12G " + G1,
                      ["DistantHorizons*", "visuality*", "particlerain*", "SubtleEffects*", "fallingleaves*", "AmbientSounds*", "PresenceFootsteps*", "pf-*"]),
    "no_dh_medium":  ({"renderDistance": 12}, True, {"SHADER": MEDIUM}, "-Xms4G -Xmx12G " + G1, ["DistantHorizons*"]),
    "shader_medium": ({"renderDistance": 12}, True, {"SHADER": MEDIUM}, "-Xms4G -Xmx12G " + G1, []),
    "rd8":           ({"renderDistance": 8, "simulationDistance": 6}, True, {}, "-Xms4G -Xmx12G " + G1, []),
    # DH tuned: 128-chunk LOD radius, 2-block LOD columns, low vertical quality, no DH SSAO (shaders do AO)
    "dh_tuned":      ({"renderDistance": 12}, True, {"DH": DH_TUNED}, "-Xms4G -Xmx12G " + G1, []),
    "dh_tuned_rd10": ({"renderDistance": 10, "simulationDistance": 6}, True, {"DH": DH_TUNED}, "-Xms4G -Xmx12G " + G1, []),
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



def set_shader_profile(text):
    p = GAME / "shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt"
    if text: p.write_text(text, "utf8")
    elif p.exists(): p.unlink()


def set_iris(on):
    p = GAME / "config/iris.properties"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"enableShaders={'true' if on else 'false'}\nshaderPack=ComplementaryReimagined_r5.9.3.zip\ndisableUpdateMessage=true\n", "utf8")


def toggle_mods(globs, disable):
    moved = []
    for g in globs:
        for f in (GAME / "mods").glob(g if disable else g + ".disabled"):
            if disable and f.suffix == ".jar":
                f.replace(f.with_name(f.name + ".disabled")); moved.append(f.name)
            elif not disable:
                f.replace(f.with_name(f.name[: -len(".disabled")]))
    return moved


def prepare_world():
    dst = GAME / "saves/bench"
    if not dst.exists():
        shutil.copytree(WORLD_SRC, dst, ignore=shutil.ignore_patterns("session.lock"))
    (GAME / "kubejs/client_scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "tests/kubejs_client/zz_fps_probe.js", GAME / "kubejs/client_scripts/zz_fps_probe.js")
    (GAME / "kubejs/server_scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "tests/kubejs_bench/zz_open_quests_probe.js", GAME / "kubejs/server_scripts/zz_open_quests_probe.js")


def run(name):
    over, shaders, extra, jvm, off = VARIANTS[name]
    set_dh(extra.get("DH", []))
    set_shader_profile(extra.get("SHADER", ""))
    set_options(over)
    set_iris(shaders)
    moved = toggle_mods(off, True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(ROOT / "tools/launch_client.py"), "--world", "bench", "--res", RES, "--jvm", jvm,
                        "--fps-samples", str(SAMPLES), "--warmup", str(WARMUP), "--timeout", "180"], capture_output=True, text=True, encoding="utf8", errors="replace")
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
