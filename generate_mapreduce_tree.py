"""
Generate the map-reduce "deterministic agent" fan-in tree as STAGED, transparent
layers so the slide can reveal it one click at a time:

  mapreduce_l1.png  the book box (shown first)
  mapreduce_l2.png  + the chapters (and the arrows into them)
  mapreduce_l3.png  + the MAP step: one LLM per chapter, and its summary
  mapreduce_l4.png  + the REDUCE step: one LLM over the summaries, final summary

Each layer is transparent and uses the same 16x9 extent, so stacking them at the
same position on the slide rebuilds the whole tree. Arrows live in the same layer
as the box they point to. Box fills are opaque so they read on the dark slide.

Run: .venv/bin/python generate_mapreduce_tree.py  ->  assets/mapreduce_l*.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FG     = "#F6F6F7"
ACCENT = "#38D9A7"   # mint, LLM calls
SKY    = "#55CBF2"   # data boxes (chapters, summaries)
GOLD   = "#FEC756"   # final result
LOOP_C = "#B5CBCB"   # arrows
MUTED  = "#B5CBCB"
BOX_FILL = "#22403A"
DARKFILL = "#0E1A17"
FAM    = "DejaVu Sans"

VW, VH = 16.0, 9.0
COLS = np.linspace(2.9, 13.1, 4)   # 4 chapter columns
CX = 8.0                            # canvas centre

BOOK_Y   = 8.05
CHAP_Y   = 6.35
MAP_Y    = 4.85
SUM_Y    = 3.45
REDUCE_Y = 1.95
FINAL_Y  = 0.7

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)


def new_fig():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    ax.set_xlim(0, VW)
    ax.set_ylim(0, VH)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def box(ax, cx, cy, w, h, label, color, fontsize=15, fill=BOX_FILL):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.06", linewidth=2,
        edgecolor=color, facecolor=fill))
    ax.text(cx, cy, label, color=color, fontsize=fontsize, fontweight="bold",
            ha="center", va="center", fontfamily=FAM, linespacing=1.0)


def arrow(ax, x0, y0, x1, y1, color=LOOP_C, lw=2.2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=18))


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, transparent=True)
    plt.close(fig)
    print(f"Saved: {path}")


# ── Layer 1: the book ────────────────────────────────────────────────────────
fig, ax = new_fig()
box(ax, CX, BOOK_Y, 5.4, 1.0, "A Song of Ice and Fire", FG, fontsize=18, fill=DARKFILL)
save(fig, "mapreduce_l1.png")

# ── Layer 2: split into chapters (arrows + chapter boxes) ────────────────────
fig, ax = new_fig()
for x in COLS:
    arrow(ax, CX, BOOK_Y - 0.5, x, CHAP_Y + 0.45)
    box(ax, x, CHAP_Y, 2.35, 0.85, "chapter", SKY, fontsize=15)
save(fig, "mapreduce_l2.png")

# ── Layer 3: MAP, one LLM per chapter -> a summary ───────────────────────────
fig, ax = new_fig()
for x in COLS:
    arrow(ax, x, CHAP_Y - 0.43, x, MAP_Y + 0.32)
    box(ax, x, MAP_Y, 1.5, 0.62, "LLM", ACCENT, fontsize=15)
    arrow(ax, x, MAP_Y - 0.32, x, SUM_Y + 0.43)
    box(ax, x, SUM_Y, 2.35, 0.85, "summary", SKY, fontsize=15)
ax.text(0.35, MAP_Y, "MAP\nsummarize\neach chunk", color=MUTED, fontsize=15,
        ha="left", va="center", fontfamily=FAM, style="italic", linespacing=1.15)
save(fig, "mapreduce_l3.png")

# ── Layer 4: REDUCE, one LLM over the summaries -> final summary ─────────────
fig, ax = new_fig()
for x in COLS:
    arrow(ax, x, SUM_Y - 0.43, CX, REDUCE_Y + 0.32)
box(ax, CX, REDUCE_Y, 1.7, 0.66, "LLM", ACCENT, fontsize=16)
arrow(ax, CX, REDUCE_Y - 0.34, CX, FINAL_Y + 0.42)
box(ax, CX, FINAL_Y, 4.2, 0.82, "final summary", GOLD, fontsize=17, fill=DARKFILL)
ax.text(0.35, REDUCE_Y, "REDUCE\nsummarize the\nsummaries", color=MUTED,
        fontsize=15, ha="left", va="center", fontfamily=FAM, style="italic",
        linespacing=1.15)
save(fig, "mapreduce_l4.png")
