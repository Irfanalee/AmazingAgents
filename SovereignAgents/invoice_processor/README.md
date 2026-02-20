# Invoice Processor

Automated invoice/receipt processing pipeline powered by the `doc-intel` model via Ollama.

## Features

- Upload PDF, PNG, or JPG invoices
- OCR extraction (PyMuPDF for PDFs, pytesseract for images)
- Structured data extraction via local `doc-intel` model
- SQLite database storage with line items
- FastAPI REST API
- Gradio web interface

## Prerequisites

1. **Ollama** running with the `doc-intel` model:
   ```bash
   ollama serve
   ollama run doc-intel "test"
   ```

2. **Tesseract OCR** system package (for image files):
   ```bash
   # Ubuntu/Debian
   sudo apt install tesseract-ocr

   # macOS
   brew install tesseract
   ```

3. **Python 3.12+**

## Setup

```bash
# Clone / navigate to this directory
cd SovereignAgents/invoice_processor

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env if needed (Ollama URL, model name, etc.)
```

## Run

```bash
python main.py
```

The server starts on port 8000:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Health check |
| `http://localhost:8000/docs` | Interactive API docs (Swagger UI) |
| `http://localhost:8000/ui` | Gradio web interface |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload` | Upload and process an invoice file |
| `GET` | `/invoices` | List all processed invoices |
| `GET` | `/invoices/{id}` | Get a specific invoice |
| `GET` | `/reports/daily` | Daily summary report (optional `?date=YYYY-MM-DD`) |

### Example: Upload via curl

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/invoice.pdf"
```

## Database Schema

SQLite database (`invoices.db`) with two tables:

- **invoices** — one row per processed invoice
- **line_items** — one row per line item, linked to invoices

## Project Structure

```
invoice_processor/
├── main.py          # Entry point (FastAPI + Gradio)
├── api.py           # REST endpoints
├── ui.py            # Gradio web interface
├── analyzer.py      # Ollama integration
├── ocr.py           # Text extraction (PDF + images)
├── database.py      # SQLite CRUD
├── models.py        # Pydantic models
├── config.py        # Configuration
├── requirements.txt
├── .env.example
└── uploads/         # Temp storage for uploaded files
```
