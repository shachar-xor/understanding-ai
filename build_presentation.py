"""
Build "Understanding AI for Geeks" — re-skinned onto the official Cato template.

Loads `Cato Presentation Template.pptx`, deletes its sample slides, and rebuilds
the talk on Cato's dark (black) layout family so the deck inherits Cato branding
(logo, footer, slide numbers, Aptos fonts, dark-teal theme).

Hybrid approach:
  - Native Cato layouts give background + branding + the title placeholder.
  - Body content is positioned with custom text boxes / shapes (full control,
    matching the original deck), drawn with the Cato colour palette.

Run:    .venv/bin/python build_presentation.py
Output: understanding_ai_for_geeks.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn, nsdecls
from pptx.oxml import parse_xml

HERE     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "Cato Presentation Template.pptx")
ASSETS   = os.path.join(HERE, "assets")

# ── Cato design tokens ───────────────────────────────────────────────────────
BG       = RGBColor(0x18, 0x2D, 0x29)   # dark teal (inherited from layout bg)
FG       = RGBColor(0xF6, 0xF6, 0xF7)   # off-white text
ACCENT   = RGBColor(0x38, 0xD9, 0xA7)   # mint — primary accent
GOLD     = RGBColor(0xFE, 0xC7, 0x56)
PURPLE   = RGBColor(0x99, 0x55, 0xBA)
CORAL    = RGBColor(0xFF, 0x6F, 0x5B)
SKY      = RGBColor(0x55, 0xCB, 0xF2)
MUTED    = RGBColor(0xB5, 0xCB, 0xCB)   # grey-blue — sub-text
CODE_BG  = RGBColor(0x0E, 0x1A, 0x17)   # very dark teal — code/context blocks
CODE_FG  = RGBColor(0xA8, 0xE6, 0xCF)   # mint-tint code text
LINE_DIM = RGBColor(0x2E, 0x4A, 0x44)   # subtle dividers / outlines
BOX_FILL = RGBColor(0x22, 0x40, 0x3A)   # raised box interior on teal

FONT = "Aptos"
HEAD = "Aptos Display"
MONO = "Consolas"

W = Inches(13.33)
H = Inches(7.5)

# Agent walk-through colour aliases
_DIM  = RGBColor(0x5E, 0x7A, 0x73)   # already-seen context (dim teal)
_NEW  = RGBColor(0x6C, 0xFF, 0xB0)   # tool result / new data (bright green)
_AI   = GOLD                          # previous LLM response (amber/gold)
_HEAD = SKY                           # section markers inside context block


# ═══════════════════════════════════════════════════════════════════════════
#  TEMPLATE / LAYOUT PLUMBING
# ═══════════════════════════════════════════════════════════════════════════

def new_prs():
    """Load the Cato template and strip every sample slide (keep masters/layouts)."""
    prs = Presentation(TEMPLATE)
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        rId = sldId.get(qn("r:id"))
        prs.part.drop_rel(rId)
        sldIdLst.remove(sldId)
    return prs


def layout(prs, name):
    """Return the slide layout with the given name (raises if renamed/missing)."""
    for master in prs.slide_masters:
        for lay in master.slide_layouts:
            if lay.name == name:
                return lay
    raise KeyError(f"Layout {name!r} not found in template")


def add(prs, layout_name):
    return prs.slides.add_slide(layout(prs, layout_name))


def ph(slide, idx):
    """Get a placeholder by its idx, or None."""
    for p in slide.placeholders:
        if p.placeholder_format.idx == idx:
            return p
    return None


def del_ph(slide, idx):
    """Remove an unused placeholder so it does not show prompt text."""
    p = ph(slide, idx)
    if p is not None:
        p._element.getparent().remove(p._element)


def set_ph(slide, idx, text, size=None, color=None, bold=None, font=None):
    """Write text into a placeholder, keeping its native (Cato) styling by default."""
    p = ph(slide, idx)
    tf = p.text_frame
    tf.text = text
    for para in tf.paragraphs:
        for run in para.runs:
            if size is not None:  run.font.size = Pt(size)
            if color is not None: run.font.color.rgb = color
            if bold is not None:  run.font.bold = bold
            if font is not None:  run.font.name = font
    return p


def hide(slide):
    """Mark a slide as hidden (skipped in slideshow)."""
    slide._element.set("show", "0")


# ═══════════════════════════════════════════════════════════════════════════
#  DRAWING HELPERS  (custom-positioned body content)
# ═══════════════════════════════════════════════════════════════════════════

def txb(slide, text, left, top, width, height,
        size=28, bold=False, color=None, align=PP_ALIGN.LEFT,
        font=None, italic=False):
    """Add a single-paragraph text box."""
    tf_box = slide.shapes.add_textbox(left, top, width, height)
    tf = tf_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color or FG
    run.font.name = font or FONT
    return tf_box


def rect(slide, left, top, width, height, fill=None, line=None, line_w=Pt(1)):
    """Add a rectangle shape."""
    shp = slide.shapes.add_shape(1, left, top, width, height)
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = line_w
    return shp


def code_block(slide, text, left, top, width, height, size=15):
    """Monospaced code block with dark background."""
    rect(slide, left, top, width, height, fill=CODE_BG)
    tf_box = slide.shapes.add_textbox(
        left + Inches(0.2), top + Inches(0.12),
        width - Inches(0.4), height - Inches(0.24))
    tf = tf_box.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.name = MONO
    run.font.color.rgb = CODE_FG
    return tf_box


def add_pic_fit(slide, path, left, top, max_w, max_h):
    """Add image preserving aspect ratio within max_w x max_h, centered."""
    from PIL import Image as PILImage
    im = PILImage.open(path)
    iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w = iw * ratio
    h = ih * ratio
    offset_x = (max_w - w) / 2
    offset_y = (max_h - h) / 2
    return slide.shapes.add_picture(path, left + offset_x, top + offset_y, w, h)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def animate_clicks(slide, click_groups):
    """
    Add 'Appear' entrance animations triggered on click.

    click_groups : list of click steps; each step is a list of shape objects
                   revealed together on that click, in order.

    Animated shapes stay hidden until their click, then appear. NOTE: python-pptx
    cannot render animations and QuickLook ignores them — verify playback in
    PowerPoint/Keynote.
    """
    cid = [2]   # id 1 = tmRoot, id 2 = mainSeq (reserved)

    def nid():
        cid[0] += 1
        return cid[0]

    def set_node(spid):
        return (
            '<p:set>'
            '<p:cBhvr>'
            f'<p:cTn id="{nid()}" dur="1" fill="hold">'
            '<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            '</p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            '</p:cBhvr>'
            '<p:to><p:strVal val="visible"/></p:to>'
            '</p:set>'
        )

    def effect_par(spid, node_type):
        return (
            '<p:par>'
            f'<p:cTn id="{nid()}" presetID="1" presetClass="entr" presetSubtype="0" '
            f'fill="hold" grpId="0" nodeType="{node_type}">'
            '<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst>{set_node(spid)}</p:childTnLst>'
            '</p:cTn>'
            '</p:par>'
        )

    click_pars = []
    for group in click_groups:
        outer, inner = nid(), nid()
        effects = "".join(
            effect_par(shp.shape_id, "clickEffect" if i == 0 else "withEffect")
            for i, shp in enumerate(group)
        )
        click_pars.append(
            '<p:par>'
            f'<p:cTn id="{outer}" fill="hold">'
            '<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
            '<p:childTnLst><p:par>'
            f'<p:cTn id="{inner}" fill="hold">'
            '<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst>{effects}</p:childTnLst>'
            '</p:cTn></p:par></p:childTnLst>'
            '</p:cTn>'
            '</p:par>'
        )

    timing = (
        f'<p:timing {nsdecls("p")}>'
        '<p:tnLst><p:par>'
        '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        '<p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(click_pars)}</p:childTnLst>'
        '</p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        '</p:seq></p:childTnLst>'
        '</p:cTn>'
        '</p:par></p:tnLst>'
        '</p:timing>'
    )
    slide._element.append(parse_xml(timing))


def asset(name):
    return os.path.join(ASSETS, name)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE SCAFFOLDS  (native Cato layouts + eyebrow/title)
# ═══════════════════════════════════════════════════════════════════════════

def head(slide, eyebrow, title):
    """Populate the native title placeholder: small mint eyebrow + bold title."""
    t = ph(slide, 0)
    tf = t.text_frame
    tf.clear()
    p0 = tf.paragraphs[0]
    if eyebrow:
        r0 = p0.add_run()
        r0.text = eyebrow
        r0.font.size = Pt(13)
        r0.font.bold = True
        r0.font.color.rgb = ACCENT
        r0.font.name = FONT
        p1 = tf.add_paragraph()
    else:
        p1 = p0
    r1 = p1.add_run()
    r1.text = title
    r1.font.size = Pt(30)
    r1.font.bold = True
    r1.font.color.rgb = FG
    r1.font.name = HEAD


def content_slide(prs, eyebrow, title):
    """Standard content slide: native 'Text Slide black' + custom body region."""
    s = add(prs, "Text Slide black")
    del_ph(s, 1)            # drop body placeholder; body is custom-positioned
    head(s, eyebrow, title)
    return s


def image_slide(prs):
    """Dark slide with no title — for full-image/mystery slides."""
    s = add(prs, "Text Slide black")
    del_ph(s, 0)
    del_ph(s, 1)
    return s


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDES
# ═══════════════════════════════════════════════════════════════════════════

def s01_title(prs):
    """1 — Title slide (Cover Slide Black)"""
    s = add(prs, "Cover Slide Black")
    set_ph(s, 0, "Understanding AI for Geeks", color=FG)
    del_ph(s, 12)   # no subtitle
    add_notes(s,
        "⏱ 0:30 | Running: 0:30\n\n"
        "Let the slide sit for a moment. No need to say much.\n"
        "You can say: 'Let's talk about AI — but not in the way you've heard before.'")


def s02_intro_me(prs):
    """2 — Hi, I'm Shachar (the hook / self-intro)"""
    s = content_slide(prs, "ABOUT ME", "Hi, I'm Shachar")

    # Four bullets — minimal text, revealed one per click. Mint marker + white text.
    bullet_shapes = []
    y = Inches(1.95)
    for text in ["A software developer", "5+ years at Cato",
                 "A Lego & The Office fan", "A geek"]:
        tb = s.shapes.add_textbox(Inches(0.55), y, Inches(6.0), Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        m = p.add_run(); m.text = "▸   "
        m.font.size = Pt(26); m.font.bold = True; m.font.color.rgb = ACCENT; m.font.name = FONT
        r = p.add_run(); r.text = text
        r.font.size = Pt(26); r.font.bold = True; r.font.color.rgb = FG; r.font.name = FONT
        bullet_shapes.append(tb)
        y += Inches(0.95)

    # Hero photo on the right (AI-enhanced version) — enlarged
    add_pic_fit(s, asset("Cato_leggo_ai_enhanced.png"),
                Inches(6.65), Inches(1.55), Inches(6.55), Inches(5.4))

    # Pop-up punchline: Michael Scott also holding a Dundie (mint-framed inset)
    mx, my, mw, mh = Inches(9.0), Inches(5.5), Inches(4.05), Inches(2.28)
    frame = rect(s, mx - Pt(3), my - Pt(3), mw + Pt(6), mh + Pt(6), fill=ACCENT)
    mscott = s.shapes.add_picture(asset("michael_scott.png"), mx, my, mw, mh)

    # Reveal bullets one per click; the Michael Scott pop-up appears together
    # with the "A Lego & The Office fan" bullet (index 2).
    animate_clicks(s, [
        [bullet_shapes[0]],
        [bullet_shapes[1]],
        [bullet_shapes[2], frame, mscott],
        [bullet_shapes[3]],
    ])

    add_notes(s,
        "⏱ 0:45 | Running: 1:15\n\n"
        "Open warm and light — this is the hook. Click through the four points as you\n"
        "talk; let the photo carry the rest.\n"
        "'Hi, my name is Shachar, and as you can see from my picture here, I'm:\n"
        " a software developer; over 5 years at Cato — there's the 5-years-a-Catonian\n"
        " Lego tower; a Lego and The Office fan — yes, that's my Dundie...'\n"
        " (same click: Michael Scott pops up) '...just like Michael's.'  'And a geek —\n"
        " which is what this talk is about.'\n\n"
        "Click-to-reveal is authored as PowerPoint 'Appear' animations — confirm it\n"
        "plays in PowerPoint/Keynote (it won't show in QuickLook previews).")


def s03_geek_origin(prs):
    """3 — As a geek, I learn by taking things apart (build up / break down / fix)"""
    s = image_slide(prs)

    # Centered title — "love" in mint to echo the heart on the client.
    t = s.shapes.add_textbox(Inches(0.55), Inches(0.5), Inches(12.2), Inches(0.95))
    tf = t.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for txt, col in [("I ", FG), ("love", ACCENT), (" to understand things", FG)]:
        r = p.add_run(); r.text = txt
        r.font.size = Pt(32); r.font.bold = True; r.font.color.rgb = col; r.font.name = HEAD

    # (name, left, top, box_w, box_h) — CatoClient is a bit larger (the focal joke).
    specs = [
        ("lego_pieces.jpg",       Inches(0.45), Inches(1.7), Inches(4.0), Inches(3.6)),
        ("m16_parts_cropped.png", Inches(4.66), Inches(1.7), Inches(4.0), Inches(3.6)),
        ("cato-client.png",       Inches(8.70), Inches(1.5), Inches(4.3), Inches(4.2)),
    ]
    pics = []
    for name, left, top, bw, bh in specs:
        p = asset(name)
        if os.path.exists(p):
            pics.append(add_pic_fit(s, p, left, top, bw, bh))
        else:
            box = rect(s, left, top, bw, bh, fill=BOX_FILL, line=LINE_DIM)
            txb(s, f"[ add {name} ]", left, top + bh / 2, bw, Inches(0.5),
                size=12, color=MUTED, align=PP_ALIGN.CENTER)
            pics.append(box)

    # Little green heart on the CatoClient (the "...but I love it" wink),
    # near its top-right corner as a badge.
    heart = s.shapes.add_textbox(Inches(11.75), Inches(1.55), Inches(0.9), Inches(0.8))
    hp = heart.text_frame.paragraphs[0]
    hp.alignment = PP_ALIGN.CENTER
    hr = hp.add_run(); hr.text = "💚"; hr.font.size = Pt(34)

    final = txb(s,
        "So let's do the same with AI.",
        Inches(0.55), Inches(5.85), Inches(12.2), Inches(0.8),
        size=30, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # Reveal images one per click; the heart pops with the CatoClient; then the line.
    animate_clicks(s, [[pics[0]], [pics[1]], [pics[2], heart], [final]])

    add_notes(s,
        "⏱ ~1:00 | Running: ~2:15\n\n"
        "Continue from 'a geek'. Click through the three images as you talk:\n"
        "'As a geek, I've always understood things by building them up' (click: Lego),\n"
        "'breaking them down' (click: M16 disassembled),\n"
        "'and fixing what's broken' (click: CatoClient... yes, ours too; wink + green heart).\n"
        "'I've basically been doing this my whole life.'\n"
        "'So now let's do the same with AI:' (click: closing line) 'take it apart,\n"
        " and learn to think with it and use it better.'\n\n"
        "Click-to-reveal uses PowerPoint 'Appear' animations; confirm playback in\n"
        "PowerPoint/Keynote (it won't show in QuickLook previews).")


def s04a_done_before_grid(prs):
    """4A — We've done this before (concept-card grid variant; HIDDEN backup)"""
    s = content_slide(prs, "THE INSIGHT", "We've done this before")
    hide(s)   # kept as a backup; timeline variant is the live slide

    cards = [
        ("Object-Oriented",       "encapsulation · inheritance · polymorphism"),
        ("Design Patterns",       "Singleton · Factory · Observer · Strategy"),
        ("SOLID",                 "SRP · OCP · LSP · ISP · DIP"),
        ("Functional",            "pure functions · immutability · composition"),
        ("Cloud / Microservices", "containers · orchestration · IaC"),
        ("Agile / DevOps",        "CI/CD · sprints · retros"),
    ]
    lefts = [Inches(0.45), Inches(4.66), Inches(8.87)]
    tops  = [Inches(1.9), Inches(3.6)]
    col_w, card_h = Inches(4.0), Inches(1.5)

    for i, (name, terms) in enumerate(cards):
        left, top = lefts[i % 3], tops[i // 3]
        rect(s, left, top, col_w, card_h, fill=BOX_FILL, line=LINE_DIM)
        txb(s, name, left + Inches(0.22), top + Inches(0.14),
            col_w - Inches(0.44), Inches(0.5), size=18, bold=True, color=ACCENT)
        txb(s, terms, left + Inches(0.22), top + Inches(0.66),
            col_w - Inches(0.44), Inches(0.75), size=13, color=MUTED)

    payoff = txb(s, "We built the language for software. Now let's build one for AI.",
                 Inches(0.55), Inches(5.55), Inches(12.2), Inches(0.7),
                 size=22, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    animate_clicks(s, [[payoff]])

    add_notes(s,
        "⏱ ~1:30 | Running: ~3:45\n\n"
        "AI is a new technology. But handling new technology is our home turf.\n"
        "Every time a new paradigm arrived, WE coined the words that made it thinkable:\n"
        "object-orientation, design patterns, SOLID, cloud, agile. Thinking of a Singleton\n"
        "or a Factory isn't hard for an experienced developer; SOLID is second nature. Once\n"
        "we coined these terms, juniors and seniors alike could think and communicate them.\n"
        "None of it came from a single vendor; the community built it.\n"
        "(click) 'We built the language for software. Now let's build one for AI.'\n\n"
        "Show more than you name: let the grid speak; you only need to mention a few.")


def s04b_done_before_timeline(prs):
    """4B — We've done this before, as a community (timeline; live slide)"""
    s = content_slide(prs, "", "We've done this before, as a community")

    # Chronologically sorted (community-coined vocabulary, with rough years).
    milestones = [
        ("OOP",             "1970s", "encapsulation · inheritance"),
        ("Design Patterns", "1994",  "Singleton · Factory"),
        ("Agile",           "2001",  "sprints · retros"),
        ("SOLID",           "2004",  "SRP · OCP · DIP"),
        ("Cloud",           "2006",  "containers · microservices"),
        ("AI ?",            "now",   "we write this"),
    ]
    box_w, box_h = Inches(1.82), Inches(1.25)
    step    = Inches(2.12)
    x0      = Inches(0.5)
    box_top = Inches(2.55)

    groups = []
    for i, (name, year, terms) in enumerate(milestones):
        left = x0 + step * i
        last = (i == len(milestones) - 1)
        shapes = []
        if i > 0:  # arrow leading into this milestone, revealed with it
            shapes.append(txb(s, "→",
                left - (step - box_w) - Inches(0.13), box_top + Inches(0.32),
                Inches(0.62), Inches(0.6), size=24, color=MUTED, align=PP_ALIGN.CENTER))
        shapes.append(txb(s, year, left, box_top - Inches(0.5), box_w, Inches(0.4),
            size=14, bold=True, color=ACCENT if last else MUTED, align=PP_ALIGN.CENTER))
        shapes.append(rect(s, left, box_top, box_w, box_h,
            fill=BOX_FILL, line=ACCENT if last else LINE_DIM,
            line_w=Pt(1.75) if last else Pt(0.75)))
        shapes.append(txb(s, name, left, box_top + Inches(0.4), box_w, Inches(0.55),
            size=18, bold=True, color=ACCENT if last else FG, align=PP_ALIGN.CENTER))
        shapes.append(txb(s, terms, left - Inches(0.12), box_top + box_h + Inches(0.1),
            box_w + Inches(0.24), Inches(0.7), size=12, color=MUTED, align=PP_ALIGN.CENTER))
        groups.append(shapes)

    payoff = txb(s, "Every shift, the community coined the words. AI is next.",
                 Inches(0.55), Inches(5.6), Inches(12.2), Inches(0.7),
                 size=22, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    groups[-1].append(payoff)   # payoff lands with the AI milestone

    # Each milestone appears on its own click; the payoff lands with AI.
    animate_clicks(s, groups)

    add_notes(s,
        "⏱ ~1:30 | Running: ~3:45\n\n"
        "AI is new, but handling new technology is home turf for us, as a community.\n"
        "Walk the timeline as you click:\n"
        "OOP (1970s), Design Patterns (1994), Agile (2001), SOLID (2004), Cloud (2006)...\n"
        "each time, WE coined the vocabulary that made the idea thinkable and shareable.\n"
        "A Singleton or a Factory isn't hard for an experienced developer; SOLID is second\n"
        "nature. None of it came from a single vendor; the community built the language.\n"
        "(final click) AI is the next stop, and the words are ours to write:\n"
        "'Every shift, the community coined the words. AI is next.'\n\n"
        "Milestones appear one per click; the payoff lands with the AI box. (PowerPoint\n"
        "'Appear' animations; confirm playback in PowerPoint, not QuickLook.)")


def s05_ai_different(prs):
    """5 — But AI is different: fast and closed"""
    s = content_slide(prs, "BUT AI IS DIFFERENT", "Fast, and closed")

    img_top, img_h, col_w = Inches(1.9), Inches(3.5), Inches(5.8)
    if os.path.exists(asset("fast.png")):
        add_pic_fit(s, asset("fast.png"), Inches(0.3), img_top, col_w, img_h)
    if os.path.exists(asset("closed.png")):
        add_pic_fit(s, asset("closed.png"), Inches(7.0), img_top, col_w, img_h)

    rect(s, Inches(6.55), img_top, Pt(1), Inches(4.0), fill=LINE_DIM)

    txb(s, "Fast", Inches(0.3), Inches(5.5), Inches(5.8), Inches(0.6),
        size=28, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    txb(s, "Closed", Inches(7.0), Inches(5.5), Inches(5.8), Inches(0.6),
        size=28, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    payoff = txb(s, "So the language won't come from the vendors. It has to come from us.",
                 Inches(0.55), Inches(6.25), Inches(12.2), Inches(0.6),
                 size=18, bold=True, color=FG, align=PP_ALIGN.CENTER)
    animate_clicks(s, [[payoff]])

    add_notes(s,
        "⏱ ~1:30 | Running: ~5:15\n\n"
        "There's a catch, two of them.\n"
        "FAST: AI moves faster than we can build shared understanding. New models and terms\n"
        "every few weeks.\n"
        "CLOSED: it's vendor-driven and built for lock-in. OpenAI, Anthropic, Google, Meta\n"
        "all compete; none is incentivized to give us a shared vocabulary.\n"
        "(click) 'So the language won't come from the vendors. It has to come from us.'\n"
        "That is exactly what the rest of this talk does, with three words.")


def s04_why_hard(prs):
    """4 — Why AI feels hard (superseded by s05_ai_different; kept for reference)"""
    s = content_slide(prs, "THE PROBLEM", "Why AI feels hard")

    img_top = Inches(1.95)
    img_h   = Inches(3.7)
    col_w   = Inches(5.8)

    def add_half_pic(path, left):
        if os.path.exists(path):
            add_pic_fit(s, path, left, img_top, col_w, img_h)

    add_half_pic(asset("fast.png"),   Inches(0.3))
    add_half_pic(asset("closed.png"), Inches(7.0))

    rect(s, Inches(6.55), img_top, Pt(1), Inches(4.7), fill=LINE_DIM)

    txb(s, "Fast", Inches(0.3), Inches(5.85), Inches(5.8), Inches(0.6),
        size=28, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    txb(s, "Moves faster than we can build shared understanding",
        Inches(0.3), Inches(6.45), Inches(5.8), Inches(0.6),
        size=15, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s, "Closed", Inches(7.0), Inches(5.85), Inches(5.8), Inches(0.6),
        size=28, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    txb(s, "Vendor-driven. Each wants lock-in.\nNo incentive to build a common language.",
        Inches(7.0), Inches(6.45), Inches(5.8), Inches(0.6),
        size=15, color=MUTED, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 2:00 | Running: 3:00\n\n"
        "FAST: AI moves faster than our ability to build shared understanding around it.\n"
        "New models drop every few weeks. The terminology shifts constantly.\n\n"
        "CLOSED: OpenAI, Anthropic, Google, Meta — they all compete.\n"
        "Each one wants you locked into their platform, their API, their way of thinking.\n"
        "Nobody is incentivized to create a shared vocabulary.\n"
        "That's why it feels like you're learning from scratch every time.\n\n"
        "These two things together are why AI feels hard — not because it's magic.")


def s05_common_language(prs):
    """5 — We've solved this before"""
    s = content_slide(prs, "THE INSIGHT", "We've solved this before")

    concepts = [
        ("Functional Programming", "Pure functions, immutability, composition"),
        ("Object-Oriented",        "Encapsulation, inheritance, polymorphism"),
        ("Design Patterns",        "Singleton, Factory, Observer, Strategy, Decorator..."),
        ("SOLID Principles",       "Single responsibility, Open/closed, Liskov, "
                                   "Interface segregation, Dependency inversion"),
    ]
    y = Inches(2.0)
    for title, sub in concepts:
        txb(s, title, Inches(0.55), y, Inches(4.5), Inches(0.5),
            size=22, bold=True, color=FG)
        txb(s, sub, Inches(0.55), y + Inches(0.48), Inches(4.5), Inches(0.55),
            size=14, color=MUTED)
        y += Inches(1.2)

    txb(s, '"We built Functional Programming, OOP,\nDesign Patterns, SOLID\n'
           '— none of it was invented by\nMicrosoft or Oracle.\n\n'
           'The community did it.  We can do it again."',
        Inches(5.8), Inches(2.0), Inches(7.0), Inches(3.2),
        size=18, color=FG, italic=True)
    txb(s, "Trivially important  ·  Vendor-independent  ·  Transferable  ·  Community-owned",
        Inches(5.8), Inches(5.4), Inches(7.0), Inches(0.5),
        size=13, color=ACCENT)
    add_notes(s,
        "⏱ 2:30 | Running: 5:30\n\n"
        "We've been here before as a profession.\n"
        "OOP didn't come from Microsoft. Design Patterns didn't come from Oracle.\n"
        "The community built these — a shared language that works regardless of\n"
        "which vendor, language, or framework you use.\n\n"
        "That's what we're doing today: LLM, Agent, Context — our attempt at that\n"
        "vocabulary for AI. Simple, transferable, community-owned.")


def s06_pin_reveal(prs):
    """6 — Pin reveal: pin -> disassembled -> assembled"""
    s = content_slide(prs, "THE METAPHOR", "Know your weapon")

    col1, col2, col3 = Inches(0.3), Inches(4.55), Inches(8.8)
    col_w   = Inches(3.9)
    img_top = Inches(1.95)
    img_h   = Inches(4.1)
    label_t = Inches(6.25)

    add_pic_fit(s, asset("pin_transparent.png"), col1, img_top, col_w, img_h)
    txb(s, "The pin", col1, label_t, col_w, Inches(0.5),
        size=16, color=MUTED, align=PP_ALIGN.CENTER)

    txb(s, "→", Inches(4.1), Inches(3.7), Inches(0.5), Inches(0.6),
        size=28, color=ACCENT, align=PP_ALIGN.CENTER)
    txb(s, "→", Inches(8.35), Inches(3.7), Inches(0.5), Inches(0.6),
        size=28, color=ACCENT, align=PP_ALIGN.CENTER)

    for col, img, label in [
        (col2, "m16_parts_cropped.png", "Disassembled"),
        (col3, "m16_assembled.png",     "Assembled"),
    ]:
        p = asset(img)
        if os.path.exists(p):
            add_pic_fit(s, p, col, img_top, col_w, img_h)
        else:
            rect(s, col, img_top, col_w, img_h, fill=BOX_FILL, line=LINE_DIM)
            txb(s, f"[ add {img} ]", col, Inches(3.7), col_w, Inches(0.5),
                size=12, color=MUTED, align=PP_ALIGN.CENTER)
        txb(s, label, col, label_t, col_w, Inches(0.5),
            size=16, color=MUTED, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 1:30 | Running: 7:00\n\n"
        "Point at the pin: 'Remember this? A cotter pin — פין פזיל.'\n"
        "'Tiny. Costs nothing. But if it's missing, the M16 won't fire.'\n\n"
        "Disassembled: 'In the IDF, before you fire, you break the weapon down\n"
        "completely — knowing each part gives you confidence and control.'\n\n"
        "Assembled: 'That's what we're doing with AI today. By the end you'll know\n"
        "every part — and none of it will feel like magic.'")


def _roadmap_slide(prs, visible_count, title, notes):
    """Layer stack diagram; visible_count layers active (bottom-up)."""
    ALL_LAYERS = [("LLM", ACCENT), ("Agent", FG), ("Context Management", MUTED)]
    s = content_slide(prs, "THE MAP", title)

    left, width = Inches(1.8), Inches(9.5)
    gap, layer_h = Inches(0.1), Inches(1.5)
    y_bottom = Inches(5.9)

    for i, (name, col) in enumerate(ALL_LAYERS):
        y = y_bottom - i * (layer_h + gap)
        active = (i < visible_count)
        box = rect(s, left, y, width, layer_h,
                   fill=BOX_FILL if active else RGBColor(0x15, 0x21, 0x1E),
                   line=col if active else LINE_DIM,
                   line_w=Pt(1.5) if active else Pt(0.5))
        if active:
            txb(s, name, left + Inches(0.3), y + Inches(0.42),
                width - Inches(0.6), Inches(0.7),
                size=30, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_notes(s, notes)


def s07a_roadmap_llm(prs):
    _roadmap_slide(prs, 1, "Layer 1",
        "⏱ 0:20 | Running: 7:20\n\n"
        "'Let's start with the foundation. One box. LLM.'\n"
        "Everything else sits on top of this.")


def s07b_roadmap_agent(prs):
    _roadmap_slide(prs, 2, "Layer 2",
        "⏱ 0:20 | Running: 7:40\n\n"
        "'Agent sits on top of LLM. You can't have an agent without an LLM inside it.'")


def s07c_roadmap_full(prs):
    _roadmap_slide(prs, 3, "Three layers",
        "⏱ 0:40 | Running: 8:00\n\n"
        "Our roadmap. Three layers, bottom to top.\n\n"
        "LLM: the core unit. Agent: LLM + tools + a loop. "
        "Context Management: everything that controls what the LLM sees.\n\n"
        "By the end, every AI product you've used will make sense — they're all\n"
        "combinations of these three things.")


def _blackbox_slide(prs, show_answer):
    s = content_slide(prs, "LAYER 1 · LLM", "A black box with common human knowledge")

    txb(s, "INPUT", Inches(0.55), Inches(2.0), Inches(2), Inches(0.4),
        size=13, color=MUTED)
    code_block(s, '"Cato Networks is the best SASE company in the ___"',
               Inches(0.55), Inches(2.45), Inches(12.2), Inches(0.65), size=16)
    txb(s, "↓", Inches(0), Inches(3.15), Inches(13.33), Inches(0.5),
        size=28, color=ACCENT, align=PP_ALIGN.CENTER)

    rect(s, Inches(5.0), Inches(3.7), Inches(3.3), Inches(1.1),
         fill=RGBColor(0x0B, 0x15, 0x12), line=ACCENT, line_w=Pt(1.5))
    txb(s, "LLM", Inches(5.0), Inches(3.85), Inches(3.3), Inches(0.6),
        size=32, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    txb(s, "↓", Inches(0), Inches(4.85), Inches(13.33), Inches(0.5),
        size=28, color=ACCENT, align=PP_ALIGN.CENTER)
    txb(s, "OUTPUT", Inches(0.55), Inches(5.35), Inches(2), Inches(0.4),
        size=13, color=MUTED)

    if show_answer:
        code_block(s, '"Universe!"',
                   Inches(0.55), Inches(5.8), Inches(12.2), Inches(0.65), size=16)
    else:
        rect(s, Inches(0.55), Inches(5.8), Inches(12.2), Inches(0.65), fill=CODE_BG)

    txb(s, "Trained on most of the text ever written.  Thinks in patterns, not rules.  "
           "Its knowledge was frozen at training time.",
        Inches(0.55), Inches(6.65), Inches(12.2), Inches(0.5),
        size=16, color=MUTED, align=PP_ALIGN.CENTER)
    if show_answer:
        add_notes(s,
            "⏱ 0:30 | Running: 9:00\n\n"
            "'Universe! Not world — universe.' Let the room react.\n"
            "'The model has seen enough Cato marketing to know the answer.\n"
            "It's not thinking — it's completing the most probable next token.'")
    else:
        add_notes(s,
            "⏱ 0:30 | Running: 8:30\n\n"
            "Read the prompt out loud. Pause. 'What would you complete this with?'\n"
            "Let the room answer (most say 'world'). Then click to reveal.")


def s08a_llm_blackbox(prs):
    _blackbox_slide(prs, show_answer=False)


def s08a2_llm_blackbox_reveal(prs):
    _blackbox_slide(prs, show_answer=True)


def s08b_autocomplete(prs):
    """8b — Autocomplete can do logic"""
    s = content_slide(prs, "LAYER 1 · LLM", "Autocomplete can do logic")

    L_W, DIV, R_X, R_W = Inches(4.44), Inches(4.54), Inches(4.74), Inches(8.35)
    rect(s, DIV, Inches(2.0), Pt(1), Inches(4.5), fill=LINE_DIM)

    txb(s, "A 4-year-old", Inches(0.3), Inches(2.0), L_W, Inches(0.45),
        size=15, color=MUTED, italic=True)
    y = Inches(2.6)
    for prompt, ans in [('"The sky is ___"', '"blue"'), ('"Dogs say ___"', '"woof"')]:
        txb(s, prompt, Inches(0.3), y, L_W, Inches(0.45), size=20, color=FG, font=MONO)
        txb(s, f"→  {ans}", Inches(0.3), y + Inches(0.48), L_W, Inches(0.4),
            size=20, color=ACCENT, font=MONO)
        y += Inches(1.2)

    txb(s, "Logic  &  knowledge", R_X, Inches(2.0), R_W, Inches(0.45),
        size=15, color=MUTED, italic=True)
    txb(s, '"All humans are mortal.\nSocrates is human.\nTherefore Socrates is ___"',
        R_X, Inches(2.6), R_W, Inches(1.3), size=18, color=FG, font=MONO)
    txb(s, '→  "mortal"', R_X, Inches(3.95), R_W, Inches(0.4),
        size=18, color=ACCENT, font=MONO)
    txb(s, '"I travel to Sirius at 99%\nthe speed of light and return.\n'
           'Compared to my twin, I aged ___"',
        R_X, Inches(4.55), R_W, Inches(1.3), size=18, color=FG, font=MONO)
    txb(s, '→  "less"', R_X, Inches(5.9), R_W, Inches(0.4),
        size=18, color=ACCENT, font=MONO)

    txb(s, "The mechanism is trivial.  The scale is not.",
        Inches(0.55), Inches(6.55), Inches(12.2), Inches(0.5),
        size=17, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 2:00 | Running: 11:00\n\n"
        "Walk left to right; ask the room to complete each before revealing.\n"
        "Left: pure pattern matching. Right — Socrates: pure logic completed from\n"
        "everything ever written. Sirius: special relativity, twin paradox — the LLM\n"
        "completes 'less' from the corpus, not from first-principles reasoning.\n"
        "Same mechanism, two very different levels of abstraction.")


def s08c_context_sensitivity(prs):
    """8c — Same prompt, opposite output"""
    s = content_slide(prs, "LAYER 1 · LLM",
                      "The LLM sees the whole prompt — not just the end")
    code_block(s,
        'Prompt:  "A cat walked into a library and asked for a book about"\n'
        'Output:  "...fish. The librarian smiled and pointed to the nature section."',
        Inches(0.55), Inches(2.0), Inches(12.2), Inches(1.1), size=15)
    code_block(s,
        'Prompt:  "A car walked into a library and asked for a book about"\n'
        'Output:  "...roads and highways. The librarian — confused but helpful — reached for an atlas."',
        Inches(0.55), Inches(3.3), Inches(12.2), Inches(1.1), size=15)
    txb(s, "cat  vs  car  — one letter.",
        Inches(0.55), Inches(4.65), Inches(7), Inches(0.6),
        size=22, bold=True, color=ACCENT)
    txb(s, "The model reads every token.\n"
           "The context window is finite — what you put in it is everything.",
        Inches(0.55), Inches(5.45), Inches(12.2), Inches(0.9),
        size=18, color=MUTED, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 1:30 | Running: 12:00\n\n"
        "Read both prompts — one letter different. The model reads every token,\n"
        "left to right; they all matter. This is why prompt engineering exists: one\n"
        "word early can change behaviour for the whole conversation.\n"
        "Key point: context is a finite budget. What you put in it is everything.")


def s08d_hallucination(prs):
    """8d — Hallucination"""
    s = content_slide(prs, "LAYER 1 · LLM",
                      "Hallucination — autocomplete with no good data")
    code_block(s,
        'Prompt:  "Who won the 1987 regional chess\n'
        '          championship in Tulsa, Oklahoma?"\n\n'
        'Output:  "The 1987 championship was won by\n'
        '          David Harrington, a local teacher who..."',
        Inches(0.55), Inches(2.0), Inches(7.5), Inches(2.4), size=15)
    txb(s, "David Harrington\nprobably doesn't exist.",
        Inches(8.3), Inches(2.1), Inches(4.7), Inches(1.2),
        size=26, bold=True, color=ACCENT)
    txb(s, "Hallucination is not a bug.\nIt's autocomplete applied where\n"
           "there's no good data to complete from.",
        Inches(0.55), Inches(4.8), Inches(12), Inches(1.4),
        size=20, color=FG, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 1:30 | Running: 13:30\n\n"
        "David Harrington almost certainly doesn't exist — a plausible name and story,\n"
        "stated confidently, no warning. Not a bug they forgot to fix: when the training\n"
        "data has no good completion, the model still completes — it has to.\n"
        "Takeaway: confident tone means nothing. Verify specific facts.")


def _agent_diagram_slide(prs, eyebrow, title, img_name, notes):
    """Full-bleed agent diagram PNG below the title."""
    s = content_slide(prs, eyebrow, title)
    s.shapes.add_picture(asset(img_name),
                         Inches(0), Inches(1.85), Inches(13.33), Inches(5.5))
    add_notes(s, notes)


def s09a1_agent_llm(prs):
    _agent_diagram_slide(prs, "LAYER 2 · AGENT", "Agent  =  LLM",
        "agent_diagram_1.png",
        "⏱ 0:20 | Running: 14:20\n\n"
        "'At its core, an agent starts with just an LLM. It reads input and decides\n"
        "what to do — in text.'")


def s09a2_agent_llm_tools(prs):
    _agent_diagram_slide(prs, "LAYER 2 · AGENT", "Agent  =  LLM  +  Tools",
        "agent_diagram_2.png",
        "⏱ 0:20 | Running: 14:40\n\n"
        "'Add tools — web search, calculator, APIs. The LLM decides which tool to\n"
        "call; the framework runs it.'")


def s09a3_agent_loop(prs):
    _agent_diagram_slide(prs, "LAYER 2 · AGENT", "Agent  =  LOOP( LLM + Tools )",
        "agent_diagram_3.png",
        "⏱ 0:30 | Running: 15:10\n\n"
        "'Wrap it in a loop. The tool result goes back to the LLM, which re-reads\n"
        "everything and decides the next step — until it decides it's done.'")


def s09a4_agent_full(prs):
    _agent_diagram_slide(prs, "LAYER 2 · AGENT", "Agent  =  LOOP( LLM + Tools )",
        "agent_diagram_4.png",
        "⏱ 1:00 | Running: 16:00\n\n"
        "'User input enters at the LLM. At the bottom it asks: done? If yes — output\n"
        "exits as the Agent Output. If no — it loops, calls a tool, reads the result,\n"
        "asks again. One question in; everything else happens inside the loop.'")


# Reusable agent walk-through layout ------------------------------------------

def _agent_slide(prs, call_num, total, context_lines, new_lines, decision):
    s = content_slide(prs, f"LAYER 2 · AGENT  —  CALL {call_num} of {total}",
                      "Context accumulates with every step")

    box_left, box_top = Inches(0.45), Inches(1.95)
    box_w, box_h = Inches(8.2), Inches(5.25)
    rect(s, box_left, box_top, box_w, box_h, fill=CODE_BG)

    tf_box = s.shapes.add_textbox(
        box_left + Inches(0.18), box_top + Inches(0.12),
        box_w - Inches(0.36), box_h - Inches(0.24))
    tf = tf_box.text_frame
    tf.word_wrap = False
    first = True
    for text, color in context_lines + new_lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        run = p.add_run()
        run.text = text
        run.font.size = Pt(12)
        run.font.name = MONO
        run.font.color.rgb = color

    d_left, d_top, d_w = Inches(8.9), Inches(1.95), Inches(4.1)
    txb(s, "LLM decided:", d_left, d_top, d_w, Inches(0.4), size=13, color=MUTED)
    rect(s, d_left, d_top + Inches(0.42), d_w, Inches(1.5),
         fill=RGBColor(0x12, 0x22, 0x1E), line=ACCENT, line_w=Pt(1))
    txb(s, decision, d_left + Inches(0.15), d_top + Inches(0.55),
        d_w - Inches(0.3), Inches(1.2), size=15, color=ACCENT, font=MONO)

    txb(s, "▌ tool result (new)", d_left, d_top + Inches(2.2), d_w, Inches(0.4),
        size=13, color=_NEW)
    txb(s, "▌ previous LLM response", d_left, d_top + Inches(2.65), d_w, Inches(0.4),
        size=13, color=_AI)
    txb(s, "Context grows every step.\nLLM re-reads all of it.",
        d_left, d_top + Inches(3.2), d_w, Inches(1.0), size=13, color=MUTED)
    return s


def s09b_developer_wrote(prs):
    """9b — Just the human question"""
    s = content_slide(prs, "LAYER 2 · AGENT", "The developer wrote one question")
    rect(s, Inches(2.5), Inches(2.7), Inches(8.3), Inches(1.2),
         fill=CODE_BG, line=_HEAD, line_w=Pt(1))
    txb(s, "Who is Taylor Swift's boyfriend?\n"
           "Find out his age and calculate the square root of his age.",
        Inches(2.7), Inches(2.85), Inches(7.9), Inches(0.85),
        size=15, color=FG, font=MONO)
    add_notes(s,
        "⏱ 0:20 | Running: 15:20\n\n"
        "Just the question. 'This is what the developer typed. One question.'\n"
        "Click to show what the agent wraps around it.")


def s09b2_developer_full_prompt(prs):
    """9b2 — Full prompt wrapped in system context (hidden)"""
    s = content_slide(prs, "LAYER 2 · AGENT", "The agent wraps it in context")
    hide(s)
    rect(s, Inches(0.55), Inches(1.95), Inches(12.2), Inches(4.9),
         fill=RGBColor(0x12, 0x22, 0x1E), line=ACCENT, line_w=Pt(1))
    txb(s, "[SYSTEM]", Inches(0.75), Inches(2.05), Inches(11), Inches(0.4),
        size=13, color=ACCENT, font=MONO)
    txb(s, "You are a helpful research assistant.\n"
           "1. Search the web for any facts you need.\n"
           "2. Use the calculator for any math.\n"
           "3. Always show your reasoning step by step.\n\n"
           "Available tools:\n"
           "  web_search(query)   — search the internet\n"
           "  calculator(expr)    — evaluate a math expression",
        Inches(0.75), Inches(2.48), Inches(11.8), Inches(2.1),
        size=14, color=MUTED, font=MONO)
    rect(s, Inches(2.5), Inches(4.7), Inches(8.3), Inches(1.5),
         fill=CODE_BG, line=_HEAD, line_w=Pt(1))
    txb(s, "[HUMAN]", Inches(2.7), Inches(4.85), Inches(8.0), Inches(0.4),
        size=13, color=_HEAD, font=MONO)
    txb(s, "Who is Taylor Swift's boyfriend?\n"
           "Find out his age and calculate the square root of his age.",
        Inches(2.7), Inches(5.25), Inches(7.9), Inches(0.75),
        size=15, color=FG, font=MONO)
    add_notes(s,
        "⏱ 0:40 | Running: 16:00\n\n"
        "'The agent didn't change the question — it wrapped it. System instructions,\n"
        "tools list, then the original question nested inside.' Point at the tools list:\n"
        "'This is how the LLM knows what tools exist — just text. Not a function\n"
        "registry. A description.' Click to watch call #1.")


def s09c_call1(prs):
    new = [
        ("[SYSTEM]",                                                   _HEAD),
        ("You are a helpful research assistant.",                      _NEW),
        ("When given a task:",                                         _NEW),
        ("  1. Search the web for any facts you need.",                _NEW),
        ("  2. Use the calculator for any math.",                      _NEW),
        ("  3. Always show your reasoning step by step.",              _NEW),
        ("",                                                           _NEW),
        ("Available tools:",                                           _NEW),
        ("  web_search(query)   — search the internet",           _NEW),
        ("  calculator(expr)    — evaluate a math expression",     _NEW),
        ("",                                                           _NEW),
        ("[HUMAN]",                                                    _HEAD),
        ("Who is Taylor Swift's boyfriend?",                           _NEW),
        ("Find out his age and calculate the square root of his age.", _NEW),
    ]
    s = _agent_slide(prs, 1, 4, [], new,
                     'web_search(\n  "Taylor Swift\n   boyfriend")')
    add_notes(s,
        "⏱ 1:00 | Running: 16:45\n\n"
        "Everything is green — first call, all new. The LLM reads top to bottom:\n"
        "I'm a research assistant, I have these tools, here's the question. It decides\n"
        "it needs to search, and outputs a tool call — in text.")


def s09d_call2(prs):
    ctx = [
        ("[SYSTEM]",                                                   _HEAD),
        ("You are a helpful research assistant. ...",                  _DIM),
        ("Available tools: web_search, calculator",                   _DIM),
        ("",                                                           _DIM),
        ("[HUMAN]",                                                    _HEAD),
        ("Who is Taylor Swift's boyfriend? ...",                       _DIM),
        ("",                                                           _DIM),
        ("[LLM]",                                                      _HEAD),
        ("I'll help find information...",                              _DIM),
        ('→ web_search("Taylor Swift boyfriend")',                _AI),
    ]
    new = [
        ("",                                                           _NEW),
        ("[TOOL RESULT]",                                              _HEAD),
        ("Taylor Swift and Travis Kelce confirmed their romance",      _NEW),
        ("in 2023. The couple announced their engagement on",          _NEW),
        ("August 26, 2025...",                                         _NEW),
    ]
    s = _agent_slide(prs, 2, 4, ctx, new,
                     'web_search(\n  "Travis Kelce\n   age born")')
    add_notes(s,
        "⏱ 1:00 | Running: 18:00\n\n"
        "Grey = already seen, amber = previous LLM response, green = new tool result.\n"
        "The search result is appended; the entire context is sent again. The LLM is\n"
        "never told it's on step 2 — it figures that out by re-reading from the top.")


def s09e_call3(prs):
    ctx = [
        ("[SYSTEM]  ...",                                              _DIM),
        ("[HUMAN]   Who is Taylor Swift's boyfriend? ...",             _DIM),
        ("[LLM]     I'll help... -> web_search(\"Taylor Swift...\")", _DIM),
        ("[TOOL]    Taylor Swift and Travis Kelce...",                 _DIM),
        ('[LLM]     → web_search("Travis Kelce age born")',       _AI),
    ]
    new = [
        ("",                                                           _NEW),
        ("[TOOL RESULT]",                                              _HEAD),
        ("Born: October 5, 1989 (age 35).",                           _NEW),
        ("Travis Kelce, born in Westlake, Ohio,",                      _NEW),
        ("is currently 35 years old...",                              _NEW),
    ]
    s = _agent_slide(prs, 3, 4, ctx, new, 'calculator(\n  "sqrt(35)")')
    add_notes(s,
        "⏱ 1:00 | Running: 18:45\n\n"
        "Context keeps growing; everything from calls 1-2 is still there and re-read.\n"
        "Now it knows: boyfriend is Kelce, age 35. What's left? The square root —\n"
        "it switches tools to the calculator. Still just text output.")


def s09f_call4(prs):
    ctx = [
        ("[SYSTEM]  ...",                                              _DIM),
        ("[HUMAN]   Who is Taylor Swift's boyfriend? ...",             _DIM),
        ('[LLM]     → web_search("Taylor Swift boyfriend")',      _DIM),
        ("[TOOL]    Taylor Swift and Travis Kelce...",                 _DIM),
        ('[LLM]     → web_search("Travis Kelce age born")',       _DIM),
        ("[TOOL]    Born: October 5, 1989 (age 35)...",                _DIM),
        ("[LLM]     Now let me calculate...",                          _DIM),
        ('[LLM]     → calculator("sqrt(35)")',                    _AI),
    ]
    new = [
        ("",                                                           _NEW),
        ("[TOOL RESULT]",                                              _HEAD),
        ("5.916079783099616",                                          _NEW),
        ("",                                                           _NEW),
        ("[LLM — FINAL ANSWER]",                                  _HEAD),
        ("Taylor Swift's boyfriend is Travis Kelce.",                  _AI),
        ("His age: 35.  √35 ≈ 5.92",                         _AI),
    ]
    s = _agent_slide(prs, 4, 4, ctx, new, "Done.\nNo more tools\nneeded.")
    add_notes(s,
        "⏱ 1:00 | Running: 19:45\n\n"
        "Full history dimmed; new green: calculator result and final answer. The LLM\n"
        "reads four calls' worth of context, sees the result, and decides it has\n"
        "everything — no more tools. One question from the developer; 4 LLM calls,\n"
        "2 web searches, 1 calculator call underneath. That's an agent.")


def s10a_context_problem(prs):
    """10a — Context is limited"""
    s = content_slide(prs, "LAYER 3 · CONTEXT MANAGEMENT",
                      "Context is limited. We need to manage it.")
    rect(s, Inches(6.65), Inches(2.0), Pt(1), Inches(3.7), fill=LINE_DIM)

    txb(s, "Human intelligence is unlimited too.",
        Inches(0.55), Inches(2.1), Inches(5.8), Inches(0.55),
        size=19, bold=True, color=FG)
    txb(s, "But it needs resources:\ntime, food, sleep, motivation.",
        Inches(0.55), Inches(2.75), Inches(5.8), Inches(1.0), size=18, color=MUTED)
    txb(s, "AI agents mostly need context.",
        Inches(0.55), Inches(3.85), Inches(5.8), Inches(0.55),
        size=19, bold=True, color=ACCENT)

    txb(s, "Context fills up fast.",
        Inches(6.9), Inches(2.1), Inches(6.1), Inches(0.55), size=22, bold=True, color=FG)
    txb(s, "Larger context costs significantly more.",
        Inches(6.9), Inches(2.85), Inches(6.1), Inches(0.55), size=22, bold=True, color=FG)

    txb(s, "Every agent manages context on its own — some vendors better than others.",
        Inches(0.55), Inches(5.2), Inches(12.2), Inches(0.5),
        size=16, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s, "Our job: manage context on top of that, and help the agent manage its own.",
        Inches(0.55), Inches(5.75), Inches(12.2), Inches(0.5),
        size=17, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 1:30 | Running: 22:30\n\n"
        "Human intelligence has no hard limit either — but it needs fuel; deprive it\n"
        "and performance degrades. AI is the same: wrong or too little context and it\n"
        "degrades. Real agents do 20-50 steps and fill the window fast. Every agent\n"
        "auto-manages some of this; our job is to manage on top and help it manage its own.")


def s10b_skills_filesystem(prs):
    """10b — Skills and the filesystem"""
    s = content_slide(prs, "LAYER 3 · CONTEXT MANAGEMENT",
                      "Example: skills and the filesystem")
    txb(s, "A skill is a file on disk.",
        Inches(0.55), Inches(2.0), Inches(12), Inches(0.6), size=26, bold=True, color=FG)
    txb(s, "It has a name and a description. The LLM reads the description\n"
           "and decides whether to load it — like a pointer into the filesystem.",
        Inches(0.55), Inches(2.65), Inches(12), Inches(0.8), size=18, color=MUTED)
    code_block(s,
        'skill: "commit"\ndescription: "Use when the user wants to create a git commit..."',
        Inches(0.55), Inches(3.55), Inches(12), Inches(1.0), size=15)
    txb(s, "Why this matters:", Inches(0.55), Inches(4.75), Inches(4), Inches(0.45),
        size=16, bold=True, color=ACCENT)
    y = Inches(5.25)
    for b in ["Load / unload on demand  — keep the context lean",
              "Share with colleagues     — put skills in a repo",
              "Community skills          — use what others built",
              "Vendor-independent        — just text files"]:
        txb(s, f"→  {b}", Inches(0.55), y, Inches(12), Inches(0.42),
            size=16, color=FG, font=MONO)
        y += Inches(0.42)
    add_notes(s,
        "⏱ 1:30 | Running: 24:00\n\n"
        "A skill is literally a text file; its description tells the LLM when to load it\n"
        "— the LLM pattern-matches the description against the task. Four wins: load/\n"
        "unload (pay for context only when needed), share (commit the folder), community\n"
        "(use others' skills, like npm/pip), vendor-independent (just text). The\n"
        "filesystem is your context-management layer — you already know how to use it.")


def s10c_ecosystem(prs):
    """10c — The ecosystem"""
    s = content_slide(prs, "LAYER 3 · CONTEXT MANAGEMENT",
                      "The ecosystem — different names, same idea")
    txb(s, "Once you see it, you can't unsee it:",
        Inches(0.55), Inches(2.0), Inches(12), Inches(0.5), size=20, color=MUTED)
    y = Inches(2.65)
    for name, desc in [
        ("Cursor rules",                "Project-level instructions loaded into every prompt"),
        ("Claude Projects",             "Persistent context shared across conversations"),
        ("GitHub Copilot instructions", "Repo-level context injected into the coding agent"),
        ("MCP servers",                 "Live data sources pulled into context on demand"),
        ("LangChain / LlamaIndex",      "Frameworks that manage context routing at scale"),
    ]:
        txb(s, name, Inches(0.55), y, Inches(4.5), Inches(0.48),
            size=17, bold=True, color=ACCENT)
        txb(s, desc, Inches(5.2), y + Inches(0.04), Inches(7.6), Inches(0.44),
            size=16, color=FG)
        y += Inches(0.62)
    txb(s, "Some are vendor-specific. Some are open. All are context management.",
        Inches(0.55), Inches(6.0), Inches(12), Inches(0.5),
        size=17, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s, "Learn the concept once. Apply it everywhere.",
        Inches(0.55), Inches(6.55), Inches(12), Inches(0.5),
        size=18, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_notes(s,
        "⏱ 1:30 | Running: 25:30\n\n"
        "You've used some of these already: Cursor rules, Claude Projects, Copilot\n"
        "instructions, MCP, LangChain/LlamaIndex. Different names, vendors, polish —\n"
        "all answering one question: what goes in the context window? Learn the concept\n"
        "once and you can evaluate any new tool by asking how it manages context.")


def s10d_layer_summary(prs):
    """10d — Three-layer summary + agent diagram"""
    s = content_slide(prs, "PUTTING IT TOGETHER", "The three layers")

    layers = [("Context Management", MUTED), ("Agent", FG), ("LLM", ACCENT)]
    lft, lft_w = Inches(0.4), Inches(5.2)
    layer_h, gap = Inches(1.3), Inches(0.08)
    y_bottom = Inches(6.1)
    agent_box_top = None
    for i, (name, col) in enumerate(layers):
        y = y_bottom - i * (layer_h + gap)
        if name == "Agent":
            agent_box_top = y
        rect(s, lft, y, lft_w, layer_h, fill=BOX_FILL, line=col,
             line_w=Pt(1.5) if col != MUTED else Pt(0.5))
        txb(s, name, lft + Inches(0.2), y + Inches(0.38),
            lft_w - Inches(0.4), Inches(0.6),
            size=22, bold=True, color=col, align=PP_ALIGN.CENTER)

    exp_y = agent_box_top + layer_h / 2 - Inches(0.3)
    txb(s, "«", lft + lft_w + Inches(0.05), exp_y, Inches(0.7), Inches(0.6),
        size=28, bold=True, color=FG, align=PP_ALIGN.CENTER)

    img_l = lft + lft_w + Inches(0.65)
    s.shapes.add_picture(asset("agent_diagram_4.png"),
                         img_l, Inches(1.9), Inches(13.33) - img_l - Inches(0.2), Inches(5.3))
    add_notes(s,
        "⏱ 0:30 | Running: 26:00\n\n"
        "Quick callback. LLM at the bottom (autocomplete at scale), Agent in the middle\n"
        "(LLM + tools + loop), Context Management on top (what the LLM sees). These three\n"
        "describe every AI product you'll use or build. Now — what to do with them.")


def s11_tips(prs):
    """11 — Takeaways"""
    s = content_slide(prs, "TAKEAWAYS", "Using AI well")
    tips = [
        ('"Give me the right context\nand I shall move the world"',
         "AI can do almost anything —\nif you manage its context correctly."),
        ("Better agent = less manual context",
         "The best agents need the least hand-holding.\nThat's what you're optimising for."),
        ("AI disappoints you?",
         "Ask yourself: what did I forget to give it?"),
    ]
    y = Inches(2.0)
    for header, body in tips:
        txb(s, header, Inches(0.55), y, Inches(5.8), Inches(0.9),
            size=20, bold=True, color=ACCENT, italic=True)
        txb(s, body, Inches(6.5), y + Inches(0.05), Inches(6.5), Inches(0.85),
            size=18, color=FG)
        y += Inches(1.6)
    add_notes(s,
        "⏱ 3:00 | Running: 26:15\n\n"
        "Take your time — this is the payoff.\n"
        "1. Archimedes: 'Give me a lever long enough...' — give the LLM the right\n"
        "context and it can do almost anything. The limit is the context, not the model.\n"
        "2. Better agent = less context management: a great agent figures it out from\n"
        "minimal context. That's what you're building towards.\n"
        "3. If AI disappoints — ask what you forgot to give it. 9/10 it's the context.")


def s12_thanks(prs):
    """12 — Thank you (Thank you slide Black)"""
    s = add(prs, "Thank you slide Black")
    set_ph(s, 0, "Thank you", color=FG)
    txb(s, "Questions?", Inches(3.3), Inches(4.8), Inches(6), Inches(0.7),
        size=28, color=ACCENT)
    add_notes(s,
        "⏱ 3:45 | Running: 30:00\n\n"
        "Optional callback before Q&A: 'You now know the parts. Go fire the weapon.'\n"
        "Budget ~3-4 min for Q&A. Expect: when to use an agent vs a plain LLM call\n"
        "(real-world data / multi-step), best model (depends; concepts are the same),\n"
        "how we use this at Cato (good opening for a follow-up session).")


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def build():
    prs = new_prs()

    s01_title(prs)
    s02_intro_me(prs)
    s03_geek_origin(prs)
    s04a_done_before_grid(prs)       # variant A1 — pick grid or timeline, remove the other
    s04b_done_before_timeline(prs)   # variant A2
    s05_ai_different(prs)
    s06_pin_reveal(prs)
    s07a_roadmap_llm(prs)
    s07b_roadmap_agent(prs)
    s07c_roadmap_full(prs)
    s08a_llm_blackbox(prs)
    s08a2_llm_blackbox_reveal(prs)
    s08b_autocomplete(prs)
    s08c_context_sensitivity(prs)
    s08d_hallucination(prs)
    s09a1_agent_llm(prs)
    s09a2_agent_llm_tools(prs)
    s09a3_agent_loop(prs)
    s09a4_agent_full(prs)
    s09b_developer_wrote(prs)
    s09b2_developer_full_prompt(prs)
    s09c_call1(prs)
    s09d_call2(prs)
    s09e_call3(prs)
    s09f_call4(prs)
    s10a_context_problem(prs)
    s10b_skills_filesystem(prs)
    s10c_ecosystem(prs)
    s10d_layer_summary(prs)
    s11_tips(prs)
    s12_thanks(prs)

    out = os.path.join(HERE, "understanding_ai_for_geeks.pptx")
    prs.save(out)
    print(f"Saved: {out}  ({len(prs.slides)} slides)")
    return out


if __name__ == "__main__":
    build()
