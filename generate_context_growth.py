"""
Generate assets/context_growth.png, the LLM context-window growth chart.

A log-scale climb of the largest context windows from 2020 to 2026, labelled with
the model that set each mark. Cato-branded palette, full-bleed dark-teal background
so it blends seamlessly when placed edge-to-edge on a slide.

Run: .venv/bin/python generate_context_growth.py  ->  assets/context_growth.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

# ── Cato theme colours (match build_presentation.py / generate_agent_diagram.py)
BG     = "#182D29"   # dark teal, same as the Cato dark slide background
FG     = "#F6F6F7"
ACCENT = "#38D9A7"   # mint, the growth line
SKY    = "#55CBF2"   # point labels
GOLD   = "#FEC756"   # highlight today's frontier
MUTED  = "#B5CBCB"   # grid / axes
GRID   = "#2E4A44"
FAM    = "DejaVu Sans"

# (year as decimal, tokens, label, label-offset in points (dx, dy), ha, va)
POINTS = [
    (2020.5, 2_048,     "GPT-3\n2K",          (10, -6),  "left",  "center"),
    (2022.9, 4_096,     "GPT-3.5\n4K",        (10, -6),  "left",  "center"),
    (2023.2, 8_192,     "GPT-4\n8K",          (8, 18),   "left",  "bottom"),
    (2023.9, 128_000,   "GPT-4 Turbo\n128K",  (10, -10), "left",  "top"),
    (2024.2, 1_000_000, "Gemini 1.5\n1M",     (-10, 16), "right", "bottom"),
    (2025.4, 2_000_000, "Gemini 2.5\n2M",     (-12, -8), "right", "top"),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

xs = [p[0] for p in POINTS]
ys = [p[1] for p in POINTS]

ax.set_yscale("log")
ax.set_xlim(2019.7, 2026.1)
ax.set_ylim(1_000, 10_000_000)

# Growth line
ax.plot(xs, ys, color=ACCENT, linewidth=3.5, zorder=3,
        solid_capstyle="round")
# Points (highlight the latest frontier in gold)
ax.scatter(xs[:-1], ys[:-1], s=140, color=ACCENT, zorder=4,
           edgecolors=BG, linewidths=2)
ax.scatter([xs[-1]], [ys[-1]], s=320, color=GOLD, zorder=5,
           edgecolors=BG, linewidths=2, marker="*")

for x, y, label, (dx, dy), ha, va in POINTS:
    color = GOLD if y == 2_000_000 else FG
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(dx, dy),
                ha=ha, va=va, color=color, fontsize=17, fontweight="bold",
                fontfamily=FAM, linespacing=1.1)

# Axes styling
ax.set_xticks([2020, 2021, 2022, 2023, 2024, 2025, 2026])
ax.tick_params(axis="x", colors=MUTED, labelsize=16, length=0)
ax.yaxis.set_major_locator(FixedLocator([1e3, 1e4, 1e5, 1e6, 1e7]))
ax.yaxis.set_major_formatter(FixedFormatter(["1K", "10K", "100K", "1M", "10M"]))
ax.tick_params(axis="y", colors=MUTED, labelsize=16, length=0)
ax.set_ylabel("context window  (tokens)", color=MUTED, fontsize=17,
              fontfamily=FAM, labelpad=12)

ax.grid(True, which="major", axis="y", color=GRID, linewidth=1, alpha=0.7)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.subplots_adjust(left=0.085, right=0.975, top=0.95, bottom=0.08)
path = os.path.join(OUT, "context_growth.png")
fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
plt.close(fig)
print(f"Saved: {path}")
