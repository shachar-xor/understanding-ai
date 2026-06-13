"""
DRAFT — "Context windows exploded" visualization.

A standalone, throwaway deck with a single slide: a log-scale timeline of LLM
context-window sizes growing over time (2K → 2M tokens in ~5 years).

Reuses the Cato design tokens + drawing helpers from build_presentation.py
WITHOUT touching the main deck. Importing that module only runs its top-level
definitions (build() is guarded by __main__), so nothing is rebuilt.

Run:    .venv/bin/python draft_context_growth.py
Output: draft_context_growth.pptx   (open in PowerPoint/Keynote — has click anim)
"""

import os
import math

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from build_presentation import (
    new_prs, content_slide, txb, rect, animate_clicks, add_notes,
    HERE, FG, ACCENT, GOLD, SKY, MUTED, LINE_DIM, _DIM,
)


def s_context_growth(prs):
    """Log-scale bar timeline: context windows grew ~1000× in ~5 years."""
    s = content_slide(prs, "LAYER 3 · CONTEXT MANAGEMENT", "Context windows exploded")

    # ── plot geometry (inches) ────────────────────────────────────────────────
    baseline_y = 6.05          # y of the 1K gridline / bar baseline
    max_h      = 3.25          # bar height at the top of the scale (2M)
    e_lo, e_hi = 3.0, 6.301    # log10 range: 1K … 2M
    plot_l, plot_r = 1.30, 12.95

    def y_for(exp):
        """Inches-y for a given log10 value on the scale."""
        frac = (exp - e_lo) / (e_hi - e_lo)
        return baseline_y - frac * max_h

    # ── log-scale gridlines (1K / 10K / 100K / 1M) ────────────────────────────
    for exp, lbl in [(3, "1K"), (4, "10K"), (5, "100K"), (6, "1M")]:
        gy = y_for(exp)
        rect(s, Inches(plot_l), Inches(gy), Inches(plot_r - plot_l), Pt(0.75),
             fill=LINE_DIM)
        txb(s, lbl, Inches(0.35), Inches(gy - 0.14), Inches(0.85), Inches(0.32),
            size=11, color=MUTED, align=PP_ALIGN.RIGHT)

    txb(s, "tokens  ·  log scale", Inches(0.30), Inches(1.85), Inches(2.4), Inches(0.4),
        size=11, color=MUTED, italic=True)

    # ── milestones (chronological) ────────────────────────────────────────────
    # (model, year, display, tokens, colour)
    data = [
        ("GPT-3",           "2020", "2K",   2048,    _DIM),
        ("GPT-3.5",         "2022", "4K",   4096,    _DIM),
        ("GPT-4",           "2023", "8K",   8192,    SKY),
        ("Claude",          "2023", "100K", 100000,  ACCENT),
        ("Claude 2.1",      "2023", "200K", 200000,  ACCENT),
        ("Gemini 1.5",      "2024", "2M",   2000000, GOLD),
        ("Claude Sonnet 4", "2025", "1M",   1000000, GOLD),
        ("Claude Opus 4.8", "2026", "1M",   1000000, GOLD),
    ]

    n = len(data)
    step  = (plot_r - plot_l) / n
    bar_w = 0.80

    groups = []
    for i, (name, year, disp, tokens, col) in enumerate(data):
        cx   = plot_l + step * (i + 0.5)
        left = cx - bar_w / 2
        top  = y_for(math.log10(tokens))
        h    = baseline_y - top

        shapes = []
        # bar
        shapes.append(rect(s, Inches(left), Inches(top), Inches(bar_w), Inches(h),
                           fill=col))
        # token size above the bar
        shapes.append(txb(s, disp, Inches(left - 0.25), Inches(top - 0.42),
                          Inches(bar_w + 0.5), Inches(0.4),
                          size=15, bold=True, color=col, align=PP_ALIGN.CENTER))
        # model name + year below the baseline
        shapes.append(txb(s, name, Inches(cx - 0.95), Inches(baseline_y + 0.08),
                          Inches(1.9), Inches(0.42),
                          size=12, bold=True, color=FG, align=PP_ALIGN.CENTER))
        shapes.append(txb(s, year, Inches(cx - 0.95), Inches(baseline_y + 0.48),
                          Inches(1.9), Inches(0.34),
                          size=12, color=MUTED, align=PP_ALIGN.CENTER))
        groups.append(shapes)

    # ── headline callout (lands with the explosion) ──────────────────────────
    callout = []
    callout.append(txb(s, "≈ 1000×", Inches(1.45), Inches(2.45), Inches(3.6), Inches(0.8),
                       size=44, bold=True, color=GOLD, align=PP_ALIGN.LEFT))
    callout.append(txb(s, "2K → millions of tokens in ~4 years.\nThen 1M became the standard.",
                       Inches(1.5), Inches(3.35), Inches(4.6), Inches(1.0),
                       size=18, color=FG, align=PP_ALIGN.LEFT))

    # Reveal the story in three clicks: early → mid → explosion + callout.
    animate_clicks(s, [
        groups[0] + groups[1] + groups[2],
        groups[3] + groups[4] + groups[5],
        groups[6] + groups[7] + callout,
    ])

    add_notes(s,
        "DRAFT visualization — context-window growth.\n\n"
        "The window we've been talking about hasn't stood still. Walk it left to right:\n"
        "early models gave us a couple thousand tokens — a few pages. Then 100K, 200K,\n"
        "and by 2024 a million-plus (Gemini hit 2M). That's roughly a 1000× jump in ~4\n"
        "years (log scale — each gridline is 10×, so the real jump dwarfs the bar heights).\n\n"
        "The interesting part is what happened next: the race plateaued. Instead of\n"
        "chasing ever-bigger numbers, ~1M became the standard ceiling across vendors —\n"
        "Claude Sonnet 4 (2025) and Opus 4.8 (2026) both ship 1M.\n\n"
        "Punchline still holds: bigger windows fill up just as fast, and large context\n"
        "costs significantly more — so managing context matters more, not less.")


def build():
    prs = new_prs()
    s_context_growth(prs)
    out = os.path.join(HERE, "draft_context_growth.pptx")
    prs.save(out)
    print(f"Saved: {out}  ({len(prs.slides)} slide)")
    return out


if __name__ == "__main__":
    build()
