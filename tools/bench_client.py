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
# World + flight circle (x, z, radius). "real": a copy of the live server world, circling the players' base.
WORLDS = {"bench": (ROOT / "tests/server_run/world", -850, 0, 64),
          "bench_real": (Path("C:/Arkhaven/server/world"), -73, -133, 32)}
WORLD = "bench_real" if "--real" in sys.argv else "bench"
RES = "2560x1377"
WARMUP = 4    # 20 s discarded (owner: every run <= 3 minutes)
SAMPLES = 4 + 10  # the owner's maximised window

MEDIUM = "\n".join([
    "SHADOW_QUALITY=2", "shadowDistance=128.0", "WATER_REFLECT_QUALITY=2", "BLOCK_REFLECT_QUALITY=1",
    "LIGHTSHAFT_QUALI_DEFINE=1", "SSAO_QUALI_DEFINE=2", "FXAA_DEFINE=1", "DETAIL_QUALITY=2", "CLOUD_QUALITY=2",
    "ANISOTROPIC_FILTER=0", "COLORED_LIGHTING=0", "WORLD_SPACE_REFLECTIONS=-1", "ENTITY_SHADOW=-1", "RAIN_PUDDLES=0"]) + "\n"


def shp(s):
    return "\n".join(s.split()) + "\n"


SH_LOW = shp("SHADOW_QUALITY=0 shadowDistance=96.0 WATER_REFLECT_QUALITY=2 BLOCK_REFLECT_QUALITY=1 LIGHTSHAFT_QUALI_DEFINE=0 SSAO_QUALI_DEFINE=2 FXAA_DEFINE=-1 DETAIL_QUALITY=2 CLOUD_QUALITY=2 ANISOTROPIC_FILTER=0 COLORED_LIGHTING=0 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=-1 RAIN_PUDDLES=0")
# our pick: soft shadows to 96 blocks, cheap light shafts, FXAA, no entity shadows / block reflections
SH_TUNED = shp("SHADOW_QUALITY=1 shadowDistance=96.0 WATER_REFLECT_QUALITY=2 BLOCK_REFLECT_QUALITY=1 LIGHTSHAFT_QUALI_DEFINE=1 SSAO_QUALI_DEFINE=2 FXAA_DEFINE=1 DETAIL_QUALITY=2 CLOUD_QUALITY=2 ANISOTROPIC_FILTER=0 COLORED_LIGHTING=0 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=-1 RAIN_PUDDLES=0")
SH_LITE = shp("SHADOW_QUALITY=0 shadowDistance=80.0 WATER_REFLECT_QUALITY=2 BLOCK_REFLECT_QUALITY=0 LIGHTSHAFT_QUALI_DEFINE=0 SSAO_QUALI_DEFINE=0 FXAA_DEFINE=1 DETAIL_QUALITY=2 CLOUD_QUALITY=2 ANISOTROPIC_FILTER=0 COLORED_LIGHTING=0 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=-1 RAIN_PUDDLES=0")
SH_NOSHADOW = shp("SHADOW_QUALITY=-1 shadowDistance=64.0 WATER_REFLECT_QUALITY=2 BLOCK_REFLECT_QUALITY=1 LIGHTSHAFT_QUALI_DEFINE=0 SSAO_QUALI_DEFINE=2 FXAA_DEFINE=1 DETAIL_QUALITY=2 CLOUD_QUALITY=2 ANISOTROPIC_FILTER=0 COLORED_LIGHTING=0 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=-1 RAIN_PUDDLES=0")

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
    # pack defaults as shipped (options.txt from pack/: render 10, simulation 8)
    "pack":          ({"renderDistance": 10, "simulationDistance": 8}, True, {}, "-Xms4G -Xmx8G " + G1, []),
    "sh_medium":     ({"renderDistance": 10, "simulationDistance": 8}, True, {"SHADER": MEDIUM}, "-Xms4G -Xmx8G " + G1, []),
    "sh_low":        ({"renderDistance": 10, "simulationDistance": 8}, True, {"SHADER": SH_LOW}, "-Xms4G -Xmx8G " + G1, []),
    "sh_tuned":      ({"renderDistance": 10, "simulationDistance": 8}, True, {"SHADER": SH_TUNED}, "-Xms4G -Xmx8G " + G1, []),
    # cosmetic client mods off, one group at a time (cost on a CPU-bound client)
    "ns_no_cosmetic": ({"renderDistance": 10, "simulationDistance": 8}, False, {}, "-Xms4G -Xmx8G " + G1,
                       ["sound-physics*", "particlerain*", "visuality*", "SubtleEffects*", "Falling Leaves*", "AmbientSounds*", "PresenceFootsteps*"]),
    "ns_no_soundphys": ({"renderDistance": 10, "simulationDistance": 8}, False, {}, "-Xms4G -Xmx8G " + G1, ["sound-physics*"]),
    "ns_no_emf":     ({"renderDistance": 10, "simulationDistance": 8}, False, {}, "-Xms4G -Xmx8G " + G1, ["entity_model_features*", "notenoughanimations*"]),
    "sh_lite":       ({"renderDistance": 10, "simulationDistance": 8}, True, {"SHADER": SH_LITE}, "-Xms4G -Xmx8G " + G1, []),
    "sh_noshadow":   ({"renderDistance": 10, "simulationDistance": 8}, True, {"SHADER": SH_NOSHADOW}, "-Xms4G -Xmx8G " + G1, []),
    "sh_low_rd8":    ({"renderDistance": 8, "simulationDistance": 8}, True, {"SHADER": SH_LOW}, "-Xms4G -Xmx8G " + G1, []),
    "sh_lite_rd8":   ({"renderDistance": 8, "simulationDistance": 8}, True, {"SHADER": SH_LITE}, "-Xms4G -Xmx8G " + G1, []),
    "makeup":        ({"renderDistance": 10, "simulationDistance": 8}, True, {"PACK": "MakeUp-UltraFast-9.5g.zip"}, "-Xms4G -Xmx8G " + G1, []),
    # exactly what ships (shader profile from pack/shaderpacks), with a too-small heap to trigger the memory hint
    "shipped_5g":    ({"renderDistance": 10, "simulationDistance": 8}, True,
                      {"SHADER": (ROOT / "pack/shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt").read_text("utf8")}, "-Xms4G -Xmx5G " + G1, []),
    "pack_noshader": ({"renderDistance": 10, "simulationDistance": 8}, False, {}, "-Xms4G -Xmx8G " + G1, []),
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


def set_iris(on, pack="ComplementaryReimagined_r5.9.3.zip"):
    p = GAME / "config/iris.properties"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"enableShaders={'true' if on else 'false'}\nshaderPack={pack}\ndisableUpdateMessage=true\n", "utf8")


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
    src, cx, cz, r = WORLDS[WORLD]
    dst = GAME / "saves" / WORLD
    if not dst.exists():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("session.lock", "*.dat_old"))
    (GAME / "kubejs/client_scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "tests/kubejs_client/zz_fps_probe.js", GAME / "kubejs/client_scripts/zz_fps_probe.js")
    (GAME / "kubejs/server_scripts").mkdir(parents=True, exist_ok=True)
    (GAME / "kubejs/server_scripts/zz_open_quests_probe.js").unlink(missing_ok=True)
    probe = (ROOT / "tests/kubejs_bench/zz_move_probe.js").read_text("utf8")
    for k, v in (("ARK_CX", cx), ("ARK_CZ", cz), ("ARK_R", r)):
        probe = probe.replace(k, str(v))
    (GAME / "kubejs/server_scripts/zz_move_probe.js").write_text(probe, "utf8")


SHOT_PS = r"""Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height
[System.Drawing.Graphics]::FromImage($bmp).CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size); $bmp.Save('%s')"""


def shoot_later(name, at=9):
    """Screenshot of the desktop once the run has logged `at` frame-time windows (for eyeballing presets)."""
    import threading

    def go():
        log, t0 = GAME / "smoke.log", time.time()
        time.sleep(20)
        while time.time() - t0 < 300:
            if log.exists() and log.read_text("utf8", "replace").count("ARK_FT") >= at:
                out = ROOT / "tests/client_run/shots" / f"{name}.png"
                out.parent.mkdir(exist_ok=True)
                subprocess.run(["powershell", "-NoProfile", "-Command", SHOT_PS % out], capture_output=True)
                return
            time.sleep(2)
    threading.Thread(target=go, daemon=True).start()


def run(name):
    over, shaders, extra, jvm, off = VARIANTS[name]
    set_dh(extra.get("DH", []))
    set_shader_profile(extra.get("SHADER", ""))
    set_options(over)
    set_iris(shaders, extra.get("PACK", "ComplementaryReimagined_r5.9.3.zip"))
    moved = toggle_mods(off, True)
    shoot_later(name + ("_real" if WORLD == "bench_real" else ""))
    t0 = time.time()
    r = subprocess.run([sys.executable, str(ROOT / "tools/launch_client.py"), "--world", WORLD, "--res", RES, "--jvm", jvm,
                        "--fps-samples", str(SAMPLES), "--warmup", str(WARMUP), "--timeout", "180"], capture_output=True, text=True, encoding="utf8", errors="replace")
    toggle_mods(off, False)
    m = re.search(r"FPS median=(\d+) min=(\d+) max=(\d+) avg=(\d+)", r.stdout)
    f = re.search(r"FT p99med=([\d.]+) worst=(\d+) s33=(\d+) s50=(\d+)", r.stdout)
    ft = f"{f.group(1)} | {f.group(2)} | {f.group(3)} | {f.group(4)}" if f else "| | |"
    name += " (real)" if WORLD == "bench_real" else ""
    line = (f"| {time.strftime('%Y-%m-%d %H:%M')} | {name} | {m.group(1)} | {m.group(2)} | {m.group(4)} | {ft} | {', '.join(moved) or '-'} |"
            if m else f"| {time.strftime('%Y-%m-%d %H:%M')} | {name} | FAILED | | | | | | | {r.stdout.strip().splitlines()[-1:] if r.stdout else ''} |")
    print(line, f"({time.time() - t0:.0f}s)")
    rep = ROOT / "docs/reports/performance.md"
    if not rep.exists():
        rep.write_text("# Производительность клиента (авто, tools/bench_client.py)\n\nПК теста: Ryzen 5 7500F, RX 6700 XT, 2560×1377, сервер выключен (одиночный мир).\n\n"
                       "| дата | вариант | медиана FPS | мин | макс | среднее | разрешение | выключено |\n|---|---|---|---|---|---|---|---|\n", "utf8")
    with open(rep, "a", encoding="utf8") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    prepare_world()
    for n in [a for a in sys.argv[1:] if not a.startswith("--")] or ["baseline"]:
        run(n)
