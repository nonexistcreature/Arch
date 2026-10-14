#!/bin/bash
# Build arkhaven-core (+GameTests) and put the jar into pack/mods (our own mod is shipped inside the pack).
set -e
cd "$(dirname "$0")/.."
python tools/make_core_resources.py
export JAVA_HOME="$(cd tools/bin/jre/jdk-21* && pwd -W 2>/dev/null || pwd)"
(cd core-mod && ./gradlew.bat build --no-daemon -q && ([ "$1" == "--no-tests" ] || ./gradlew.bat runGameTestServer --no-daemon -q 2>&1 | grep -E "GAME TESTS|tests passed|failed" ))
rm -f pack/mods/arkhaven_core-*.jar
cp core-mod/build/libs/arkhaven_core-*.jar pack/mods/
(cd pack && ../tools/bin/packwiz.exe refresh | tail -1)
