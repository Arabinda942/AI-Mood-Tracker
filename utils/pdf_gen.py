"""
PDF generation for Auro — welcome letter and therapist report,
styled after Rajbari (Bengali heritage palace) motifs: deep maroon,
antique gold rule lines, ornamental borders, serif typography.
"""
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

MAROON = colors.HexColor("#5A1A24")
GOLD = colors.HexColor("#C9A24B")
TEAL = colors.HexColor("#1F4B4A")
IVORY = colors.HexColor("#F3E9D2")
INK = colors.HexColor("#2B1810")


def _rajbari_border(canvas, doc):
    """Draw an ornamental double-line palace-style border on every page."""
    canvas.saveState()
    w, h = A4
    margin = 1.0 * cm
    # outer gold line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.6)
    canvas.rect(margin, margin, w - 2 * margin, h - 2 * margin)
    # inner maroon line
    canvas.setStrokeColor(MAROON)
    canvas.setLineWidth(0.7)
    inset = margin + 0.22 * cm
    canvas.rect(inset, inset, w - 2 * inset, h - 2 * inset)

    # corner flourishes (small diamond motifs, Rajbari jali-inspired)
    def diamond(cx, cy, size=6):
        canvas.setFillColor(GOLD)
        canvas.setStrokeColor(MAROON)
        p = canvas.beginPath()
        p.moveTo(cx, cy + size)
        p.lineTo(cx + size, cy)
        p.lineTo(cx, cy - size)
        p.lineTo(cx - size, cy)
        p.close()
        canvas.drawPath(p, fill=1, stroke=1)

    corners = [
        (inset, inset), (w - inset, inset),
        (inset, h - inset), (w - inset, h - inset)
    ]
    for cx, cy in corners:
        diamond(cx, cy)

    # footer
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(MAROON)
    canvas.drawCentredString(w / 2, margin - 0.1 * cm + 4, "Auro — a quiet mind, kept")
    canvas.restoreState()


def _base_doc(path):
    doc = BaseDocTemplate(path, pagesize=A4,
                           topMargin=2.4 * cm, bottomMargin=2.2 * cm,
                           leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    template = PageTemplate(id="rajbari", frames=[frame], onPage=_rajbari_border)
    doc.addPageTemplates([template])
    return doc


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="AuroTitle", fontName="Times-Bold", fontSize=28,
        textColor=MAROON, alignment=TA_CENTER, spaceAfter=4, leading=32
    ))
    styles.add(ParagraphStyle(
        name="AuroSub", fontName="Times-Italic", fontSize=13,
        textColor=TEAL, alignment=TA_CENTER, spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name="AuroHeading", fontName="Times-Bold", fontSize=15,
        textColor=MAROON, spaceBefore=14, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="AuroBody", fontName="Times-Roman", fontSize=11.5,
        textColor=INK, alignment=TA_LEFT, leading=17, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="AuroSignoff", fontName="Times-Italic", fontSize=11.5,
        textColor=MAROON, alignment=TA_CENTER, spaceBefore=20
    ))
    return styles


def generate_welcome_pdf(user_name, phone, age, sex, email, location, out_path):
    """Welcome letter delivered right after registration."""
    styles = _styles()
    story = []

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("आ &nbsp; U R O", styles["AuroTitle"]))
    story.append(Paragraph("A Mental Health Tracker, kept in the manner of an old Bengali household", styles["AuroSub"]))
    story.append(HRFlowable(width="60%", thickness=1, color=GOLD, spaceAfter=16, hAlign="CENTER"))

    story.append(Paragraph(f"Dear {user_name},", styles["AuroBody"]))
    story.append(Paragraph(
        "Welcome to Auro. Consider this letter the brass nameplate at the gate of a "
        "Rajbari — the old zamindari houses of Bengal, where every courtyard held a "
        "quiet room set aside for rest and reflection. Auro is built to be that room: "
        "a private, unhurried space where your moods, your sleep, and your days can be "
        "noted down without judgement, and read back to you in patterns you might "
        "otherwise miss.", styles["AuroBody"]
    ))

    story.append(Paragraph("Your account", styles["AuroHeading"]))
    data = [
        ["Name", user_name],
        ["Phone", phone],
        ["Age", str(age) if age else "—"],
        ["Sex", sex or "—"],
        ["Email", email or "—"],
        ["Location", location or "—"],
        ["Registered on", datetime.now().strftime("%d %B %Y")],
    ]
    tbl = Table(data, colWidths=[4.2 * cm, 9.5 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
        ("TEXTCOLOR", (0, 0), (0, -1), MAROON),
        ("TEXTCOLOR", (1, 0), (1, -1), INK),
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, GOLD),
        ("BACKGROUND", (0, 0), (-1, -1), IVORY),
    ]))
    story.append(tbl)

    story.append(Paragraph("What you can do here", styles["AuroHeading"]))
    for line in [
        "Log your mood each day, alongside sleep and exercise — the two quiet pillars that shape most moods.",
        "See patterns surface over weeks and months, in charts drawn in the spirit of old ledger books.",
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


def generate_therapist_report_pdf(user, logs, cbt_entries, charts, stats, out_path):
    """
    user: sqlite3.Row
    logs: list of mood_logs rows
    cbt_entries: list of cbt_entries rows
    charts: dict of base64 png strings {trend, sleep, exercise}
    stats: dict from correlation_stats()
    """
    styles = _styles()
    story = []

    story.append(Paragraph("Auro — Clinical Summary Report", styles["AuroTitle"]))
    story.append(Paragraph("Prepared for review by a mental health professional", styles["AuroSub"]))
    story.append(HRFlowable(width="60%", thickness=1, color=GOLD, spaceAfter=14, hAlign="CENTER"))

    info = [
        ["Client", user["name"]],
        ["Age / Sex", f"{user['age'] or '—'} / {user['sex'] or '—'}"],
        ["Location", user["location"] or "—"],
        ["Report generated", datetime.now().strftime("%d %B %Y, %H:%M")],
        ["Entries covered", f"{len(logs)} daily log(s)"],
    ]
    tbl = Table(info, colWidths=[4.2 * cm, 9.5 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MAROON),
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, -1), IVORY),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, GOLD),
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
            ("FONTSIZE", (0, 0), (-1, -1), 10.5),
            ("TEXTCOLOR", (0, 0), (-1, -1), INK),
            ("GRID", (0, 0), (-1, -1), 0.4, GOLD),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(stbl)
        story.append(Spacer(1, 10))

    if charts.get("trend"):
        story.append(Paragraph("Mood & anxiety trend", styles["AuroHeading"]))
        img_data = base64.b64decode(charts["trend"])
        story.append(Image(io.BytesIO(img_data), width=15.5 * cm, height=7 * cm))

    if charts.get("sleep") or charts.get("exercise"):
        story.append(Paragraph("Correlations", styles["AuroHeading"]))
        if charts.get("sleep"):
            story.append(Image(io.BytesIO(base64.b64decode(charts["sleep"])), width=9.5 * cm, height=7 * cm))
        if charts.get("exercise"):
            story.append(Image(io.BytesIO(base64.b64decode(charts["exercise"])), width=9.5 * cm, height=7 * cm))

    if cbt_entries:
        story.append(Paragraph("Recent CBT thought-records", styles["AuroHeading"]))
        for e in cbt_entries[:8]:
            story.append(Paragraph(f"<b>{e['entry_date']}</b> — {e['exercise_type'].replace('_',' ').title()}", styles["AuroBody"]))
            if e["situation"]:
                story.append(Paragraph(f"Situation: {e['situation']}", styles["AuroBody"]))
            if e["automatic_thought"]:
                story.append(Paragraph(f"Automatic thought: {e['automatic_thought']}", styles["AuroBody"]))
            if e["balanced_thought"]:
                story.append(Paragraph(f"Balanced thought: {e['balanced_thought']}", styles["AuroBody"]))
            if e["mood_before"] is not None and e["mood_after"] is not None:
                story.append(Paragraph(f"Mood shift: {e['mood_before']} &rarr; {e['mood_after']}", styles["AuroBody"]))
            story.append(HRFlowable(width="100%", thickness=0.4, color=GOLD, spaceAfter=8, spaceBefore=4))

    story.append(Paragraph(
        "This report is generated from client-entered self-report data and is intended "
        "to support, not replace, clinical judgement.", styles["AuroBody"]
    ))

    doc = _base_doc(out_path)
    doc.build(story)
    return out_path
