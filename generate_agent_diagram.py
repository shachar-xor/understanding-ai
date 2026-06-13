"""
Generate agent loop diagrams as PNGs using matplotlib — Cato-branded palette.
Produces 4 progressive images into assets/:
  agent_diagram_1.png  — LLM only
  agent_diagram_2.png  — LLM + Tools
  agent_diagram_3.png  — LLM + Tools + Loop
  agent_diagram_4.png  — full diagram (entry, exit, decision)

Run: .venv/bin/python generate_agent_diagram.py
The dark-teal background matches the Cato dark slide background so the PNGs
blend seamlessly when placed full-bleed on a slide.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Ellipse, FancyBboxPatch  # noqa: F401
import os

# ── Cato theme colours (match build_presentation.py tokens) ──────────────────
BG       = "#182D29"   # dark teal — same as Cato dark slide background
FG       = "#F6F6F7"
ACCENT   = "#38D9A7"   # mint — LLM box / user input
TOOLS_C  = "#55CBF2"   # sky blue — Tools box
LOOP_C   = "#B5CBCB"   # grey-blue — loop oval + arrows
MUTED    = "#B5CBCB"
DEC_C    = "#B5CBCB"
OUT_C    = "#F6F6F7"
BOX_FILL = "#22403A"   # slightly lighter teal for box interiors

VW, VH = 16.0, 9.0

OX, OY   = 7.5, 4.6
RX, RY   = 4.2, 2.2
BOX_W, BOX_H = 2.6, 1.1

LLM_CX = OX - RX
LLM_CY = OY
TL_CX  = OX + RX
TL_CY  = OY


def new_fig():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, VW)
    ax.set_ylim(0, VH)
    ax.set_aspect("auto")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def draw_box(ax, cx, cy, label, color, fontsize=20):
    rect = FancyBboxPatch(
        (cx - BOX_W/2, cy - BOX_H/2), BOX_W, BOX_H,
        boxstyle="round,pad=0.08",
        linewidth=2, edgecolor=color,
        facecolor=BOX_FILL,
    )
    ax.add_patch(rect)
    ax.text(cx, cy, label, color=color, fontsize=fontsize,
            fontweight="bold", ha="center", va="center",
            fontfamily="DejaVu Sans")


LOOP_LW = 3.5


def draw_oval(ax):
    ellipse = Ellipse(
        (OX, OY), width=2*RX, height=2*RY,
        linewidth=LOOP_LW, edgecolor=LOOP_C, facecolor="none",
    )
    ax.add_patch(ellipse)


def draw_loop_arrows(ax):
    def pt(deg):
        r = np.radians(deg)
        return OX + RX * np.cos(r), OY + RY * np.sin(r)

    for angle, dangle in [(100, 10), (220, 10), (320, 10)]:
        x0, y0 = pt(angle - dangle)
        x1, y1 = pt(angle + dangle)
        ax.annotate("",
            xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>", color=LOOP_C,
                            lw=LOOP_LW, mutation_scale=22,
                            connectionstyle="arc3,rad=0.0"))


def draw_user_input(ax):
    ex = LLM_CX
    ey = LLM_CY + BOX_H / 2
    sx = ex
    sy = ey + 1.8
    ax.annotate("",
        xy=(ex, ey), xytext=(sx, sy),
        arrowprops=dict(arrowstyle="-|>", color=ACCENT,
                        lw=2.5, mutation_scale=20))
    ax.text(sx, sy + 0.2, "User Input",
            color=ACCENT, fontsize=16, fontweight="bold",
            ha="center", va="bottom", fontfamily="DejaVu Sans")


def draw_decision(ax):
    ax.text(OX, OY - RY + 0.35, "done?",
            color=DEC_C, fontsize=16, ha="center", va="bottom",
            fontfamily="DejaVu Sans", style="italic")


def draw_agent_output(ax):
    bx = OX
    by = OY - RY
    ex = bx + 4.0
    ey = by
    ax.annotate("",
        xy=(ex, ey), xytext=(bx, by),
        arrowprops=dict(arrowstyle="-|>", color=OUT_C,
                        lw=2.5, mutation_scale=20))
    ax.text(ex + 0.2, ey, "Agent Output",
            color=OUT_C, fontsize=16, fontweight="bold",
            ha="left", va="center", fontfamily="DejaVu Sans")


def save(fig, path):
    fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"Saved: {path}")


OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

# ── Diagram 1: LLM only ──────────────────────────────────────────────────────
fig, ax = new_fig()
draw_box(ax, LLM_CX, LLM_CY, "LLM", ACCENT, fontsize=22)
save(fig, os.path.join(OUT, "agent_diagram_1.png"))

# ── Diagram 2: LLM + Tools ───────────────────────────────────────────────────
fig, ax = new_fig()
draw_box(ax, LLM_CX, LLM_CY, "LLM",   ACCENT,   fontsize=22)
draw_box(ax, TL_CX,  TL_CY,  "Tools", TOOLS_C,  fontsize=22)
save(fig, os.path.join(OUT, "agent_diagram_2.png"))

# ── Diagram 3: LLM + Tools + Loop ────────────────────────────────────────────
fig, ax = new_fig()
draw_oval(ax)
draw_loop_arrows(ax)
draw_box(ax, LLM_CX, LLM_CY, "LLM",   ACCENT,   fontsize=22)
draw_box(ax, TL_CX,  TL_CY,  "Tools", TOOLS_C,  fontsize=22)
save(fig, os.path.join(OUT, "agent_diagram_3.png"))

# ── Diagram 4: Full ──────────────────────────────────────────────────────────
fig, ax = new_fig()
draw_oval(ax)
draw_loop_arrows(ax)
draw_box(ax, LLM_CX, LLM_CY, "LLM",   ACCENT,   fontsize=22)
draw_box(ax, TL_CX,  TL_CY,  "Tools", TOOLS_C,  fontsize=22)
draw_user_input(ax)
draw_decision(ax)
draw_agent_output(ax)
save(fig, os.path.join(OUT, "agent_diagram_4.png"))

# ── Loop without tools: one LLM feeding its own output back in ───────────────
fig, ax = new_fig()
draw_oval(ax)
draw_loop_arrows(ax)
draw_box(ax, OX, OY, "LLM", ACCENT, fontsize=22)   # single, centred box
# User input arrow into the top of the box
ax.annotate("",
    xy=(OX, OY + BOX_H / 2), xytext=(OX, OY + BOX_H / 2 + 1.8),
    arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.5, mutation_scale=20))
ax.text(OX, OY + BOX_H / 2 + 2.0, "Your input",
        color=ACCENT, fontsize=16, fontweight="bold",
        ha="center", va="bottom", fontfamily="DejaVu Sans")
# Loop caption + exit decision + output
ax.text(OX, OY + RY + 0.18, "feeds its own output back in",
        color=LOOP_C, fontsize=15, ha="center", va="bottom",
        style="italic", fontfamily="DejaVu Sans")
draw_decision(ax)
draw_agent_output(ax)
save(fig, os.path.join(OUT, "agent_loop_notools.png"))
