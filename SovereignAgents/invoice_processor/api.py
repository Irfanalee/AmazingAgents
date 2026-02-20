import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from analyzer import extract_invoice_data
from config import ALLOWED_EXTENSIONS, UPLOAD_DIR
from database import daily_report, get_invoice, list_invoices, save_invoice
from models import DailyReport, InvoiceRecord
from ocr import extract_text

router = APIRouter()


@router.post("/upload", response_model=InvoiceRecord, summary="Upload and process an invoice")
async def upload_invoice(file: UploadFile = File(...)) -> InvoiceRecord:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    dest_path = UPLOAD_DIR / file.filename
    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        raw_text = extract_text(str(dest_path))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"OCR extraction failed: {e}")

    extracted = extract_invoice_data(raw_text)
    invoice_id = save_invoice(file.filename, raw_text, extracted)

    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve saved invoice")
    return record


@router.get("/invoices", response_model=List[InvoiceRecord], summary="List all processed invoices")
async def get_invoices() -> List[InvoiceRecord]:
    return list_invoices()


@router.get("/invoices/{invoice_id}", response_model=InvoiceRecord, summary="Get a specific invoice")
async def get_invoice_by_id(invoice_id: int) -> InvoiceRecord:
    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    return record


@router.get("/reports/daily", response_model=DailyReport, summary="Daily invoice summary report")
async def get_daily_report(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (defaults to today)")
) -> DailyReport:
    return daily_report(date)
