"""
PDF generation for Auro — welcome letter and therapist report,
styled to match the app's "Neon Night" dark theme: charcoal page
background, glowing blue / green / red accents, modern sans type.
"""
import io
import base64
from datetime import datetime
from xml.sax.saxutils import escape as _xml_escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

BG = colors.HexColor("#0a0e14")
PANEL = colors.HexColor("#131b25")
BORDER = colors.HexColor("#2a3542")
BLUE = colors.HexColor("#3aa0ff")
GREEN = colors.HexColor("#35e08a")
RED = colors.HexColor("#ff4d6a")
TEXT = colors.HexColor("#e8f0f7")
TEXT_DIM = colors.HexColor("#93a4b8")


def _safe(value):
    """Escape user-entered text so a stray '&', '<', or '>' can't break
    ReportLab's Paragraph XML parser and crash the whole report build.
    Always route free-text fields (names, notes, CBT entries, etc.) through
    this before putting them in a Paragraph."""
    if value is None:
        return ""
    return _xml_escape(str(value))


def _neon_page(canvas, doc):
    """Dark page background with a glowing blue/green frame, drawn on every page."""
    canvas.saveState()
    w, h = A4

    canvas.setFillColor(BG)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    margin = 1.0 * cm
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1.4)
    canvas.rect(margin, margin, w - 2 * margin, h - 2 * margin)
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(0.6)
    inset = margin + 0.22 * cm
    canvas.rect(inset, inset, w - 2 * inset, h - 2 * inset)

    def dot(cx, cy, color, r=3.2):
        canvas.setFillColor(color)
        canvas.circle(cx, cy, r, fill=1, stroke=0)

    corners = [(inset, inset), (w - inset, inset), (inset, h - inset), (w - inset, h - inset)]
    dot_colors = [BLUE, GREEN, RED, BLUE]
    for (cx, cy), col in zip(corners, dot_colors):
        dot(cx, cy, col)

    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(TEXT_DIM)
    canvas.drawCentredString(w / 2, margin - 0.1 * cm + 4, "Auro — a quiet mind, kept")
    canvas.restoreState()


def _base_doc(path):
    doc = BaseDocTemplate(path, pagesize=A4,
                           topMargin=2.4 * cm, bottomMargin=2.2 * cm,
                           leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    template = PageTemplate(id="neon", frames=[frame], onPage=_neon_page)
    doc.addPageTemplates([template])
    return doc


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="AuroTitle", fontName="Helvetica-Bold", fontSize=28,
        textColor=BLUE, alignment=TA_CENTER, spaceAfter=4, leading=32
    ))
    styles.add(ParagraphStyle(
        name="AuroSub", fontName="Helvetica-Oblique", fontSize=12.5,
        textColor=GREEN, alignment=TA_CENTER, spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name="AuroHeading", fontName="Helvetica-Bold", fontSize=14.5,
        textColor=BLUE, spaceBefore=14, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="AuroBody", fontName="Helvetica", fontSize=10.8,
        textColor=TEXT, alignment=TA_LEFT, leading=16, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="AuroSignoff", fontName="Helvetica-Oblique", fontSize=11,
        textColor=GREEN, alignment=TA_CENTER, spaceBefore=20
    ))
    return styles


def generate_welcome_pdf(user_name, phone, age, sex, email, location, out_path):
    """Welcome letter delivered right after registration."""
    styles = _styles()
    story = []

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("A U R O", styles["AuroTitle"]))
    story.append(Paragraph("A Mental Health Tracker for the quiet parts of your day", styles["AuroSub"]))
    story.append(HRFlowable(width="60%", thickness=1, color=BLUE, spaceAfter=16, hAlign="CENTER"))

    story.append(Paragraph(f"Dear {_safe(user_name)},", styles["AuroBody"]))
    story.append(Paragraph(
        "Welcome to Auro. Think of this as the little glowing lamp by the door — "
        "a private, unhurried space where your moods, your sleep, and your days can be "
        "noted down without judgement, and read back to you in patterns you might "
        "otherwise miss.", styles["AuroBody"]
    ))

    story.append(Paragraph("Your account", styles["AuroHeading"]))
    data = [
        ["Name", _safe(user_name)],
        ["Phone", _safe(phone)],
        ["Age", str(age) if age else "—"],
        ["Sex", _safe(sex) or "—"],
        ["Email", _safe(email) or "—"],
        ["Location", _safe(location) or "—"],
        ["Registered on", datetime.now().strftime("%d %B %Y")],
    ]
    tbl = Table(data, colWidths=[4.2 * cm, 9.5 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 0), (0, -1), BLUE),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
    ]))
    story.append(tbl)

    story.append(Paragraph("What you can do here", styles["AuroHeading"]))
    for line in [
        "Log your mood each day, alongside sleep and exercise — the two quiet pillars that shape most moods.",
        "See patterns surface over weeks and months, in clean trend and correlation charts.",
        "Work through short CBT exercises when a thought needs to be examined rather than believed.",
        "Export a clean report for your therapist whenever you'd like a second pair of eyes.",
    ]:
        story.append(Paragraph(f"&bull;&nbsp;&nbsp;{line}", styles["AuroBody"]))

    story.append(Paragraph(
        "This is not a replacement for professional care. If you are in crisis or in danger, "
        "please reach out to a licensed professional or local emergency services right away.",
        styles["AuroBody"]
    ))

    story.append(Paragraph("With warmth, from the house of Auro.", styles["AuroSignoff"]))

    doc = _base_doc(out_path)
    doc.build(story)
    return out_path


def generate_therapist_report_pdf(user, logs, cbt_entries, charts, stats, out_path, analysis=None, plan=None):
    """
    user: sqlite3.Row
    logs: list of mood_logs rows
    cbt_entries: list of cbt_entries rows
    charts: dict of base64 png strings {trend, sleep, exercise}
    stats: dict from correlation_stats()
    analysis: optional list of narrative paragraphs from insights.build_graph_analysis()
    plan: optional dict from insights.build_lifestyle_plan()
    """
    styles = _styles()
    story = []

    story.append(Paragraph("Auro — Clinical Summary Report", styles["AuroTitle"]))
    story.append(Paragraph("Prepared for review by a mental health professional", styles["AuroSub"]))
    story.append(HRFlowable(width="60%", thickness=1, color=BLUE, spaceAfter=14, hAlign="CENTER"))

    info = [
        ["Client", _safe(user["name"])],
        ["Age / Sex", f"{user['age'] or '—'} / {_safe(user['sex']) or '—'}"],
        ["Location", _safe(user["location"]) or "—"],
        ["Report generated", datetime.now().strftime("%d %B %Y, %H:%M")],
        ["Entries covered", f"{len(logs)} daily log(s)"],
    ]
    tbl = Table(info, colWidths=[4.2 * cm, 9.5 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), BLUE),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    if logs:
        avg_mood = round(sum(r["mood_score"] for r in logs) / len(logs), 1)
        anx_vals = [r["anxiety_score"] for r in logs if r["anxiety_score"] is not None]
        avg_anx = round(sum(anx_vals) / len(anx_vals), 1) if anx_vals else None
        sleep_vals = [r["sleep_hours"] for r in logs if r["sleep_hours"] is not None]
        avg_sleep = round(sum(sleep_vals) / len(sleep_vals), 1) if sleep_vals else None
        ex_vals = [r["exercise_minutes"] for r in logs if r["exercise_minutes"] is not None]
        avg_ex = round(sum(ex_vals) / len(ex_vals), 1) if ex_vals else None

        story.append(Paragraph("Summary statistics", styles["AuroHeading"]))
        summary_rows = [
            ["Average mood (1-10)", str(avg_mood)],
            ["Average anxiety (1-10)", str(avg_anx) if avg_anx is not None else "—"],
            ["Average sleep (hours/night)", str(avg_sleep) if avg_sleep is not None else "—"],
            ["Average exercise (min/day)", str(avg_ex) if avg_ex is not None else "—"],
            ["Sleep–mood correlation (r)", str(stats.get("sleep_corr")) if stats.get("sleep_corr") is not None else "insufficient data"],
            ["Exercise–mood correlation (r)", str(stats.get("exercise_corr")) if stats.get("exercise_corr") is not None else "insufficient data"],
        ]
        stbl = Table(summary_rows, colWidths=[7.5 * cm, 6.2 * cm])
        stbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("BACKGROUND", (0, 0), (-1, -1), PANEL),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(stbl)
        story.append(Spacer(1, 10))

    if charts.get("trend"):
        try:
            story.append(Paragraph("Mood & anxiety trend", styles["AuroHeading"]))
            img_data = base64.b64decode(charts["trend"])
            story.append(Image(io.BytesIO(img_data), width=15.5 * cm, height=7 * cm))
        except Exception:
            pass

    if charts.get("sleep") or charts.get("exercise"):
        story.append(Paragraph("Correlations", styles["AuroHeading"]))
        if charts.get("sleep"):
            try:
                story.append(Image(io.BytesIO(base64.b64decode(charts["sleep"])), width=9.5 * cm, height=7 * cm))
            except Exception:
                pass
        if charts.get("exercise"):
            try:
                story.append(Image(io.BytesIO(base64.b64decode(charts["exercise"])), width=9.5 * cm, height=7 * cm))
            except Exception:
                pass

    if analysis:
        story.append(Paragraph("Graph analysis", styles["AuroHeading"]))
        for para in analysis:
            story.append(Paragraph(_safe(para), styles["AuroBody"]))
        story.append(Spacer(1, 6))

    if cbt_entries:
        story.append(Paragraph("Recent CBT thought-records", styles["AuroHeading"]))
        for e in cbt_entries[:8]:
            story.append(Paragraph(f"<b>{_safe(e['entry_date'])}</b> — {_safe(e['exercise_type'].replace('_',' ').title())}", styles["AuroBody"]))
            if e["situation"]:
                story.append(Paragraph(f"Situation: {_safe(e['situation'])}", styles["AuroBody"]))
            if e["automatic_thought"]:
                story.append(Paragraph(f"Automatic thought: {_safe(e['automatic_thought'])}", styles["AuroBody"]))
            if e["balanced_thought"]:
                story.append(Paragraph(f"Balanced thought: {_safe(e['balanced_thought'])}", styles["AuroBody"]))
            if e["mood_before"] is not None and e["mood_after"] is not None:
                story.append(Paragraph(f"Mood shift: {e['mood_before']} &rarr; {e['mood_after']}", styles["AuroBody"]))
            story.append(HRFlowable(width="100%", thickness=0.4, color=BORDER, spaceAfter=8, spaceBefore=4))

    if plan:
        story.append(Paragraph("Suggested weekly lifestyle plan", styles["AuroHeading"]))
        story.append(Paragraph(_safe(plan["wind_down_note"]), styles["AuroBody"]))
        story.append(Spacer(1, 4))

        story.append(Paragraph("Weekday routine", styles["AuroHeading"]))
        wd_rows = [[t, _safe(desc)] for t, desc in plan["weekday_routine"]]
        wd_tbl = Table(wd_rows, colWidths=[3.4 * cm, 10.3 * cm])
        wd_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.2),
            ("TEXTCOLOR", (0, 0), (0, -1), BLUE),
            ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
            ("BACKGROUND", (0, 0), (-1, -1), PANEL),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(wd_tbl)
        story.append(Spacer(1, 8))

        story.append(Paragraph("Weekend routine", styles["AuroHeading"]))
        we_rows = [[t, _safe(desc)] for t, desc in plan["weekend_routine"]]
        we_tbl = Table(we_rows, colWidths=[3.4 * cm, 10.3 * cm])
        we_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.2),
            ("TEXTCOLOR", (0, 0), (0, -1), GREEN),
            ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
            ("BACKGROUND", (0, 0), (-1, -1), PANEL),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(we_tbl)
        story.append(Spacer(1, 8))

        for heading, items in [
            ("Eating structure", plan["eating_structure"]),
            ("Exercise plan", plan["exercise_plan"]),
            ("Activities to stay engaged", plan["engagement_activities"]),
        ]:
            story.append(Paragraph(heading, styles["AuroHeading"]))
            for line in items:
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{_safe(line)}", styles["AuroBody"]))
            story.append(Spacer(1, 4))

    story.append(Paragraph(
        "This report is generated from client-entered self-report data and is intended "
        "to support, not replace, clinical judgement.", styles["AuroBody"]
    ))

    doc = _base_doc(out_path)
    doc.build(story)
    return out_path