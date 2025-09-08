from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
import html

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
    Preformatted,
)

# ---------------------------
# Helper Functions
# ---------------------------

def _severity_color(sev: str) -> colors.Color:
    s = (sev or "").strip().lower()
    if s.startswith("crit"):
        return colors.Color(0.75, 0.0, 0.0)
    if s.startswith("high"):
        return colors.red
    if s.startswith("med"):
        return colors.orange
    if s.startswith("low"):
        return colors.green
    return colors.grey

def _section_heading(text: str) -> Paragraph:
    style = ParagraphStyle(
        "H2",
        parent=getSampleStyleSheet()["Heading2"],
        textColor=colors.HexColor("#0f1726"),
        fontSize=14,
        spaceAfter=6,
    )
    return Paragraph(text, style)

def _body(text: str) -> Paragraph:
    style = ParagraphStyle(
        "Body",
        parent=getSampleStyleSheet()["BodyText"],
        textColor=colors.black,  # Black text for readability
        fontSize=10.5,
        leading=14,
    )
    if not isinstance(text, str):
        text = str(text)
    safe_text = html.escape(text)
    return Paragraph(safe_text, style)

def _code(text: str) -> Preformatted:
    style = ParagraphStyle(
        "Code",
        parent=getSampleStyleSheet()["Code"],
        textColor=colors.black,  # Black code text
        backColor=colors.whitesmoke,  # Optional light background
        fontName="Courier",
        fontSize=9.5,
        leading=12,
    )
    if not isinstance(text, str):
        text = str(text)
    return Preformatted(text, style)

def _ports_table(nmap_items: List[Dict[str, Any]]) -> Table:
    headers = ["IP", "Port", "State", "Service"]
    data = [headers]
    for item in nmap_items:
        data.append([
            str(item.get("ip", "")),
            str(item.get("port", "")),
            str(item.get("state", "")),
            str(item.get("service", "")),
        ])

    tbl = Table(data, colWidths=[45 * mm, 25 * mm, 25 * mm, 65 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    return tbl

def _ai_section(title: str, ai_text: str):
    return KeepTogether([
        Spacer(1, 2 * mm),
        _section_heading(f"🤖 AI Analysis of {title}"),
        HRFlowable(width="100%", thickness=1, color=colors.black),  # Black line separator
        Spacer(1, 2 * mm),
        _body(ai_text if ai_text else "AI analysis unavailable."),  # Black readable text
    ])

# ---------------------------
# Main Report Builder
# ---------------------------

def generate_report(
        scan_results: Dict[str, Any],
        ai_reports: Dict[str, str],
        *,
        target: Optional[str] = None,
        filename: str = "security_report.pdf",
) -> str:
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="GenAI Ethical Hacking Report",
        author="GenAI PenTest Toolkit",
    )

    elems: List[Any] = []

    # Title Page
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    title_style = ParagraphStyle("Title", fontSize=22, textColor=colors.HexColor("#0f1726"))
    subtitle_style = ParagraphStyle("Subtitle", fontSize=11, textColor=colors.HexColor("#475569"))

    elems.append(Paragraph("GenAI Ethical Hacking Report", title_style))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(f"Target: {target or 'N/A'}", subtitle_style))
    elems.append(Paragraph(f"Generated: {ts}", subtitle_style))
    elems.append(PageBreak())

    # --- Tool Sections (Detailed) ---
    for tool, display_name in [
        ("nmap", "🔍 Nmap Results"),
        ("theHarvester", "🌍 theHarvester Results"),
        ("sublist3r", "🕸️ Sublist3r Results"),
        ("sql_injection", "💉 SQL Injection Results"),
        ("subdomain_enum", "🌐 Subdomain Enumeration Results")
    ]:
        elems.append(_section_heading(display_name))
        data = scan_results.get(tool, {})
        if tool == "nmap" and isinstance(data, list):
            elems.append(_ports_table(data))
        elif tool in ["sublist3r", "subdomain_enum"] and isinstance(data, dict) and data.get("output") or data.get("subdomains"):
            key_list = data.get("output") or data.get("subdomains")
            for l in key_list:
                elems.append(_body(f"- {l}"))
        else:
            elems.append(_code(str(data)))
        elems.append(_ai_section(display_name, ai_reports.get(tool, "")))
        elems.append(PageBreak())

    # --- Final Overall AI Summary ---
    elems.append(_section_heading("📊 Final Overall AI Assessment"))
    elems.append(_ai_section("Overall Findings", ai_reports.get("overall", "")))
    elems.append(PageBreak())

    # --- Consolidated Tool Results + AI Analyses ---
    elems.append(_section_heading("📚 Consolidated Tool Results"))
    for tool, result in scan_results.items():
        elems.append(_section_heading(f"🔧 {tool.capitalize()} Results"))

        # Raw result
        if isinstance(result, (dict, list)):
            elems.append(_code(str(result)))
        else:
            elems.append(_body(str(result)))

        # AI analysis
        ai_text = ai_reports.get(tool, "")
        elems.append(_ai_section(tool.capitalize(), ai_text))
        elems.append(Spacer(1, 6))

    doc.build(elems)
    return filename

# ---------------------------
# Severity Inference
# ---------------------------

def _infer_severity(ai_report: Optional[str]) -> str:
    if not ai_report:
        return "Medium"
    txt = ai_report.lower()
    if "critical" in txt:
        return "Critical"
    if "high" in txt:
        return "High"
    if "medium" in txt:
        return "Medium"
    if "low" in txt:
        return "Low"
    return "Medium"
