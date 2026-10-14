#!/usr/bin/env python3
"""Title-screen branding via KubeJS assets (they override vanilla): ARKHAVEN logo, empty edition strip, RU/EN splashes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pack/kubejs/assets/minecraft"


def font(size):
    for f in ("C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def logo():
    W, H = 1024, 256
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(170)
    text = "ARKHAVEN"
    box = ImageDraw.Draw(img).textbbox((0, 0), text, font=f)
    x, y = (W - (box[2] - box[0])) // 2 - box[0], (H - (box[3] - box[1])) // 2 - box[1] - 10
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x + 8, y + 10), text, font=f, fill=(10, 20, 40, 220))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(4)))
    # gold gradient text with dark outline
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((x, y), text, font=f, fill=255)
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for row in range(H):
        t = row / H
        gd.line([(0, row), (W, row)], fill=(int(255 - 40 * t), int(222 - 90 * t), int(140 - 100 * t), 255))
    outline = mask.filter(ImageFilter.MaxFilter(9))
    img.paste((30, 40, 60, 255), (0, 0), outline)
    img.paste(grad, (0, 0), mask)
    p = OUT / "textures/gui/title/minecraft.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)
    Image.new("RGBA", (128, 16), (0, 0, 0, 0)).save(p.with_name("edition.png"))


SPLASHES = [
    "Дом для всех!", "Мир спокойный — опасность по желанию!", "Повар, маг и инженер заходят в таверну…",
    "Сыр, который ждал!", "Небо зовёт!", "Метеориты не чаще раза в три дня!", "Кухня на шестерёнках!",
    "Не забудь покормить пчёл!", "Звёздный карп существует!", "Оберег заправлен?", "Дирижабль — это дом!",
    "Home for everyone!", "Calm world, danger on demand!", "The sky is calling!", "Bring cheese to the mage!",
]


def splashes():
    p = OUT / "texts/splashes.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(SPLASHES) + "\n", "utf8")


if __name__ == "__main__":
    logo()
    splashes()
    print("branding ok")
