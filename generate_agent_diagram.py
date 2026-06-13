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
from matplotlib.patches import FancyArrowPatch, Ellipse, FancyBboxPatch, Polygon  # noqa: F401
import os

# ── Cato theme colours (match build_presentation.py tokens) ──────────────────
BG       = "#182D29"   # dark teal, same as Cato dark slide background
FG       = "#F6F6F7"
ACCENT   = "#38D9A7"   # mint, LLM box / user input
TOOLS_C  = "#55CBF2"   # sky blue, Tools / data boxes
GOLD     = "#FEC756"   # gold, decision diamond
LOOP_C   = "#B5CBCB"   # grey-blue, loop oval + arrows
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


# ── Flowchart helpers (directed loops with a decision diamond) ───────────────
def flow_canvas(figsize, vw, vh):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, vw)
    ax.set_ylim(0, vh)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def flow_box(ax, cx, cy, w, h, label, color, fontsize=18, fill=BOX_FILL):
    ax.add_patch(FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h, boxstyle="round,pad=0.06",
        linewidth=2.4, edgecolor=color, facecolor=fill))
    ax.text(cx, cy, label, color=color, fontsize=fontsize, fontweight="bold",
            ha="center", va="center", fontfamily="DejaVu Sans", linespacing=1.0)


def flow_diamond(ax, cx, cy, w, h, label, color, fontsize=15, fill=BOX_FILL):
    pts = [(cx, cy + h/2), (cx + w/2, cy), (cx, cy - h/2), (cx - w/2, cy)]
    ax.add_patch(Polygon(pts, closed=True, linewidth=2.4,
                         edgecolor=color, facecolor=fill))
    ax.text(cx, cy, label, color=color, fontsize=fontsize, fontweight="bold",
            ha="center", va="center", fontfamily="DejaVu Sans", linespacing=1.0)


def flow_arrow(ax, x0, y0, x1, y1, color=LOOP_C, lw=2.6, head=True):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>" if head else "-",
                                color=color, lw=lw, mutation_scale=22))


def flow_label(ax, x, y, text, color=MUTED, fontsize=14, style="italic",
               ha="center", va="center"):
    ax.text(x, y, text, color=color, fontsize=fontsize, ha=ha, va=va,
            fontfamily="DejaVu Sans", style=style)


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

# ── Diagram 4: the agent loop, LLM + Tools ───────────────────────────────────
# A real directed loop: your task -> LLM -> done? -> (yes) answer, or
# (no) call a tool -> observation -> back to the LLM.
fig, ax = flow_canvas((16, 6.0), 16, 6.0)
SPINE, CHAN = 4.0, 1.4
# entry
flow_arrow(ax, 3.0, 5.35, 3.0, SPINE + 0.55, color=ACCENT)
flow_label(ax, 3.0, 5.45, "Your task", color=ACCENT, fontsize=16, style="normal",
           va="bottom")
# main spine
flow_box(ax, 3.0, SPINE, 2.4, 1.1, "LLM", ACCENT, fontsize=20)
flow_diamond(ax, 8.5, SPINE, 2.9, 1.6, "done?", GOLD, fontsize=18)
flow_box(ax, 13.2, SPINE, 2.7, 1.1, "answer", FG, fontsize=18)
flow_arrow(ax, 3.0 + 1.2, SPINE, 8.5 - 1.45, SPINE)
flow_arrow(ax, 8.5 + 1.45, SPINE, 13.2 - 1.35, SPINE)
flow_label(ax, (8.5 + 1.45 + 13.2 - 1.35) / 2, SPINE + 0.3, "yes", color=ACCENT,
           fontsize=15, style="normal", va="bottom")
# return channel: routes through a Tools box and brings back an observation
flow_box(ax, 5.75, CHAN, 2.8, 1.1, "Tools", TOOLS_C, fontsize=19)
flow_arrow(ax, 8.5, SPINE - 0.8, 8.5, CHAN, head=False)
flow_arrow(ax, 8.5, CHAN, 5.75 + 1.4, CHAN, color=TOOLS_C)
flow_arrow(ax, 5.75 - 1.4, CHAN, 3.0, CHAN, head=False)
flow_arrow(ax, 3.0, CHAN, 3.0, SPINE - 0.55, color=ACCENT)
flow_label(ax, 8.5 + 0.18, (SPINE - 0.8 + CHAN) / 2, "no", color=GOLD, fontsize=14,
           ha="left")
flow_label(ax, (8.5 + 5.75 + 1.4) / 2, CHAN + 0.22, "call a tool", color=TOOLS_C,
           fontsize=14, style="normal", va="bottom")
flow_label(ax, (3.0 + 5.75 - 1.4) / 2, CHAN + 0.22, "observation", color=MUTED,
           fontsize=14, va="bottom")
save(fig, os.path.join(OUT, "agent_diagram_4.png"))

# ── Loop without tools: the LLM critiques and rewrites its own draft ─────────
# Same skeleton as diagram 4, but the feedback edge has no tool: the model just
# feeds its own draft back in. Wider/shorter so it fits below two lines of text.
fig, ax = flow_canvas((16, 4.1), 16, 4.1)
SPINE, CHAN = 2.55, 0.75
# entry
flow_arrow(ax, 3.0, 3.82, 3.0, SPINE + 0.5, color=ACCENT)
flow_label(ax, 3.0, 3.9, "Your prompt", color=ACCENT, fontsize=15, style="normal",
           va="bottom")
# main spine
flow_box(ax, 3.0, SPINE, 2.2, 1.0, "LLM", ACCENT, fontsize=19)
flow_diamond(ax, 10.4, SPINE, 2.8, 1.5, "good\nenough?", GOLD, fontsize=15)
flow_box(ax, 13.7, SPINE, 2.3, 1.0, "final tweet", FG, fontsize=16)
# the draft is the LLM's output, so it labels the arrow into the check
flow_arrow(ax, 3.0 + 1.1, SPINE, 10.4 - 1.4, SPINE)
flow_label(ax, (3.0 + 1.1 + 10.4 - 1.4) / 2, SPINE + 0.26, "draft", color=TOOLS_C,
           fontsize=14, va="bottom")
flow_arrow(ax, 10.4 + 1.4, SPINE, 13.7 - 1.15, SPINE)
flow_label(ax, (10.4 + 1.4 + 13.7 - 1.15) / 2, SPINE + 0.26, "yes", color=ACCENT,
           fontsize=13, style="normal", va="bottom")
# feedback U: no tool, the draft just goes back to the LLM
flow_arrow(ax, 10.4, SPINE - 0.75, 10.4, CHAN, head=False)
flow_arrow(ax, 10.4, CHAN, 3.0, CHAN, head=False)
flow_arrow(ax, 3.0, CHAN, 3.0, SPINE - 0.5, color=ACCENT)
flow_label(ax, 10.4 + 0.18, (SPINE - 0.75 + CHAN) / 2, "no", color=GOLD,
           fontsize=13, ha="left")
flow_label(ax, 6.7, CHAN + 0.2, "critique + rewrite", color=MUTED, fontsize=14,
           va="bottom")
save(fig, os.path.join(OUT, "agent_loop_notools.png"))
