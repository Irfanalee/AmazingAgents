import json
import re
from typing import Any, Dict

import requests

from config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL
from models import InvoiceExtracted, LineItem

INVOICE_SYSTEM_PROMPT = (
    "You are an expert invoice analyst. Extract structured data from the invoice text "
    "and return ONLY valid JSON in this exact format:\n"
    '{"vendor": "", "date": "", "items": [{"description": "", "quantity": 1, "unit_price": 0, "amount": 0}], '
    '"subtotal": 0, "tax": 0, "total": 0, "currency": "USD"}\n'
    "Do not include any explanation or text outside the JSON."
)


def query_ollama(prompt: str, system: str = "") -> str:
    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
    response.raise_for_status()
    return response.json().get("response", "")


def _parse_json_from_response(text: str) -> Dict[str, Any]:
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block from markdown code fences or surrounding text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {}


def extract_invoice_data(raw_text: str) -> InvoiceExtracted:
    if not raw_text.strip():
        return InvoiceExtracted()

    prompt = f"Extract the invoice data from the following text:\n\n{raw_text}"

    try:
        response_text = query_ollama(prompt, system=INVOICE_SYSTEM_PROMPT)
        data = _parse_json_from_response(response_text)
    except Exception:
        return InvoiceExtracted()

    if not data:
        return InvoiceExtracted()

    line_items = []
    for item in data.get("items", []):
        line_items.append(
            LineItem(
                description=str(item.get("description", "")),
                quantity=float(item.get("quantity", 1)),
                unit_price=float(item.get("unit_price", 0)),
                amount=float(item.get("amount", 0)),
            )
        )

    return InvoiceExtracted(
        vendor=str(data.get("vendor", "")),
        invoice_date=str(data.get("date", "")) or None,
        subtotal=float(data.get("subtotal", 0)),
        tax=float(data.get("tax", 0)),
        total=float(data.get("total", 0)),
        currency=str(data.get("currency", "USD")),
        line_items=line_items,
    )
