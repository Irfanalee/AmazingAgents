import json
from datetime import date
from typing import Any, Dict, List, Tuple

import gradio as gr
import requests

API_BASE = "http://localhost:8000"


# ── helpers ──────────────────────────────────────────────────────────────────

def _post_upload(file_path: str) -> Tuple[str, str]:
    """Upload a file to the API and return (summary_text, raw_json_text)."""
    if file_path is None:
        return "No file selected.", ""
    try:
        with open(file_path, "rb") as f:
            import os
            filename = os.path.basename(file_path)
            response = requests.post(
                f"{API_BASE}/upload",
                files={"file": (filename, f)},
                timeout=150,
            )
        if response.status_code == 200:
            data = response.json()
            summary = _format_invoice_summary(data)
            return summary, json.dumps(data, indent=2)
        else:
            error = response.json().get("detail", response.text)
            return f"Error {response.status_code}: {error}", ""
    except requests.exceptions.ConnectionError:
        return "Could not connect to API. Make sure the server is running.", ""
    except Exception as e:
        return f"Unexpected error: {e}", ""


def _format_invoice_summary(data: Dict[str, Any]) -> str:
    lines = [
        f"Invoice ID : #{data.get('id', '?')}",
        f"File       : {data.get('file_name', '')}",
        f"Vendor     : {data.get('vendor') or 'Unknown'}",
        f"Date       : {data.get('invoice_date') or 'N/A'}",
        f"Currency   : {data.get('currency', 'USD')}",
        f"Subtotal   : {data.get('subtotal', 0):.2f}",
        f"Tax        : {data.get('tax', 0):.2f}",
        f"Total      : {data.get('total', 0):.2f}",
        f"Status     : {data.get('status', '')}",
    ]
    items = data.get("line_items", [])
    if items:
        lines.append("\nLine Items:")
        for item in items:
            lines.append(
                f"  • {item.get('description', '')}  "
                f"qty={item.get('quantity', 1)}  "
                f"@ {item.get('unit_price', 0):.2f}  "
                f"= {item.get('amount', 0):.2f}"
            )
    return "\n".join(lines)


def _fetch_invoices() -> List[List[Any]]:
    try:
        response = requests.get(f"{API_BASE}/invoices", timeout=30)
        if response.status_code == 200:
            records = response.json()
            rows = []
            for r in records:
                rows.append([
                    r.get("id"),
                    r.get("file_name", ""),
                    r.get("vendor") or "Unknown",
                    r.get("invoice_date") or "N/A",
                    f"{r.get('total', 0):.2f}",
                    r.get("currency", "USD"),
                    r.get("status", ""),
                    r.get("processed_at", ""),
                ])
            return rows
        return []
    except Exception:
        return []


def _fetch_report(report_date: str) -> str:
    params = {}
    if report_date:
        params["date"] = report_date
    try:
        response = requests.get(f"{API_BASE}/reports/daily", params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            lines = [
                f"Date           : {data.get('report_date')}",
                f"Total Invoices : {data.get('total_invoices', 0)}",
                f"Total Amount   : {data.get('total_amount', 0):.2f}",
                f"Total Tax      : {data.get('total_tax', 0):.2f}",
                f"Vendors        : {', '.join(data.get('vendors', [])) or 'None'}",
            ]
            invoices = data.get("invoices", [])
            if invoices:
                lines.append("\nInvoices processed today:")
                for inv in invoices:
                    lines.append(
                        f"  #{inv.get('id')} | {inv.get('vendor') or 'Unknown'} | "
                        f"{inv.get('file_name')} | Total: {inv.get('total', 0):.2f}"
                    )
            return "\n".join(lines)
        error = response.json().get("detail", response.text)
        return f"Error {response.status_code}: {error}"
    except requests.exceptions.ConnectionError:
        return "Could not connect to API. Make sure the server is running."
    except Exception as e:
        return f"Unexpected error: {e}"


# ── Gradio UI ─────────────────────────────────────────────────────────────────

def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Invoice Processor", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Invoice Processor\nPowered by `doc-intel` via Ollama")

        with gr.Tab("Upload Invoice"):
            gr.Markdown("Upload a PDF, PNG, or JPG invoice to extract structured data.")
            file_input = gr.File(
                label="Invoice File",
                file_types=[".pdf", ".png", ".jpg", ".jpeg"],
            )
            process_btn = gr.Button("Process Invoice", variant="primary")
            summary_out = gr.Textbox(label="Extracted Summary", lines=15, interactive=False)
            json_out = gr.Code(label="Raw JSON", language="json")

            process_btn.click(
                fn=_post_upload,
                inputs=[file_input],
                outputs=[summary_out, json_out],
            )

        with gr.Tab("View Invoices"):
            gr.Markdown("All invoices processed so far.")
            refresh_btn = gr.Button("Refresh List")
            invoice_table = gr.Dataframe(
                headers=["ID", "File", "Vendor", "Date", "Total", "Currency", "Status", "Processed At"],
                datatype=["number", "str", "str", "str", "str", "str", "str", "str"],
                interactive=False,
            )

            refresh_btn.click(fn=_fetch_invoices, inputs=[], outputs=[invoice_table])
            demo.load(fn=_fetch_invoices, inputs=[], outputs=[invoice_table])

        with gr.Tab("Daily Report"):
            gr.Markdown("Generate a daily invoice summary report.")
            date_input = gr.Textbox(
                label="Date (YYYY-MM-DD, leave blank for today)",
                placeholder=date.today().isoformat(),
            )
            report_btn = gr.Button("Generate Report", variant="primary")
            report_out = gr.Textbox(label="Report", lines=20, interactive=False)

            report_btn.click(fn=_fetch_report, inputs=[date_input], outputs=[report_out])

    return demo


demo = build_ui()
