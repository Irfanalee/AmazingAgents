import os
import uuid
from html import escape
from typing import List
from datetime import datetime

import markdown as md
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from htmldocx import HtmlToDocx

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


def _tables_to_pre(html: str) -> str:
    """Convert HTML tables to ASCII <pre> blocks — xhtml2pdf crashes on tables."""
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
            rows.append(cells)
        if not rows:
            table.decompose()
            continue
        num_cols = max(len(r) for r in rows)
        col_widths = [
            max((len(r[i]) if i < len(r) else 0) for r in rows)
            for i in range(num_cols)
        ]
        lines = []
        for idx, row in enumerate(rows):
            padded = [
                (row[i] if i < len(row) else "").ljust(col_widths[i])
                for i in range(num_cols)
            ]
            lines.append("| " + " | ".join(padded) + " |")
            if idx == 0:
                lines.append("|-" + "-|-".join("-" * w for w in col_widths) + "-|")
        pre = soup.new_tag("pre")
        pre.string = "\n".join(lines)
        table.replace_with(pre)
    return str(soup)


# ── DOCX ─────────────────────────────────────────────────────────────────────

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
    title_run = title_para.add_run("NPI Strategy Suite Report")
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

    parser = HtmlToDocx()

    for analysis in analyses:
        title = analysis.get("title", analysis.get("prompt_id", "Analysis"))
        output = analysis.get("output", "")
        cost = analysis.get("cost_usd", 0)
        from_cache = analysis.get("from_cache", False)

        # Section heading
        heading = doc.add_heading(title, level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in heading.runs:
            run.font.color.rgb = RGBColor(0x0A, 0x23, 0x42)
            run.font.size = Pt(18)

        # Cost meta line
        meta_p = doc.add_paragraph()
        meta_run = meta_p.add_run(
            f"Cost: ${cost:.4f}" + (" (from cache)" if from_cache else "")
        )
        meta_run.font.size = Pt(9)
        meta_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        meta_run.italic = True

        # Convert markdown → HTML → docx (handles tables, lists, bold, etc.)
        if output:
            content_html = md.markdown(
                output,
                extensions=["tables", "fenced_code"],
            )
            parser.add_html_to_document(content_html, doc)

        doc.add_page_break()

    filename = f"pls_report_{uuid.uuid4().hex[:8]}.docx"
    filepath = os.path.join(EXPORTS_DIR, filename)
    doc.save(filepath)
    return filepath


# ── PDF ───────────────────────────────────────────────────────────────────────

_PDF_CSS = """
@page {
    margin: 2.5cm 2cm;
    size: A4;
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
    table-layout: fixed;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
    word-wrap: break-word;
}
th {
    background: #0A2342;
    color: white;
    padding: 5px 4px;
    text-align: left;
    font-weight: bold;
}
td {
    border: 1px solid #ddd;
    padding: 4px 4px;
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
    font-size: 10px;
    font-family: monospace;
}
pre {
    background: #f0f0f0;
    padding: 12px;
    font-size: 10px;
}
strong { color: #0A2342; }
"""


def generate_pdf(session_name: str, analyses: List[dict]) -> str:
    from xhtml2pdf import pisa

    html_parts = [
        f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{_PDF_CSS}</style>
</head><body>
<div class="cover">
  <h1>NPI Suite Report</h1>
  <div class="divider"></div>
  <div class="subtitle">{escape(session_name)}</div>
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
            extensions=["tables", "fenced_code"],
        )
        content_html = _tables_to_pre(content_html)
        meta = f"Cost: ${cost:.4f}" + (" &mdash; served from cache" if from_cache else "")

        html_parts.append(
            f"""<div class="chapter">
  <div class="chapter-title">{escape(title)}</div>
  <div class="chapter-meta">{meta}</div>
  {content_html}
</div>
"""
        )

    html_parts.append("</body></html>")
    full_html = "\n".join(html_parts)

    filename = f"pls_report_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(EXPORTS_DIR, filename)
    with open(filepath, "wb") as f:
        result = pisa.CreatePDF(full_html.encode("utf-8"), dest=f, encoding="utf-8")

    if result.err:
        raise RuntimeError(f"PDF generation failed with {result.err} error(s)")

    return filepath
