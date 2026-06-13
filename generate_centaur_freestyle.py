"""
Generate the "2 amateurs + 3 home PCs" illustration for the Kasparov / centaur
slide: two simple human glyphs above three monitor glyphs, each screen showing a
chess knight. Drawn in the deck palette, transparent, so it sits on the dark slide.

This is an on-brand vector illustration (like the other generated diagrams),
not a downloaded photo: there is no freely licensed photo of the actual 2005
freestyle winners, and an icon reads more clearly at slide size anyway.

Run: .venv/bin/python generate_centaur_freestyle.py  ->  assets/freestyle_team.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon

FG       = "#F6F6F7"
ACCENT   = "#38D9A7"
SKY      = "#55CBF2"
GOLD     = "#FEC756"
MUTED    = "#B5CBCB"
DARKFILL = "#0E1A17"
FAM      = "DejaVu Sans"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)


def person(ax, cx, cy, color):
    # head
    ax.add_patch(Circle((cx, cy + 0.95), 0.52, facecolor=color,
                         edgecolor="none", zorder=3))
    # shoulders / torso as a rounded "bust"
    ax.add_patch(FancyBboxPatch((cx - 0.95, cy - 0.95), 1.9, 1.5,
                                boxstyle="round,pad=0.02,rounding_size=0.6",
                                facecolor=color, edgecolor="none", zorder=2))


def monitor(ax, cx, cy):
    w, h = 2.5, 1.85
    # screen
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor=DARKFILL, edgecolor=SKY, linewidth=2.4,
                                zorder=2))
    # chess knight on the screen
    ax.text(cx, cy + 0.02, "♞", color=GOLD, fontsize=34, ha="center",
            va="center", fontfamily=FAM, zorder=3)
    # stand
    ax.add_patch(Polygon([(cx - 0.55, cy - h / 2 - 0.55), (cx + 0.55, cy - h / 2 - 0.55),
                          (cx + 0.28, cy - h / 2), (cx - 0.28, cy - h / 2)],
                         closed=True, facecolor=SKY, edgecolor="none", zorder=1))


fig, ax = plt.subplots(figsize=(8.6, 5.4))
fig.patch.set_alpha(0.0)
ax.set_facecolor("none")
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.set_aspect("equal")
ax.axis("off")
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Two amateurs on top.
person(ax, 5.6, 7.5, FG)
person(ax, 10.4, 7.5, FG)
ax.text(8.0, 7.4, "+", color=MUTED, fontsize=40, ha="center", va="center",
        fontfamily=FAM, fontweight="bold")

# Three home PCs on the bottom row.
for mx in (3.2, 8.0, 12.8):
    monitor(ax, mx, 2.7)

out = os.path.join(OUT, "freestyle_team.png")
fig.savefig(out, dpi=150, transparent=True)
plt.close(fig)
print(f"Saved: {out}")
