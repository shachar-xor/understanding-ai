"""
DRAFT ONLY — the Kasparov / centaur-chess story as a standalone mini-deck.

Output: centaur_story_draft.pptx  (separate file; main deck untouched).
Reuses Cato styling from build_presentation.py.

Tone rule applied per request: this is told as a STORY with a lesson, NOT as
absolute truth. Wording is hedged ("by most accounts", "Kasparov's conclusion",
"the advantage later faded"). The honest twist (the centaur edge eroded as
engines became overwhelmingly strong) is included as slide 6 so the conclusion
stays interesting without overclaiming.

Photos (downloaded to assets/, freely licensed — credit lines on slide + notes):
  kasparov.jpg          Grendelkhan,          CC BY-SA 4.0  (Wikimedia Commons)
  deep_blue.jpg         James the photographer, CC BY 2.0   (Wikimedia Commons)
  deep_blue_museum.jpg  Anton Chiang,         CC BY 2.0     (Wikimedia Commons)

Animations OFF so everything is visible on a read-through.

Run:    .venv/bin/python build_centaur_story.py
"""

import os
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from build_presentation import (
    new_prs, content_slide, image_slide, txb, rect, add_notes, add_pic_fit, asset,
    FG, ACCENT, GOLD, SKY, MUTED, CORAL, BOX_FILL, LINE_DIM, HEAD,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def credit(s, text, left, top, width):
    txb(s, text, left, top, width, Inches(0.3), size=9, color=MUTED, align=PP_ALIGN.CENTER)


# ── 1 — 1997: the machine won ─────────────────────────────────────────────────

def s1_1997(prs):
    s = content_slide(prs, "A STORY ABOUT FINDING YOUR VALUE", "1997: the year the machine won")
    if os.path.exists(asset("deep_blue.jpg")):
        add_pic_fit(s, asset("deep_blue.jpg"), Inches(0.6), Inches(2.0), Inches(3.6), Inches(4.4))
        credit(s, "Deep Blue · James the photographer · CC BY 2.0", Inches(0.6), Inches(6.5), Inches(3.6))
    txb(s, "IBM's Deep Blue beat Garry Kasparov — the reigning world champion, and by most "
           "accounts the strongest player alive.",
        Inches(4.6), Inches(2.2), Inches(8.2), Inches(1.6), size=26, bold=True, color=FG)
    txb(s, "Worth saying out loud: Deep Blue wasn't “AI” the way we mean it today. It was a "
           "purpose-built machine doing brute-force search. But the symbolism was total — the "
           "best human had lost his own game.",
        Inches(4.6), Inches(4.1), Inches(8.2), Inches(1.8), size=18, color=MUTED)
    add_notes(s, "S1 | ~1:00. Set the stakes. The honest aside (Deep Blue is not an LLM, it's "
                 "brute-force search) keeps you credible with a sharp room and makes the later "
                 "lesson land harder. The point isn't the tech, it's how Kasparov responded.")


# ── 2 — Kasparov's response ───────────────────────────────────────────────────

def s2_response(prs):
    s = content_slide(prs, "THE TWIST", "He asked a better question")
    if os.path.exists(asset("kasparov.jpg")):
        add_pic_fit(s, asset("kasparov.jpg"), Inches(9.1), Inches(2.0), Inches(3.7), Inches(4.4))
        credit(s, "Garry Kasparov · Grendelkhan · CC BY-SA 4.0", Inches(9.1), Inches(6.5), Inches(3.7))
    txb(s, "Instead of “are humans obsolete?”, he asked:\n“What if human and machine play on the "
           "same side?”",
        Inches(0.55), Inches(2.1), Inches(8.2), Inches(1.5), size=24, bold=True, color=FG)
    txb(s, "In 1998 he launched Advanced Chess — a human playing WITH a computer. His reasoning:",
        Inches(0.55), Inches(3.7), Inches(8.2), Inches(0.7), size=18, color=MUTED)
    for i, b in enumerate([
        "Let the machine handle calculation — no more blunders.",
        "Free the human for strategy, plans, and judgment.",
        "The pair should be stronger than either one alone.",
    ]):
        txb(s, "▸  " + b, Inches(0.7), Inches(4.5) + i * Inches(0.62), Inches(8.1),
            Inches(0.55), size=19, color=FG)
    add_notes(s, "S2 | ~1:15. The reframe is the heart of the story and mirrors the whole talk: "
                 "not human vs machine, but human + machine. Kasparov's bet was that the pairing "
                 "beats either side alone.")


# ── 3 — 2005 freestyle ────────────────────────────────────────────────────────

def s3_2005(prs):
    s = content_slide(prs, "2005 · FREESTYLE", "Two amateurs. Three ordinary PCs.")
    txb(s, "An online “freestyle” tournament let anyone enter — grandmasters, strong chess "
           "computers, mixed teams, anyone.",
        Inches(0.55), Inches(2.1), Inches(12.2), Inches(1.0), size=22, color=FG)
    txb(s, "The winners were two amateurs — Steven Cramton and Zackary Stephen, playing as "
           "“ZackS” — using three average home computers.",
        Inches(0.55), Inches(3.2), Inches(12.2), Inches(1.0), size=22, bold=True, color=ACCENT)
    # rating callout box
    rect(s, Inches(0.55), Inches(4.5), Inches(12.2), Inches(1.0), fill=BOX_FILL, line=LINE_DIM)
    txb(s, "They were not strong players: their ratings were roughly 1685 and 1398. "
           "A titled master is 2200+; a grandmaster 2500+.",
        Inches(0.8), Inches(4.7), Inches(11.7), Inches(0.7), size=18, color=FG)
    txb(s, "(Online play even sparked a rumor that Kasparov himself was secretly behind ZackS. "
           "He wasn't.)",
        Inches(0.55), Inches(5.8), Inches(12.2), Inches(0.6), size=16, italic=True, color=MUTED)
    add_notes(s, "S3 | ~1:15. Land the David-vs-Goliath setup with the real numbers — ~1685 and "
                 "~1398 are genuinely weak ratings, which is what makes the result striking. The "
                 "rumor aside is a nice beat and it's true it was debunked.")


# ── 4 — Why they won ──────────────────────────────────────────────────────────

def s4_why(prs):
    s = content_slide(prs, "2005 · FREESTYLE", "It wasn't strength. It was process.")
    for i, b in enumerate([
        "Ran several chess engines at once and cross-checked where they disagreed.",
        "Knew which engine to trust in which kind of position.",
        "Managed their time and their opening / endgame prep well.",
    ]):
        txb(s, "▸  " + b, Inches(0.7), Inches(2.2) + i * Inches(0.85), Inches(12.0),
            Inches(0.7), size=21, color=FG)
    txb(s, "They out-coordinated fields that included grandmasters and far heavier computing power.",
        Inches(0.55), Inches(5.0), Inches(12.2), Inches(0.8), size=22, bold=True, color=SKY,
        align=PP_ALIGN.CENTER)
    txb(s, "Careful wording: they beat strong fields — not a clean 1-v-1 over “the single best "
           "human” and “the single best computer”. The win was real; the slogan is a simplification.",
        Inches(0.55), Inches(6.0), Inches(12.2), Inches(0.9), size=15, italic=True, color=MUTED,
        align=PP_ALIGN.CENTER)
    add_notes(s, "S4 | ~1:15. The mechanism is the takeaway: process beat raw strength. Keep the "
                 "honesty line so you can't be caught overclaiming — they beat strong fields, "
                 "which is impressive enough.")


# ── 5 — Kasparov's conclusion ─────────────────────────────────────────────────

def s5_conclusion(prs):
    s = image_slide(prs)
    txb(s, "What Kasparov took from it", Inches(0.55), Inches(0.7), Inches(12.2), Inches(0.8),
        size=30, bold=True, color=FG, align=PP_ALIGN.CENTER, font=HEAD)
    rect(s, Inches(1.4), Inches(2.2), Inches(10.5), Inches(2.4), fill=BOX_FILL, line=ACCENT, line_w=Pt(1.5))
    txb(s, "“A weak human + machine + a better process was superior to a strong computer alone — "
           "and even to a strong human + machine + an inferior process.”",
        Inches(1.8), Inches(2.5), Inches(9.7), Inches(1.6), size=22, italic=True, color=FG)
    txb(s, "— Garry Kasparov (paraphrased)", Inches(1.8), Inches(4.05), Inches(9.7), Inches(0.4),
        size=15, color=MUTED)
    txb(s, "His conclusion, not a law of nature: the decisive factor wasn't raw human skill or "
           "raw machine power. It was the quality of the partnership.",
        Inches(1.0), Inches(5.0), Inches(11.3), Inches(1.2), size=20, bold=True, color=ACCENT,
        align=PP_ALIGN.CENTER)
    add_notes(s, "S5 | ~1:00. Read the quote slowly. Stress that this is HIS reading of a handful "
                 "of events, framed as interesting, not proven. The process > power idea is the "
                 "bridge to 'find your value'.")


# ── 6 — The honest twist + lesson ─────────────────────────────────────────────

def s6_twist(prs):
    s = content_slide(prs, "BE CRITICAL", "And then the story kept going")
    txb(s, "The centaur edge was real — but it was a moving target.",
        Inches(0.55), Inches(2.0), Inches(12.2), Inches(0.7), size=24, bold=True, color=CORAL)
    txb(s, "As engines became overwhelmingly strong (the AlphaZero era), a human could rarely "
           "improve on the machine's move — and mostly risked adding error. Top-level centaur "
           "chess faded.",
        Inches(0.55), Inches(2.75), Inches(12.2), Inches(1.2), size=18, color=MUTED)
    txb(s, "So what's the honest lesson?", Inches(0.55), Inches(4.1), Inches(12.2), Inches(0.5),
        size=18, bold=True, color=ACCENT)
    for i, b in enumerate([
        "Your edge is process and judgment, not out-muscling the machine.",
        "When the machine gets stronger, you move up to where it isn't — yet.",
        "Chess is a closed game with a perfect scorekeeper: the worst case for humans. "
        "Real work is open-ended, so the room for you lasts far longer.",
    ]):
        txb(s, "▸  " + b, Inches(0.7), Inches(4.65) + i * Inches(0.62), Inches(12.0),
            Inches(0.6), size=18, color=FG)
    txb(s, "Be the centaur. And keep moving.", Inches(0.55), Inches(6.7), Inches(12.2), Inches(0.5),
        size=20, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_notes(s, "S6 | ~1:15. This is what keeps you honest AND makes the conclusion deeper: the "
                 "advantage decayed, and that decay is the lesson — value isn't a fixed seat, it's "
                 "a direction. Note chess is the hardest case for humans (closed, perfectly "
                 "scored); your work is not, which is the optimistic note to end on.")


def build():
    prs = new_prs()
    s1_1997(prs)
    s2_response(prs)
    s3_2005(prs)
    s4_why(prs)
    s5_conclusion(prs)
    s6_twist(prs)
    out = os.path.join(HERE, "centaur_story_draft.pptx")
    prs.save(out)
    print(f"Saved: {out}  ({len(prs.slides)} slides)")
    return out


if __name__ == "__main__":
    build()
