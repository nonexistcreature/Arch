#!/usr/bin/env python3
"""Draw the Arkhaven icon (ark-like hull under a star over a teal->navy gradient) -> launcher/assets/arkhaven.{png,ico}, server/server-icon.png"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
ROOT = Path(__file__).resolve().parent.parent
S = 512
img = Image.new("RGBA", (S, S))
d = ImageDraw.Draw(img)
for y in range(S):  # vertical gradient
    t = y / S
    d.line([(0, y), (S, y)], fill=(int(20 + 10 * t), int(120 - 80 * t), int(140 - 60 * t), 255))
mask = Image.new("L", (S, S)); ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], 96, fill=255)
img.putalpha(mask)
d = ImageDraw.Draw(img)
gold = (244, 196, 92, 255)
# hull
d.polygon([(96, 300), (416, 300), (360, 400), (152, 400)], fill=(250, 240, 220, 255))
d.rectangle([150, 250, 362, 300], fill=(250, 240, 220, 255))
d.polygon([(150, 250), (256, 170), (362, 250)], fill=gold)          # roof
d.rectangle([236, 262, 276, 300], fill=(40, 70, 90, 255))             # door
# star
cx, cy, r1, r2 = 256, 104, 46, 18
import math
pts = [(cx + (r1 if i % 2 == 0 else r2) * math.sin(i * math.pi / 5), cy - (r1 if i % 2 == 0 else r2) * math.cos(i * math.pi / 5)) for i in range(10)]
glow = Image.new("RGBA", (S, S)); ImageDraw.Draw(glow).polygon(pts, fill=(255, 230, 150, 200)); glow = glow.filter(ImageFilter.GaussianBlur(14))
img = Image.alpha_composite(img, glow); ImageDraw.Draw(img).polygon(pts, fill=gold)
# waves
d = ImageDraw.Draw(img)
for i, y in enumerate((420, 450)):
    d.arc([40, y - 30, 472, y + 30], 20, 160, fill=(200, 235, 245, 200 - 60 * i), width=10)
(ROOT / "launcher/assets").mkdir(parents=True, exist_ok=True)
img.save(ROOT / "launcher/assets/arkhaven.png")
img.save(ROOT / "launcher/assets/arkhaven.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
img.resize((64, 64), Image.LANCZOS).save(ROOT / "server/server-icon.png")
# Inno wizard images
side = Image.new("RGB", (164, 314), (16, 52, 70)); side.paste(img.resize((140, 140), Image.LANCZOS), (12, 40), img.resize((140, 140), Image.LANCZOS))
side.save(ROOT / "launcher/assets/wizard.bmp")
img.convert("RGB").resize((55, 55), Image.LANCZOS).save(ROOT / "launcher/assets/wizard_small.bmp")
print("icons ok")
