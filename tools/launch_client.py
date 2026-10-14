#!/usr/bin/env python3
"""Client smoke test (docs/08_TESTING.md level 5): launch the NeoForge client offline from a vanilla-layout
directory and wait until the title screen loads (or a crash). The game window opens briefly, then is closed.

Usage: launch_client.py [--mcdir tests/client_run/appdata/.minecraft] [--gamedir tests/client_run/game]
                        [--version neoforge-21.1.259] [--timeout 900] [--keep]
Libraries missing from the mcdir are downloaded from the URLs in the version json.
"""
import json, os, re, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]


def opt(name, default):
    return args[args.index(name) + 1] if name in args else default


MC = Path(opt("--mcdir", str(ROOT / "tests/client_run/appdata/.minecraft"))).resolve()
GAME = Path(opt("--gamedir", str(ROOT / "tests/client_run/game"))).resolve()
VER = opt("--version", "neoforge-21.1.259")
TIMEOUT = int(opt("--timeout", "900"))
JAVA = next((ROOT / "tools/bin/jre").glob("*/bin/java.exe"))


def load(v):
    d = json.loads((MC / "versions" / v / f"{v}.json").read_text("utf8"))
    if "inheritsFrom" in d:
        parent = load(d["inheritsFrom"])
        merged = dict(parent)
        merged.update({k: v for k, v in d.items() if k not in ("libraries", "arguments")})
        merged["libraries"] = d.get("libraries", []) + parent.get("libraries", [])
        merged["arguments"] = {"game": parent.get("arguments", {}).get("game", []) + d.get("arguments", {}).get("game", []),
                               "jvm": parent.get("arguments", {}).get("jvm", []) + d.get("arguments", {}).get("jvm", [])}
        merged["_jar"] = d.get("jar", d["inheritsFrom"])
        return merged
    d["_jar"] = v
    return d


def allowed(rules):
    if not rules:
        return True
    ok = False
    for r in rules:
        os_ok = "os" not in r or r["os"].get("name") in (None, "windows")
        if "features" in r:
            continue
        if os_ok:
            ok = r["action"] == "allow"
    return ok


def fetch(url, path):
    if path.exists() or not url:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print("download", path.name)
    urllib.request.urlretrieve(url, path)


def main():
    v = load(VER)
    libdir = MC / "libraries"
    cp, seen = [], set()
    for lib in v["libraries"]:
        if not allowed(lib.get("rules")):
            continue
        art = lib.get("downloads", {}).get("artifact")
        if art:
            p = libdir / art["path"]
            fetch(art.get("url"), p)
        else:
            g, a, ver = lib["name"].split(":")[:3]
            p = libdir / Path(*g.split(".")) / a / ver / f"{a}-{ver}.jar"
            fetch(lib.get("url", "https://libraries.minecraft.net/") + p.relative_to(libdir).as_posix(), p)
        key = ":".join(lib["name"].split(":")[:2] + lib["name"].split(":")[3:])
        if key in seen:
            continue
        seen.add(key)
        cp.append(str(p))
    client_jar = MC / "versions" / v["_jar"] / f"{v['_jar']}.jar"
    fetch(v.get("downloads", {}).get("client", {}).get("url"), client_jar)
    if "inheritsFrom" not in json.loads((MC / "versions" / VER / f"{VER}.json").read_text("utf8")):
        cp.append(str(client_jar))  # NeoForge builds the game from its own patched jars (vanilla jar is in its ignoreList)
    natives = MC / "natives" / VER
    natives.mkdir(parents=True, exist_ok=True)
    GAME.mkdir(parents=True, exist_ok=True)
    subs = {
        "${natives_directory}": str(natives), "${launcher_name}": "arkhaven-smoke", "${launcher_version}": "1",
        "${classpath}": os.pathsep.join(cp), "${classpath_separator}": os.pathsep, "${library_directory}": str(libdir),
        "${version_name}": VER, "${game_directory}": str(GAME), "${assets_root}": str(MC / "assets"),
        "${assets_index_name}": v["assetIndex"]["id"], "${auth_player_name}": "ArkhavenTest",
        "${auth_uuid}": "00000000000000000000000000000000", "${auth_access_token}": "0", "${clientid}": "0",
        "${auth_xuid}": "0", "${user_type}": "legacy", "${version_type}": "release", "${user_properties}": "{}",
    }

    def expand(items):
        out = []
        for it in items:
            if isinstance(it, dict):
                if not allowed(it.get("rules")):
                    continue
                vals = it["value"] if isinstance(it["value"], list) else [it["value"]]
            else:
                vals = [it]
            for s in vals:
                for k, val in subs.items():
                    s = s.replace(k, val)
                out.append(s)
        return out

    user_jvm = opt("--jvm", "-Xms12G -Xmx12G -XX:+UseZGC -XX:+ZGenerational -XX:+AlwaysPreTouch").split()
    jvm = user_jvm + ["-Dsodium.checks.issue2561=false"] + expand(v["arguments"]["jvm"])
    w, h = opt("--res", "960x540").split("x")
    game = expand(v["arguments"]["game"]) + ["--width", w, "--height", h]
    join = opt("--join", None)          # e.g. 127.0.0.1:25565 -> connect straight to a server
    world = opt("--world", None)        # singleplayer save name -> benchmark mode (needs the FPS probe script)
    samples = int(opt("--fps-samples", "18"))
    hold = int(opt("--hold", "15"))     # seconds to stay alive after success
    if join:
        game += ["--quickPlayMultiplayer", join]
    if world:
        game += ["--quickPlaySingleplayer", world]
    # Crash Assistant would report our scripted shutdown as a crash: keep it out of test runs.
    for f in (GAME / "mods").glob("CrashAssistant*.jar"):
        f.replace(f.with_suffix(".jar.disabled"))
    log = GAME / "smoke.log"
    with open(log, "wb") as lf:
        p = subprocess.Popen([str(JAVA), *jvm, v["mainClass"], *game], cwd=GAME, stdout=lf, stderr=subprocess.STDOUT)
        t0, result = time.time(), "TIMEOUT"
        while time.time() - t0 < TIMEOUT:
            if p.poll() is not None:
                result = f"EXITED {p.returncode}"
                break
            txt = log.read_text("utf8", "replace")
            if world:
                fps = [int(x) for x in re.findall(r"ARK_FPS (\d+)", txt)]
                if len(fps) >= samples:
                    warm = fps[4:] or fps
                    s = sorted(warm)
                    result = "BENCH"
                    print(f"FPS samples={warm}")
                    print(f"FPS median={s[len(s) // 2]} min={s[0]} max={s[-1]} avg={sum(s) / len(s):.0f}")
                    shot = opt("--screenshot", None)
                    if shot:  # focus the game, press the given key (e.g. L = quest book) and grab the screen
                        from PIL import ImageGrab
                        ps = ("$w=New-Object -ComObject WScript.Shell; [void]$w.AppActivate('Minecraft'); Start-Sleep -Milliseconds 800; "
                              f"$w.SendKeys('{opt('--key', 'l')}'); Start-Sleep -Seconds 4")
                        subprocess.run(["powershell", "-NoProfile", "-Command", ps])
                        ImageGrab.grab().save(shot)
                        print("screenshot", shot)
                    break
            elif join:
                if re.search(r"Disconnected|Lost connection|Failed to connect|disconnect\.", txt):
                    result = "DISCONNECTED"
                    break
                if re.search(r"\[CHAT\]|logged in with entity id|Received .*ClientboundLogin|Started 1 worker threads|Preparing spawn", txt) or "joined the game" in txt:
                    result = "JOINED"
                    time.sleep(hold)
                    break
            elif re.search(r"Sound engine started|Created: \d+x\d+x\d+ minecraft:textures/atlas/gui", txt) and "Reloading ResourceManager" in txt:
                result = "TITLE_SCREEN"
                time.sleep(hold)  # let late init errors surface
                break
            time.sleep(3)
        if p.poll() is None and "--keep" not in args:
            p.terminate()
            try:
                p.wait(30)
            except subprocess.TimeoutExpired:
                p.kill()
    print(f"CLIENT {result} after {time.time() - t0:.0f}s")
    txt = log.read_text("utf8", "replace")
    for l in [l for l in txt.splitlines() if re.search(r"/(ERROR|FATAL)\]|Exception|Mixin apply failed", l)][:30]:
        print("  ", l[:300])
    sys.exit(0 if result in ("TITLE_SCREEN", "JOINED", "BENCH") else 1)


if __name__ == "__main__":
    main()
