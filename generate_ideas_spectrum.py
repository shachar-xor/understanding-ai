"""
Generate the "Where ideas live" spectrum graphic as transparent PNGs.

A horizontal spectrum of five levels (WORLD, INDUSTRY, CATO, TEAM, YOU) with three
mechanism bands underneath (LLM weights, Skills, Agents) whose edges FADE to show
partial / overlapping coverage. The bands are separate transparent overlays so the
slide can reveal them one click at a time (same trick as agent_diagram_1..4.png).

Everything is drawn on a full-slide (13.333 x 7.5") transparent canvas so the PNGs
drop onto the Cato dark-teal slide background at Inches(0,0) and align perfectly with
each other and with crisp pptx text/shapes layered on top.

Run: .venv/bin/python generate_ideas_spectrum.py
Produces into assets/:
  ideas_base.png     icons + level labels + sub-labels + guides + baseline
  band_weights.png   mint band, solid over WORLD/INDUSTRY, fading across CATO
  band_skills.png    sky band, peaks across INDUSTRY -> CATO -> TEAM
  band_agents.png    gold band, leans right across CATO -> TEAM -> YOU
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Wedge, Ellipse, FancyBboxPatch

# Cato theme colours (match build_presentation.py tokens), as matplotlib hex
FG       = "#F6F6F7"
ACCENT   = "#38D9A7"   # mint  -> LLM weights
SKY      = "#55CBF2"   # sky   -> Skills
GOLD     = "#FEC756"   # gold  -> Agents
MUTED    = "#B5CBCB"
LINE_DIM = "#2E4A44"
BG       = "#182D29"   # dark teal (used as the on-band label colour for contrast)

# Slide canvas (inches) — matches the 16:9 deck
SW, SH = 13.333, 7.5

# Five column centres + boundaries (left margin 0.7, usable width split into 5)
LMARGIN = 0.7
COLW = (SW - 2 * LMARGIN) / 5.0
BOUNDS = [LMARGIN + COLW * k for k in range(6)]              # 6 edges
CX = [LMARGIN + COLW * (k + 0.5) for k in range(5)]          # 5 centres

# Vertical anchors, expressed bottom-up in inches (matplotlib y)
ICON_CY = 5.55
CAPS_MY = 4.80
SUB_MY  = 4.32
BASE_MY = 3.84
GUIDE_TOP = 5.98

LANE_H = 0.42
LANES = {                       # (band vertical centre, top-inch helps nobody here)
    "weights": 3.34,
    "skills":  2.74,
    "agents":  2.14,
}

LEVELS = [
    ("WORLD",    "common\nknowledge",   FG),
    ("INDUSTRY", "domain &\nstandards", FG),
    ("CATO",     "products &\npolicy",  ACCENT),
    ("TEAM",     "our service\n& code", FG),
    ("YOU",      "how you\nthink & work", ACCENT),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)
FAM = "DejaVu Sans"


def new_fig():
    fig, ax = plt.subplots(figsize=(SW, SH))
    ax.set_xlim(0, SW)
    ax.set_ylim(0, SH)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, transparent=True)
    plt.close(fig)
    print(f"Saved: {path}")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# ── icon primitives ──────────────────────────────────────────────────────────

def person(ax, cx, cy, s, color, z=3):
    """A simple bust silhouette centred roughly on (cx, cy)."""
    ax.add_patch(Wedge((cx, cy - 0.06 * s), 0.20 * s, 0, 180,
                       facecolor=color, edgecolor="none", zorder=z))
    ax.add_patch(Circle((cx, cy + 0.20 * s), 0.095 * s,
                        facecolor=color, edgecolor="none", zorder=z))


def globe(ax, cx, cy, s=1.0, color=FG):
    r = 0.30 * s
    lw = 2.0
    ax.add_patch(Circle((cx, cy), r, facecolor="none", edgecolor=color,
                        lw=lw, zorder=3))
    ax.add_patch(Ellipse((cx, cy), width=0.34 * s, height=2 * r,
                        facecolor="none", edgecolor=color, lw=1.3, zorder=3))
    ax.plot([cx - r, cx + r], [cy, cy], color=color, lw=1.3, zorder=3)
    dx = r * 0.78
    ax.plot([cx - dx, cx + dx], [cy + 0.15 * s, cy + 0.15 * s],
            color=color, lw=1.0, zorder=3)
    ax.plot([cx - dx, cx + dx], [cy - 0.15 * s, cy - 0.15 * s],
            color=color, lw=1.0, zorder=3)


def skyline(ax, cx, cy, s=1.0, color=FG):
    """Three buildings of differing heights — industry / sector."""
    base = cy - 0.30 * s
    bw = 0.17 * s
    specs = [(-0.30, 0.42), (-0.085, 0.60), (0.13, 0.34)]   # (x offset, height) * s
    for ox, hh in specs:
        ax.add_patch(Rectangle((cx + ox * s, base), bw, hh * s,
                               facecolor=color, edgecolor="none", zorder=3))


def cato_badge(ax, cx, cy, s=1.0, color=ACCENT):
    side = 0.52 * s
    ax.add_patch(FancyBboxPatch((cx - side / 2, cy - side / 2), side, side,
                                boxstyle="round,pad=0.02,rounding_size=0.12",
                                facecolor=color, edgecolor="none", zorder=3))
    ax.add_patch(Circle((cx, cy), 0.10 * s, facecolor=BG, edgecolor="none", zorder=4))


def team(ax, cx, cy):
    person(ax, cx - 0.30, cy - 0.03, 1.15, MUTED, z=2)
    person(ax, cx + 0.30, cy - 0.03, 1.15, MUTED, z=2)
    person(ax, cx, cy, 1.35, FG, z=3)


# ── base graphic ──────────────────────────────────────────────────────────────

def build_base():
    fig, ax = new_fig()

    # faint vertical guides between columns + baseline rule
    for x in BOUNDS[1:-1]:
        ax.plot([x, x], [BASE_MY, GUIDE_TOP], color=LINE_DIM, lw=1.0,
                alpha=0.6, zorder=1)
    ax.plot([BOUNDS[0], BOUNDS[-1]], [BASE_MY, BASE_MY], color=LINE_DIM,
            lw=1.4, zorder=1)

    icon_drawers = [globe, skyline, cato_badge, team, None]
    for i, (caps, sub, ccol) in enumerate(LEVELS):
        cx = CX[i]
        if caps == "YOU":
            person(ax, cx, ICON_CY, 1.9, ACCENT)
        else:
            icon_drawers[i](ax, cx, ICON_CY)
        ax.text(cx, CAPS_MY, caps, color=ccol, fontsize=18, fontweight="bold",
                ha="center", va="center", fontfamily=FAM, zorder=3)
        ax.text(cx, SUB_MY, sub, color=MUTED, fontsize=11.5, ha="center",
                va="center", fontfamily=FAM, zorder=3, linespacing=1.05)

    save(fig, "ideas_base.png")


# ── mechanism bands ─────────────────────────────────────────────────────────--

def band(name, color_hex, label, points, label_x):
    fig, ax = new_fig()
    rgb = hex_rgb(color_hex)
    cy = LANES[name]
    y0, y1 = cy - LANE_H / 2, cy + LANE_H / 2

    N = 700
    xs = np.linspace(0, SW, N)
    px = [p[0] for p in points]
    pa = [p[1] for p in points]
    alpha = np.interp(xs, px, pa)
    rgba = np.zeros((1, N, 4))
    rgba[0, :, 0] = rgb[0]
    rgba[0, :, 1] = rgb[1]
    rgba[0, :, 2] = rgb[2]
    rgba[0, :, 3] = alpha
    ax.imshow(rgba, extent=[0, SW, y0, y1], origin="lower",
              aspect="auto", interpolation="bilinear", zorder=2)

    # label sits where the band is solid; dark text reads cleanly on the bright bar
    ax.text(label_x, cy, label, color=BG, fontsize=15, fontweight="bold",
            ha="left", va="center", fontfamily=FAM, zorder=3)

    save(fig, f"band_{name}.png")


def build_bands():
    # solid over WORLD+INDUSTRY, fading out across CATO
    band("weights", ACCENT, "LLM weights",
         [(0.0, 0.0), (0.55, 0.0), (0.85, 1.0), (5.47, 1.0),
          (7.0, 0.45), (7.86, 0.14), (8.6, 0.0), (SW, 0.0)],
         label_x=0.95)
    # peaks across INDUSTRY -> CATO -> TEAM, light tail into YOU
    band("skills", SKY, "Skills",
         [(0.0, 0.0), (2.6, 0.0), (3.9, 1.0), (9.6, 1.0),
          (10.9, 0.40), (11.9, 0.14), (12.5, 0.0), (SW, 0.0)],
         label_x=4.05)
    # leans right: CATO -> TEAM -> YOU, reaching the far edge
    band("agents", GOLD, "Agents",
         [(0.0, 0.0), (4.7, 0.0), (6.9, 1.0), (12.2, 1.0), (SW, 0.92)],
         label_x=7.05)


if __name__ == "__main__":
    build_base()
    build_bands()
