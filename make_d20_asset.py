"""
Build assets/d20.png from a real photograph of a translucent green d20.

Source: Wikimedia Commons "A bright green twenty-sided die (d20).jpg", released
CC0 1.0 (public domain, no attribution required). The die is photographed on a
wooden table; this script cuts it off the background (green-vs-wood separates by
the G-R channel difference, with interior number holes preserved by a flood fill)
so it floats transparently on the dark Cato slide.

Run: .venv/bin/python make_d20_asset.py  ->  assets/d20.png
"""

import os
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = ("https://upload.wikimedia.org/wikipedia/commons/d/d2/"
       "A_bright_green_twenty-sided_die_%28d20%29.jpg")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "d20.png")
CACHE = os.path.join("/tmp", "d20_green_src.jpg")


def fetch():
    if not os.path.exists(CACHE):
        req = urllib.request.Request(SRC, headers={"User-Agent": "understanding-ai-deck"})
        with urllib.request.urlopen(req) as r, open(CACHE, "wb") as f:
            f.write(r.read())
    return CACHE


def cut(path):
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im).astype(np.int16)
    R, G = arr[:, :, 0], arr[:, :, 1]

    # Bright green die (G > R); brown wood (R > G); white numbers are near-neutral
    # and become interior holes that the flood fill restores.
    mask = np.where((G - R) > 12, 255, 0).astype(np.uint8)
    mimg = Image.fromarray(mask, "L").filter(ImageFilter.MedianFilter(5))

    w, h = mimg.size
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
               (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        ImageDraw.floodfill(mimg, xy, 128, thresh=0)

    fg = np.asarray(mimg) != 128
    alpha = Image.fromarray(np.where(fg, 255, 0).astype(np.uint8), "L")
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))

    out = im.convert("RGBA")
    out.putalpha(alpha)

    ys, xs = np.where(np.asarray(alpha) > 30)
    pad = 40
    y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(w, xs.max() + pad)
    out = out.crop((x0, y0, x1, y1))

    scale = 800 / max(out.size)
    out = out.resize((round(out.size[0] * scale), round(out.size[1] * scale)), Image.LANCZOS)
    return out


os.makedirs(os.path.dirname(OUT), exist_ok=True)
cut(fetch()).save(OUT)
print(f"Saved: {OUT}")
