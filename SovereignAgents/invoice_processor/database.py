import json
import sqlite3
from datetime import date, datetime
from typing import List, Optional

from config import DB_PATH
from models import DailyReport, InvoiceExtracted, InvoiceRecord, LineItem


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                vendor TEXT,
                invoice_date DATE,
                subtotal REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                total REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                raw_text TEXT,
                extracted_json JSON,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'processed'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS line_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
                description TEXT,
                quantity REAL DEFAULT 1,
                unit_price REAL DEFAULT 0,
                amount REAL DEFAULT 0
            )
        """)
    conn.close()


def save_invoice(file_name: str, raw_text: str, extracted: InvoiceExtracted) -> int:
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO invoices
                (file_name, vendor, invoice_date, subtotal, tax, total, currency,
                 raw_text, extracted_json, processed_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_name,
                extracted.vendor,
                extracted.invoice_date,
                extracted.subtotal,
                extracted.tax,
                extracted.total,
                extracted.currency,
                raw_text,
                extracted.model_dump_json(),
                datetime.utcnow().isoformat(),
                "processed",
            ),
        )
        invoice_id = cursor.lastrowid
        for item in extracted.line_items:
            conn.execute(
                """
                INSERT INTO line_items (invoice_id, description, quantity, unit_price, amount)
                VALUES (?, ?, ?, ?, ?)
                """,
                (invoice_id, item.description, item.quantity, item.unit_price, item.amount),
            )
    conn.close()
    return invoice_id


def _row_to_record(row: sqlite3.Row, line_items: List[LineItem]) -> InvoiceRecord:
    return InvoiceRecord(
        id=row["id"],
        file_name=row["file_name"],
        vendor=row["vendor"] or "",
        invoice_date=row["invoice_date"],
        subtotal=row["subtotal"] or 0.0,
        tax=row["tax"] or 0.0,
        total=row["total"] or 0.0,
        currency=row["currency"] or "USD",
        raw_text=row["raw_text"] or "",
        extracted_json=row["extracted_json"],
        processed_at=row["processed_at"],
        status=row["status"] or "processed",
        line_items=line_items,
    )


def _fetch_line_items(conn: sqlite3.Connection, invoice_id: int) -> List[LineItem]:
    rows = conn.execute(
        "SELECT * FROM line_items WHERE invoice_id = ?", (invoice_id,)
    ).fetchall()
    return [
        LineItem(
            description=r["description"] or "",
            quantity=r["quantity"] or 1.0,
            unit_price=r["unit_price"] or 0.0,
            amount=r["amount"] or 0.0,
        )
        for r in rows
    ]


def get_invoice(invoice_id: int) -> Optional[InvoiceRecord]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if row is None:
        conn.close()
        return None
    items = _fetch_line_items(conn, invoice_id)
    conn.close()
    return _row_to_record(row, items)


def list_invoices() -> List[InvoiceRecord]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM invoices ORDER BY processed_at DESC").fetchall()
    records = []
    for row in rows:
        items = _fetch_line_items(conn, row["id"])
        records.append(_row_to_record(row, items))
    conn.close()
    return records


def daily_report(report_date: Optional[str] = None) -> DailyReport:
    target = report_date or date.today().isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM invoices WHERE DATE(processed_at) = ? ORDER BY processed_at DESC",
        (target,),
    ).fetchall()
    records = []
    for row in rows:
        items = _fetch_line_items(conn, row["id"])
        records.append(_row_to_record(row, items))
    conn.close()

    total_amount = sum(r.total for r in records)
    total_tax = sum(r.tax for r in records)
    vendors = list({r.vendor for r in records if r.vendor})

    return DailyReport(
        report_date=target,
        total_invoices=len(records),
        total_amount=round(total_amount, 2),
        total_tax=round(total_tax, 2),
        vendors=vendors,
        invoices=records,
    )
