from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    amount: float = 0.0


class InvoiceExtracted(BaseModel):
    vendor: str = ""
    invoice_date: Optional[str] = None
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    currency: str = "USD"
    line_items: List[LineItem] = Field(default_factory=list)


class InvoiceRecord(BaseModel):
    id: int
    file_name: str
    vendor: str = ""
    invoice_date: Optional[str] = None
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    currency: str = "USD"
    raw_text: str = ""
    extracted_json: Optional[str] = None
    processed_at: Optional[str] = None
    status: str = "processed"
    line_items: List[LineItem] = Field(default_factory=list)


class DailyReport(BaseModel):
    report_date: str
    total_invoices: int
    total_amount: float
    total_tax: float
    vendors: List[str]
    invoices: List[InvoiceRecord] = Field(default_factory=list)
