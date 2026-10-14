#!/usr/bin/env python3
"""Generate 16x16 item textures for arkhaven:* KubeJS items -> pack/kubejs/assets/arkhaven/textures/item/*.png
Shapes are hand-drawn masks; colours are per item. Re-runnable."""
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "pack/kubejs/assets/arkhaven/textures/item"

SHAPES = {
    "ingot": [
        "................", "................", "................", "................",
        "................", ".....hhhhhhh....", "....hlllllllh...", "...hllmmmmmlh...",
        "..hlmmmmmmmmdh..", "..hmmmmmmmmdd...", "..dddddddddd....", "................",
        "................", "................", "................", "................"],
    "dust": [
        "................", "................", "................", "................",
        "................", "......l.........", ".....lml..l.....", "....lmmml.......",
        "...lmmmmmd..l...", "..lmmmmmmmd.....", ".lmmmmmmmmmd....", ".dddddddddddd...",
        "................", "................", "................", "................"],
    "crystal": [
        "................", ".......h........", "......hlh.......", "......hlmh......",
        ".....hlmmh......", ".....hlmmdh.....", "....hlmmmdh.....", "....hlmmmddh....",
        "....hlmmmddh....", "....hlmmmddh....", ".....hlmmdh.....", ".....hlmmdh.....",
        "......hlmh......", "......hddh......", ".......hh.......", "................"],
    "cloth": [
        "................", "................", "...hhhhhhhhhh...", "..hllllllllllh..",
        "..hlmmmmmmmmlh..", "..hlmdmmmmdmlh..", "..hlmmmmmmmmlh..", "..hlmmmdmmmmlh..",
        "..hlmmmmmmdmlh..", "..hlmdmmmmmmlh..", "..hlmmmmmmmmlh..", "..hddddddddddh..",
        "...hhhhhhhhhh...", "................", "................", "................"],
    "bottle": [
        "................", "......hhhh......", "......hddh......", ".......hh.......",
        "......hllh......", ".....hlmmlh.....", "....hlmmmmlh....", "...hlmmmmmmdh...",
        "...hlmmmmmmdh...", "...hlmmmmmmdh...", "...hlmmmmmmdh...", "....hmmmmmdh....",
        ".....hhhhhh.....", "................", "................", "................"],
    "orb": [
        "................", "................", ".....hhhhhh.....", "....hllllllh....",
        "...hllmmmmmdh...", "..hllmmmmmmmdh..", "..hlmmmlmmmmdh..", "..hlmmllmmmmdh..",
        "..hlmmmmmmmmdh..", "..hlmmmmmmmddh..", "...hmmmmmmddh...", "....hddddddh....",
        ".....hhhhhh.....", "................", "................", "................"],
    "fish": [
        "................", "................", "................", "........hhh.....",
        "......hhlllh..h.", "....hhllmmmmhhlh", "...hllmmmmmmmlmh", "..hlhmmmmmmmmmh.",
        "..hlmmmmmmmmdlmh", "...hdmmmmmmddhdh", "....hhddddddh..h", "......hhhhhh....",
        "................", "................", "................", "................"],
    "plate": [
        "................", "................", "..hhhhhhhhhhhh..", "..hllllllllllh..",
        "..hlmmmmmmmmdh..", "..hlmhmmmmhmdh..", "..hlmmmmmmmmdh..", "..hlmmmmmmmmdh..",
        "..hlmmmmmmmmdh..", "..hlmhmmmmhmdh..", "..hlmmmmmmmmdh..", "..hddddddddddh..",
        "..hhhhhhhhhhhh..", "................", "................", "................"],
    "heart": [
        "................", "................", "...hhhh..hhhh...", "..hllllhhllmmh..",
        ".hllmmmllmmmmdh.", ".hlmmmmmmmmmmdh.", ".hlmmmmmmmmmmdh.", ".hlmmmmmmmmmmdh.",
        "..hmmmmmmmmmdh..", "...hmmmmmmmdh...", "....hmmmmmdh....", ".....hmmmdh.....",
        "......hmdh......", ".......hh.......", "................", "................"],
    "charm": [
        "................", ".......hh.......", "......h..h......", "......h..h......",
        ".......hh.......", "......hllh......", ".....hlmmlh.....", "....hlmmmmdh....",
        "....hlmlmmdh....", "....hlmmmmdh....", ".....hmmmdh.....", "......hmdh......",
        ".......hh.......", "................", "................", "................"],
}


def shade(rgb, f):
    return tuple(max(0, min(255, int(c * f))) for c in rgb)


ITEMS = {
    "waxed_canvas": ("cloth", (222, 196, 120)),
    "aero_lubricant": ("bottle", (196, 150, 52)),
    "dragon_plating": ("plate", (140, 46, 52)),
    "ward_crystal_t1": ("crystal", (120, 200, 230)),
    "ward_crystal_t2": ("crystal", (170, 120, 240)),
    "ward_crystal_t3": ("crystal", (250, 214, 110)),
    "meteoric_dust": ("dust", (110, 96, 120)),
    "meteoric_iron_ingot": ("ingot", (150, 140, 170)),
    "exotic_matter": ("orb", (70, 230, 200)),
    "citadel_heart": ("heart", (230, 190, 90)),
    "star_carp": ("fish", (240, 200, 90)),
    "travelers_charm": ("charm", (110, 190, 140)),
    "rift_shard": ("crystal", (150, 60, 200)),
}


def draw(shape, base):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pal = {"h": shade(base, 0.35) + (255,), "d": shade(base, 0.65) + (255,), "m": tuple(base) + (255,),
           "l": shade(base, 1.35) + (255,)}
    for y, row in enumerate(SHAPES[shape]):
        for x, ch in enumerate(row):
            if ch in pal:
                img.putpixel((x, y), pal[ch])
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (shape, col) in ITEMS.items():
        draw(shape, col).save(OUT / f"{name}.png")
    print(f"{len(ITEMS)} textures -> {OUT}")
