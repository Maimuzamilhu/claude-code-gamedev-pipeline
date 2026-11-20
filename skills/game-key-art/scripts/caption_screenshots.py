"""Add consistent caption banners to gameplay screenshots.

  python caption_screenshots.py <in_dir> <out_dir> <captions.txt> [--font F.ttf] [--accent "#D8261E"]
                                [--size 1920x1080] [--top]

captions.txt: one caption per line, matched to the images in <in_dir> sorted by name.
Each frame is fitted into the target size, a dark banner with the caption (centred, upper case)
is added at the bottom (or --top) with a thin accent line, and PNG + JPG are written.
Needs: pip install pillow
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def fit(img, w, h):
    s = max(w / img.width, h / img.height)                     # cover, then centre-crop
    img = img.resize((int(img.width * s + 0.5), int(img.height * s + 0.5)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def main(src, dst, captions_file):
    w, h = (int(v) for v in arg("--size", "1920x1080").split("x"))
    accent = arg("--accent", "#D8261E")
    font_path = arg("--font", None)
    top = "--top" in sys.argv
    band = int(h * 0.13)
    size = int(band * 0.52)
    font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default(size)
    caps = [c.strip() for c in open(captions_file, encoding="utf-8") if c.strip()]
    files = sorted(f for f in os.listdir(src) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    os.makedirs(dst, exist_ok=True)
    for i, (f, cap) in enumerate(zip(files, caps), 1):
        img = fit(Image.open(os.path.join(src, f)).convert("RGB"), w, h).convert("RGBA")
        over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(over)
        y0 = 0 if top else h - band
        d.rectangle((0, y0, w, y0 + band), fill=(10, 10, 12, 215))
        line_y = y0 + band - 3 if top else y0
        d.rectangle((0, line_y, w, line_y + 3), fill=accent)
        img = Image.alpha_composite(img, over)
        d = ImageDraw.Draw(img)
        text = cap.upper()
        # centred in the banner: "mm" anchors the text's middle at the point
        d.text((w / 2, y0 + band / 2), text, font=font, fill=(240, 240, 240), anchor="mm")
        name = "screenshot_%02d" % i
        img.convert("RGB").save(os.path.join(dst, name + ".png"))
        img.convert("RGB").save(os.path.join(dst, name + ".jpg"), quality=90)
        print(name, "-", text)
    if len(caps) < len(files):
        print("note: %d images had no caption line and were skipped" % (len(files) - len(caps)))


if __name__ == "__main__":
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags_with_values = {arg(n, None) for n in ("--font", "--accent", "--size")}
    pos = [a for a in pos if a not in flags_with_values]
    if len(pos) < 3:
        print(__doc__)
    else:
        main(pos[0], pos[1], pos[2])
