"""
Build the two Game of Thrones images for the "does not fit" slide:

  assets/got_throne.jpg   a real photo of the Iron Throne, cropped to the throne
                          and its "GAME OF THRONES" base. Source: Wikimedia Commons
                          "Game of Thrones throne model.jpg" (CC BY-SA), a recognizable
                          replica everyone associates with the TV show.
  assets/asoiaf_books.png a clean stylized stack of the five A Song of Ice and Fire
                          books (drawn, transparent). Swap in a real photo at this
                          path if you prefer one.

Run: .venv/bin/python generate_got_assets.py
"""

import os
import urllib.request
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

THRONE_SRC = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
              "Game_of_Thrones_throne_model.jpg")
THRONE_CACHE = "/tmp/got_throne_src.jpg"
FAM = "DejaVu Sans"


def make_throne():
    if not os.path.exists(THRONE_CACHE):
        req = urllib.request.Request(THRONE_SRC,
                                     headers={"User-Agent": "understanding-ai-deck/1.0"})
        with urllib.request.urlopen(req) as r, open(THRONE_CACHE, "wb") as f:
            f.write(r.read())
    im = Image.open(THRONE_CACHE).convert("RGB")
    w, h = im.size
    # Crop out the ceiling and most of the side floor, keep throne + GoT base.
    box = (int(0.07 * w), int(0.11 * h), int(0.94 * w), int(0.995 * h))
    im = im.crop(box)
    # Downscale so the deck stays light.
    scale = 1100 / max(im.size)
    if scale < 1:
        im = im.resize((round(im.size[0] * scale), round(im.size[1] * scale)),
                       Image.LANCZOS)
    out = os.path.join(OUT, "got_throne.jpg")
    im.save(out, quality=88)
    print(f"Saved: {out}")


def make_books():
    # Five spines stacked into a tidy pile, jeweled fantasy palette.
    books = [
        ("A Game of Thrones",   7.2, 5.05, "#7C2B2B"),
        ("A Clash of Kings",    6.5, 5.35, "#2E4A66"),
        ("A Storm of Swords",   6.9, 4.85, "#B8862E"),
        ("A Feast for Crows",   6.1, 5.25, "#3A5A40"),
        ("A Dance with Dragons", 6.6, 4.95, "#4A3A5A"),
    ]
    bh, gap, y0 = 1.18, 0.16, 1.5

    fig, ax = plt.subplots(figsize=(8.4, 7.4))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    ax.set_xlim(0.8, 9.2)
    ax.set_ylim(1.0, 8.4)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    for i, (title, w, cx, color) in enumerate(books):
        yb = y0 + i * (bh + gap)
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2, yb), w, bh, boxstyle="round,pad=0.02",
            linewidth=1.5, edgecolor="#0E1A17", facecolor=color))
        # thin page sliver along the bottom edge to suggest pages
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2 + 0.12, yb + 0.06), w - 0.24, 0.14,
            boxstyle="round,pad=0.0", linewidth=0, facecolor="#E8E0CF"))
        ax.text(cx, yb + bh / 2 + 0.08, title, color="#F6F6F7", fontsize=15,
                fontweight="bold", ha="center", va="center", fontfamily=FAM)

    out = os.path.join(OUT, "asoiaf_books.png")
    fig.savefig(out, dpi=150, transparent=True)
    plt.close(fig)
    print(f"Saved: {out}")


make_throne()
make_books()
