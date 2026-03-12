import os
import uuid
import re
from typing import List
from datetime import datetime

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


# ── DOCX helpers ─────────────────────────────────────────────────────────────

def _set_heading_color(run, hex_color: str):
    r = run._r
    rPr = r.get_or_add_rPr()
    color_elem = OxmlElement("w:color")
    color_elem.set(qn("w:val"), hex_color)
    rPr.append(color_elem)


def _add_styled_heading(doc, text: str, level: int):
    heading = doc.add_heading(text, level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in heading.runs:
        if level == 1:
            run.font.color.rgb = RGBColor(0x0A, 0x23, 0x42)
            run.font.size = Pt(18)
        elif level == 2:
            run.font.color.rgb = RGBColor(0x0A, 0x23, 0x42)
            run.font.size = Pt(14)
        else:
            run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            run.font.size = Pt(12)
    return heading


def generate_docx(session_name: str, analyses: List[dict]) -> str:
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.2)

    # Cover page
    doc.add_paragraph()
    doc.add_paragraph()
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run("McKinsey Market Research Report")
    title_run.bold = True
    title_run.font.size = Pt(28)
    title_run.font.color.rgb = RGBColor(0x0A, 0x23, 0x42)

    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_para.add_run(session_name)
    sub_run.font.size = Pt(16)
    sub_run.font.color.rgb = RGBColor(0xC9, 0xA8, 0x4C)

    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(
        f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}"
    ).font.size = Pt(11)

    doc.add_page_break()

    for analysis in analyses:
        title = analysis.get("title", analysis.get("prompt_id", "Analysis"))
        output = analysis.get("output", "")
        cost = analysis.get("cost_usd", 0)
        from_cache = analysis.get("from_cache", False)

        _add_styled_heading(doc, title, level=1)

        # Cost meta line
        meta_p = doc.add_paragraph()
        meta_run = meta_p.add_run(
            f"Cost: ${cost:.4f}" + (" (from cache)" if from_cache else "")
        )
        meta_run.font.size = Pt(9)
        meta_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        meta_run.italic = True

        if output:
            for line in output.split("\n"):
                stripped = line.strip()
                if not stripped:
                    doc.add_paragraph()
                    continue
                if stripped.startswith("### "):
                    _add_styled_heading(doc, stripped[4:], level=3)
                elif stripped.startswith("## "):
                    _add_styled_heading(doc, stripped[3:], level=2)
                elif stripped.startswith("# "):
                    _add_styled_heading(doc, stripped[2:], level=2)
                elif stripped.startswith(("• ", "- ", "* ")):
                    bullet = doc.add_paragraph(stripped[2:], style="List Bullet")
                    bullet.runs[0].font.size = Pt(11)
                elif re.match(r"^\d+\.\s", stripped):
                    num_text = re.sub(r"^\d+\.\s", "", stripped)
                    np = doc.add_paragraph(num_text, style="List Number")
                    np.runs[0].font.size = Pt(11)
                else:
                    # Handle inline bold/italic
                    p = doc.add_paragraph()
                    parts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", stripped)
                    for part in parts:
                        if part.startswith("**") and part.endswith("**"):
                            r = p.add_run(part[2:-2])
                            r.bold = True
                            r.font.size = Pt(11)
                        elif part.startswith("*") and part.endswith("*"):
                            r = p.add_run(part[1:-1])
                            r.italic = True
                            r.font.size = Pt(11)
                        else:
                            r = p.add_run(part)
                            r.font.size = Pt(11)

        doc.add_page_break()

    filename = f"mck_report_{uuid.uuid4().hex[:8]}.docx"
    filepath = os.path.join(EXPORTS_DIR, filename)
    doc.save(filepath)
    return filepath


# ── PDF helpers ───────────────────────────────────────────────────────────────

def generate_pdf(session_name: str, analyses: List[dict]) -> str:
    import markdown as md
    from weasyprint import HTML, CSS

    css_string = """
    @page {
        margin: 2.5cm 2cm;
        size: A4;
        @bottom-right {
            content: counter(page);
            font-size: 10px;
            color: #888;
        }
    }
    body {
        font-family: Arial, Helvetica, sans-serif;
        color: #1a1a2e;
        line-height: 1.65;
        font-size: 11pt;
    }
    .cover {
        text-align: center;
        padding-top: 180px;
        page-break-after: always;
    }
    .cover h1 {
        font-size: 30px;
        color: #0A2342;
        margin-bottom: 14px;
        letter-spacing: -0.5px;
    }
    .cover .subtitle {
        font-size: 18px;
        color: #C9A84C;
        margin-bottom: 10px;
    }
    .cover .date {
        font-size: 12px;
        color: #777;
        margin-top: 18px;
    }
    .cover .divider {
        width: 80px;
        height: 3px;
        background: #C9A84C;
        margin: 20px auto;
    }
    .chapter {
        page-break-before: always;
    }
    .chapter-title {
        font-size: 22px;
        color: #0A2342;
        font-weight: bold;
        border-bottom: 3px solid #C9A84C;
        padding-bottom: 8px;
        margin-bottom: 6px;
    }
    .chapter-meta {
        color: #999;
        font-size: 9pt;
        margin-bottom: 18px;
        font-style: italic;
    }
    h2 { font-size: 16px; color: #0A2342; margin-top: 22px; margin-bottom: 6px; }
    h3 { font-size: 13px; color: #2d3748; margin-top: 16px; margin-bottom: 4px; }
    p { margin: 7px 0; }
    ul { margin: 8px 0 8px 22px; }
    ol { margin: 8px 0 8px 22px; }
    li { margin: 3px 0; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        font-size: 10pt;
    }
    th {
        background: #0A2342;
        color: white;
        padding: 7px 10px;
        text-align: left;
        font-weight: bold;
    }
    td {
        border: 1px solid #ddd;
        padding: 6px 10px;
    }
    tr:nth-child(even) td { background: #f7f7f7; }
    blockquote {
        border-left: 4px solid #C9A84C;
        margin: 14px 0;
        padding: 8px 16px;
        background: #fdf8ee;
        color: #444;
    }
    code {
        background: #f0f0f0;
        padding: 1px 5px;
        border-radius: 3px;
        font-size: 10px;
        font-family: monospace;
    }
    pre {
        background: #f0f0f0;
        padding: 12px;
        border-radius: 4px;
        overflow: auto;
        font-size: 10px;
    }
    strong { color: #0A2342; }
    """

    html_parts = [
        f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>McKinsey Report</title></head><body>
<div class="cover">
  <h1>McKinsey Market Research Report</h1>
  <div class="divider"></div>
  <div class="subtitle">{session_name}</div>
  <div class="date">Generated: {datetime.utcnow().strftime('%B %d, %Y')}</div>
</div>
"""
    ]

    for analysis in analyses:
        title = analysis.get("title", analysis.get("prompt_id", "Analysis"))
        output = analysis.get("output", "")
        cost = analysis.get("cost_usd", 0)
        from_cache = analysis.get("from_cache", False)

        content_html = md.markdown(
            output,
            extensions=["tables", "fenced_code", "nl2br"],
        )
        meta = f"Cost: ${cost:.4f}" + (" &mdash; served from cache" if from_cache else "")

        html_parts.append(
            f"""<div class="chapter">
  <div class="chapter-title">{title}</div>
  <div class="chapter-meta">{meta}</div>
  {content_html}
</div>
"""
        )

    html_parts.append("</body></html>")
    full_html = "\n".join(html_parts)

    filename = f"mck_report_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(EXPORTS_DIR, filename)
    HTML(string=full_html).write_pdf(filepath, stylesheets=[CSS(string=css_string)])
    return filepath
