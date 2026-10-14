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


def instance_cfg(mem, own_java=True):
    pre = f'cmd /c "$INST_MC_DIR/prelaunch.cmd" "$INST_JAVA" "$INST_DIR" {REL["pack_url"]}'
    java = ("OverrideJavaLocation=true\nJavaPath=@JAVA@\nAutomaticJava=false\n" if own_java
            else "OverrideJavaLocation=false\nAutomaticJava=true\n")  # imported into someone's Prism: let it pick/download Java 21
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
JvmArgs=-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=50 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=16M -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15
{java}IgnoreJavaCompatibility=false
JoinServerOnLaunch=true
JoinServerOnLaunchAddress={REL['server_address']}
"""


def build_discover_jar():
    """Discover.java -> Discover.jar: a JRE (no compiler) can't run .java sources, but runs any jar."""
    import os, glob
    cands = glob.glob(str(ROOT / "tools/bin/jre/*/bin/javac.exe")) + [os.path.join(os.environ.get(v, ""), "bin", "javac.exe")
             for v in ("JAVA_HOME_21_X64", "JAVA_HOME")]
    javac = next((c for c in cands if os.path.exists(c)), "javac")
    out = L / "build/discover"
    if out.exists():
        shutil.rmtree(out)
    (out / "classes").mkdir(parents=True)
    subprocess.run([javac, "--release", "21", "-d", str(out / "classes"), str(L / "Discover.java")], check=True)
    jar = out / "Discover.jar"
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\nMain-Class: Discover\r\n\r\n")
        for c in (out / "classes").glob("*.class"):
            z.write(c, c.name)
    return jar


def zip_dir(src, out, prefix=""):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_file():
                z.write(f, prefix + f.relative_to(src).as_posix())
    print("built", out)


def build_prism_zip(stage_mc):
    """Arkhaven-Prism-Instance.zip: Prism Launcher / MultiMC -> "Add instance" -> "Import" -> this zip.
    Same instance as the installer's (auto-update + LAN/ZeroTier discovery before each launch), Java picked by Prism."""
    d = L / "build/prism-instance"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(stage_mc, d / ".minecraft")
    p = PRESETS["beautiful"]
    (d / ".minecraft/options.txt").write_text(options_for(p), "utf8")
    (d / ".minecraft/config").mkdir(exist_ok=True)
    (d / ".minecraft/config/iris.properties").write_text(iris_for(p), "utf8")
    (d / "instance.cfg").write_text(instance_cfg(p["mem"], own_java=False).replace("MaxMemAlloc=%d" % p["mem"], "MaxMemAlloc=10240"), "utf8")
    shutil.copy(STAGE / "instances/Arkhaven/mmc-pack.json", d / "mmc-pack.json")
    shutil.copy(L / "assets/arkhaven.png", d / "arkhaven.png")
    zip_dir(d, L / "dist/Arkhaven-Prism-Instance.zip")


def build_own_launcher_zip():
    """Arkhaven-Own-Launcher.zip: for the official Minecraft Launcher and other launchers using a .minecraft folder."""
    d = L / "build/own-launcher"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for f in ("install-to-launcher.cmd", "install-to-launcher.ps1", "zerotier-join.ps1"):
        shutil.copy(L / f, d / f)
    shutil.copy(L / "build/discover/Discover.jar", d / "Discover.jar")
    shutil.copy(L / "own-launcher-README.txt", d / "ПРОЧТИ.txt")
    zip_dir(d, L / "dist/Arkhaven-Own-Launcher.zip")


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
    pwbs = ROOT / "tools/bin/pwbs.jar"
    if not pwbs.exists():
        rel = json.load(urllib.request.urlopen("https://api.github.com/repos/packwiz/packwiz-installer-bootstrap/releases/latest"))
        fetch(rel["assets"][0]["browser_download_url"], pwbs)
    shutil.copy(pwbs, mc / "packwiz-installer-bootstrap.jar")
    discover = build_discover_jar()
    shutil.copy(discover, mc / "Discover.jar")
    shutil.copy(L / "prelaunch.cmd", mc / "prelaunch.cmd")
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
    shutil.copy(L / "zerotier-join.ps1", STAGE / "zerotier-join.ps1")
    (STAGE / "THIRD_PARTY.txt").write_text(
        "Prism Launcher — GPL-3.0, https://github.com/PrismLauncher/PrismLauncher (unmodified binaries)\n"
        "Eclipse Temurin JRE 21 — GPLv2 with Classpath Exception, https://adoptium.net\n"
        "packwiz-installer-bootstrap — MIT, https://github.com/packwiz/packwiz-installer-bootstrap\n"
        "Mods are downloaded from Modrinth/CurseForge on first launch; none are redistributed here.\n", "utf8")
    (L / "dist").mkdir(exist_ok=True)
    build_prism_zip(mc)
    build_own_launcher_zip()
    iscc = ROOT / "tools/bin/inno/ISCC.exe"
    if not iscc.exists():  # CI runner: Inno Setup is preinstalled
        iscc = next(p for p in [Path(rf"{d}/Inno Setup {v}/ISCC.exe") for v in (7, 6) for d in ("C:/Program Files", "C:/Program Files (x86)")] if p.exists())
    subprocess.run([str(iscc), f"/DStage={STAGE}", f"/DMyVersion={REL['version']}", f"/DNetworkUrl={REL.get('network_url', '')}", f"/O{L / 'dist'}", str(L / "arkhaven.iss")], check=True)
    print("built", next((L / "dist").glob(f"Arkhaven-Setup-{REL['version']}.exe")))


if __name__ == "__main__":
    main()
