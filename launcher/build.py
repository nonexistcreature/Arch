#!/usr/bin/env python3
"""Build Arkhaven-Setup.exe: Prism Launcher (portable) + Temurin 21 JRE + preconfigured instance + Inno Setup.

Inputs:  launcher/release.json (pack URL, server address, version), launcher/presets.json, pack/options.txt,
         tools/bin/cache/{prism.zip, jre21.zip} (downloaded if missing), tools/bin/pwbs.jar, tools/bin/inno/ISCC.exe
Output:  launcher/dist/Arkhaven-Setup-<version>.exe
No mod jars are bundled: mods are downloaded by packwiz-installer on first launch.
"""
import json, shutil, subprocess, sys, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L = ROOT / "launcher"
CACHE = ROOT / "tools/bin/cache"
STAGE = L / "build/stage"
REL = json.loads((L / "release.json").read_text("utf8"))
PRESETS = json.loads((L / "presets.json").read_text("utf8"))
PRISM_URL = "https://github.com/PrismLauncher/PrismLauncher/releases/download/11.1.1/PrismLauncher-Windows-MSVC-Portable-11.1.1.zip"
JRE_URL = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse"


def fetch(url, dest):
    if not dest.exists():
        print("download", url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dest)
    return dest


def unzip_flat(zp, dest):
    """Extract zip; if it has a single top-level folder, strip it."""
    with zipfile.ZipFile(zp) as z:
        names = z.namelist()
        tops = {n.split("/")[0] for n in names}
        strip = len(tops) == 1 and any("/" in n for n in names)
        for n in names:
            rel = n.split("/", 1)[1] if strip else n
            if not rel or n.endswith("/"):
                continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(n) as src, open(out, "wb") as dst:
                shutil.copyfileobj(src, dst)


def options_for(preset):
    base = (ROOT / "pack/options.txt").read_text("utf8").splitlines()
    over = {k: str(v) for k, v in preset["options"].items()}
    out, seen = [], set()
    for line in base:
        k = line.split(":", 1)[0]
        if k in over:
            out.append(f"{k}:{over[k]}"); seen.add(k)
        else:
            out.append(line)
    out += [f"{k}:{v}" for k, v in over.items() if k not in seen]
    return "\n".join(out) + "\n"


def iris_for(preset):
    return ("enableShaders=%s\nshaderPack=ComplementaryReimagined_r5.9.3.zip\ndisableUpdateMessage=true\n"
            % ("true" if preset["shaders"] else "false"))


def instance_cfg(mem):
    pre = f'"$INST_JAVA" -jar packwiz-installer-bootstrap.jar -s client {REL["pack_url"]}'
    return f"""[General]
ConfigVersion=1.2
InstanceType=OneSix
name=Arkhaven
iconKey=arkhaven
notes=Arkhaven {REL['version']}
OverrideCommands=true
PreLaunchCommand={pre}
OverrideMemory=true
MinMemAlloc=4096
MaxMemAlloc={mem}
OverrideJavaArgs=true
JvmArgs=-XX:+UseZGC -XX:+ZGenerational -XX:+AlwaysPreTouch -XX:+DisableExplicitGC
OverrideJavaLocation=true
JavaPath=@JAVA@
AutomaticJava=false
IgnoreJavaCompatibility=false
JoinServerOnLaunch=true
JoinServerOnLaunchAddress={REL['server_address']}
"""


def main():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    unzip_flat(fetch(PRISM_URL, CACHE / "prism.zip"), STAGE)
    unzip_flat(fetch(JRE_URL, CACHE / "jre21.zip"), STAGE / "java")
    (STAGE / "prismlauncher.cfg").write_text(
        "[General]\nLanguage=ru\nJavaPath=@JAVA@\nAutomaticJavaDownload=false\nAutomaticJavaSwitch=false\n"
        "MaxMemAlloc=8192\nMinMemAlloc=4096\nApplicationTheme=dark\nIconTheme=pe_colored\nShowConsole=false\n"
        "ShowConsoleOnError=true\nAutoCloseConsole=true\nUpdateChannel=\nAutoUpdate=false\nAnalyticsSeen=2\n"
        "MenuBarInsteadOfToolBar=false\nSelectedInstance=Arkhaven\nInstSortMode=Name\n", "utf8")
    inst = STAGE / "instances/Arkhaven"
    mc = inst / ".minecraft"
    mc.mkdir(parents=True)
    (inst / "instance.cfg").write_text(instance_cfg(PRESETS["beautiful"]["mem"]), "utf8")
    (inst / "mmc-pack.json").write_text(json.dumps({"formatVersion": 1, "components": [
        {"uid": "net.minecraft", "version": REL["minecraft"], "important": True},
        {"uid": "net.neoforged", "version": REL["neoforge"]}]}, indent=2), "utf8")
    shutil.copy(ROOT / "tools/bin/pwbs.jar", mc / "packwiz-installer-bootstrap.jar")
    subprocess.run([sys.executable, str(ROOT / "tools/make_servers_dat.py"), REL["server_address"]], check=True)
    shutil.copy(ROOT / "pack/servers.dat", mc / "servers.dat")
    (STAGE / "icons").mkdir(exist_ok=True)
    shutil.copy(L / "assets/arkhaven.png", STAGE / "icons/arkhaven.png")
    shutil.copy(L / "assets/arkhaven.ico", STAGE / "arkhaven.ico")
    # graphics presets (applied by the installer page and by switch-graphics.cmd)
    for name, p in PRESETS.items():
        d = STAGE / "presets" / name
        (d / "config").mkdir(parents=True)
        (d / "options.txt").write_text(options_for(p), "utf8")
        (d / "config/iris.properties").write_text(iris_for(p), "utf8")
        (d / "instance.cfg").write_text(instance_cfg(p["mem"]), "utf8")
    shutil.copy(L / "switch-graphics.cmd", STAGE / "switch-graphics.cmd")
    shutil.copy(L / "switch-graphics.ps1", STAGE / "switch-graphics.ps1")
    (STAGE / "THIRD_PARTY.txt").write_text(
        "Prism Launcher — GPL-3.0, https://github.com/PrismLauncher/PrismLauncher (unmodified binaries)\n"
        "Eclipse Temurin JRE 21 — GPLv2 with Classpath Exception, https://adoptium.net\n"
        "packwiz-installer-bootstrap — MIT, https://github.com/packwiz/packwiz-installer-bootstrap\n"
        "Mods are downloaded from Modrinth/CurseForge on first launch; none are redistributed here.\n", "utf8")
    iscc = ROOT / "tools/bin/inno/ISCC.exe"
    (L / "dist").mkdir(exist_ok=True)
    subprocess.run([str(iscc), f"/DStage={STAGE}", f"/DMyVersion={REL['version']}", f"/O{L / 'dist'}", str(L / "arkhaven.iss")], check=True)
    print("built", next((L / "dist").glob(f"Arkhaven-Setup-{REL['version']}.exe")))


if __name__ == "__main__":
    main()
