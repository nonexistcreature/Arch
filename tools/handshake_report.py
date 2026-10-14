#!/usr/bin/env python3
"""Collect `// HANDSHAKE:` comments from KubeJS scripts -> docs/reports/handshakes.md (docs/08_TESTING.md level 3)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = []
for f in sorted((ROOT / "pack/kubejs").rglob("*.js")):
    for n, line in enumerate(f.read_text("utf8").splitlines(), 1):
        m = re.search(r"//\s*HANDSHAKE:?\s*(.+)", line)
        if m:
            text = m.group(1).strip()
            solo = "solo" in text.lower() or "соло" in text.lower()
            rows.append((f.relative_to(ROOT).as_posix(), n, text, solo))
out = ["# Рукопожатия (авто, tools/handshake_report.py)\n", f"Всего: **{len(rows)}**\n", "| файл:строка | связь |", "|---|---|"]
out += [f"| {f}:{n} | {t} |" for f, n, t, _ in rows]
(ROOT / "docs/reports/handshakes.md").write_text("\n".join(out) + "\n", "utf8")
print(f"{len(rows)} handshakes")
