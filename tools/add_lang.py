#!/usr/bin/env python3
"""Merge RU/EN strings into pack/kubejs/assets/arkhaven/lang/{ru_ru,en_us}.json.
Usage from code: add({"key": ("рус", "eng"), ...}). Running the script adds alchemy strings."""
import json
from pathlib import Path

LANG = Path(__file__).resolve().parent.parent / "pack/kubejs/assets/arkhaven/lang"


def add(pairs):
    for i, loc in enumerate(("ru_ru", "en_us")):
        f = LANG / f"{loc}.json"
        d = json.loads(f.read_text("utf8")) if f.exists() else {}
        for k, v in pairs.items():
            d[k] = v[i]
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", "utf8")


def alchemy():
    names = {"quiet": ("Тишина", "Quiet"), "sea_wolf": ("Морской волк", "Sea Wolf"), "fertility": ("Плодородие", "Fertility"),
             "beast_trust": ("Звериное доверие", "Beast Trust"), "forge_heat": ("Жар горна", "Forge Heat"),
             "clean_breath": ("Чистое дыхание", "Clean Breath"), "lead_blood": ("Свинцовая кровь", "Lead Blood"),
             "star_sight": ("Звёздное зрение", "Star Sight")}
    desc = {"quiet": ("Враждебные мобы не замечают вас, пока вы не ударите.", "Hostile mobs ignore you until you strike."),
            "fertility": ("Посевы вокруг растут быстрее.", "Crops around you grow faster."),
            "beast_trust": ("Детёныши рядом растут быстрее.", "Young animals nearby grow up faster."),
            "clean_breath": ("Снимает яд, тошноту, иссушение и слепоту от смога и кислотных осадков.", "Clears poison, nausea, wither and blindness from smog and acid rain."),
            "lead_blood": ("Постепенно выводит радиацию из тела.", "Slowly flushes radiation from your body."),
            "star_sight": ("Подсвечивает враждебных существ в радиусе 48 блоков.", "Highlights hostile creatures within 48 blocks.")}
    forms = {"potion": ("Зелье «%s»", "Potion of %s"), "splash_potion": ("Взрывное зелье «%s»", "Splash Potion of %s"),
             "lingering_potion": ("Оседающее зелье «%s»", "Lingering Potion of %s"), "tipped_arrow": ("Стрела «%s»", "Arrow of %s")}
    pairs = {}
    for k, (ru, en) in names.items():
        if k in desc:
            pairs[f"effect.arkhaven.{k}"] = (ru, en)
            pairs[f"effect.arkhaven.{k}.description"] = desc[k]
        for t, (rf, ef) in forms.items():
            pairs[f"item.minecraft.{t}.effect.{k}"] = (rf % ru, ef % en)
    add(pairs)


if __name__ == "__main__":
    alchemy()
    print("lang updated")
