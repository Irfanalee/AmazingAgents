# Document Intelligence Agents - Master Prompt for VSCode

## Project Context

I have fine-tuned a Mixture of Experts (MoE) model for document intelligence:

- **Model**: gpt-oss-20b (MoE architecture: 20B total, 2-3B active per token)
- **Training**: QLoRA with Unsloth on RTX A4000 16GB
- **Datasets**: CORD (invoices), CUAD (contracts), DocVQA (general docs)
- **Deployment**: Ollama with model name `doc-intel`
- **Capabilities**: Invoice extraction, contract analysis, document Q&A

## Project Path

```
/repos/LLM-Trainings/moe_docs_image_code/
├── output/
│   ├── lora_adapters/     # Fine-tuned weights
│   └── gguf/              # GGUF export for Ollama
└── data/
    └── datasets/

Agents Repo
/repos/AmazingAgents/
├── SovereignAgents/                # Build agents here
│   ├── invoice_processor/
│   ├── contract_analyzer/
│   ├── document_qa_bot/
│   └── email_processor/

```

## Ollama Setup

The model is deployed locally via Ollama:

```bash
# Model is available as:
ollama run doc-intel

# API endpoint:
curl http://localhost:11434/api/generate -d '{
  "model": "doc-intel",
  "prompt": "Extract data from this invoice...",
  "stream": false
}'
```

## Tech Stack Preferences

- **Language**: Python 3.12
- **API Framework**: FastAPI
- **UI Framework**: Gradio or Streamlit
- **Database**: SQLite (simple) or PostgreSQL (production)
- **OCR**: pytesseract or doctr
- **PDF Processing**: PyMuPDF (fitz)
- **Task Queue**: None for now (keep simple)

---

# AGENTS TO BUILD

Build these agents one by one. Each agent should be self-contained with its own folder, requirements, and README.

---

## Agent 1: Invoice Processor

### Goal
Automated invoice/receipt processing pipeline.

### Features
- Watch folder for new invoices (PDF, PNG, JPG)
- OCR extraction for images
- Send to MoE model via Ollama
- Extract: vendor, date, items, amounts, tax, total
- Save structured data to SQLite database
- Generate daily/weekly reports

### Structure
```
SovereignAgents/invoice_processor/
├── main.py              # Entry point
├── ocr.py               # Text extraction
├── analyzer.py          # Ollama integration
├── database.py          # SQLite operations
├── models.py            # Pydantic models
├── config.py            # Configuration
├── requirements.txt
└── README.md
```

### Key Endpoints (if API)
- `POST /upload` - Upload invoice file
- `GET /invoices` - List all processed invoices
- `GET /invoices/{id}` - Get specific invoice
- `GET /reports/daily` - Daily summary

### Database Schema
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    file_name TEXT,
    vendor TEXT,
    invoice_date DATE,
    subtotal REAL,
    tax REAL,
    total REAL,
    currency TEXT,
    raw_text TEXT,
    extracted_json JSON,
    processed_at TIMESTAMP,
    status TEXT
);

CREATE TABLE line_items (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id),
    description TEXT,
    quantity REAL,
    unit_price REAL,
    amount REAL
);
```

---

## Agent 2: Contract Analyzer API

### Goal
REST API for contract analysis and clause extraction.

### Features
- Upload contract (PDF, DOCX, TXT)
- Extract parties, terms, obligations, key dates
- Identify risky clauses
- Compare two contracts
- Search across processed contracts
- Export analysis as PDF report

### Structure
```
SovereignAgents/contract_analyzer/
├── main.py              # FastAPI app
├── extractor.py         # Text extraction
├── analyzer.py          # Ollama integration
├── comparison.py        # Contract comparison
├── report.py            # PDF report generation
├── database.py          # PostgreSQL/SQLite
├── models.py            # Pydantic models
├── config.py
├── requirements.txt
└── README.md
```

### Key Endpoints
- `POST /contracts/upload` - Upload and analyze
- `GET /contracts/{id}` - Get analysis
- `POST /contracts/compare` - Compare two contracts
- `GET /contracts/search?q=` - Search contracts
- `GET /contracts/{id}/report` - Download PDF report

### Analysis Output
```json
{
  "id": "contract_123",
  "document_type": "Service Agreement",
  "parties": [
    {"name": "TechCorp Inc.", "role": "Client"},
    {"name": "ConsultingPro LLC", "role": "Provider"}
  ],
  "effective_date": "2024-01-01",
  "expiration_date": "2024-12-31",
  "key_terms": [
    "12 month engagement",
    "$15,000 monthly payment"
  ],
  "obligations": {
    "Client": ["Pay monthly fee", "Provide access to systems"],
    "Provider": ["Deliver services", "Maintain confidentiality"]
  },
  "termination": "30 days written notice",
  "risk_flags": [
    "No liability cap specified",
    "Broad indemnification clause"
  ]
}
```

---

## Agent 3: Document Q&A Bot

### Goal
Interactive chatbot for document questions.

### Features
- Upload one or more documents
- Ask natural language questions
- Get answers with source citations
- Conversation history
- Support for follow-up questions
- Gradio web interface

### Structure
```
SovereignAgents/document_qa_bot/
├── app.py               # Gradio interface
├── document_store.py    # Document management
├── qa_engine.py         # Ollama Q&A logic
├── conversation.py      # Chat history
├── config.py
├── requirements.txt
└── README.md
```

### Interface
```
┌─────────────────────────────────────────────────┐
│  📄 Document Q&A Bot                            │
├─────────────────────────────────────────────────┤
│  [Upload Documents]  [Clear All]                │
│                                                 │
│  Loaded: invoice.pdf, contract.pdf              │
├─────────────────────────────────────────────────┤
│  User: What is the total amount on the invoice? │
│                                                 │
│  Bot: The total amount is $13.77, including     │
│       $1.02 tax on a subtotal of $12.75.        │
│       [Source: invoice.pdf, page 1]             │
│                                                 │
│  User: Who are the parties in the contract?     │
│                                                 │
│  Bot: The contract is between TechCorp Inc.     │
│       (Client) and ConsultingPro LLC (Provider).│
│       [Source: contract.pdf, page 1]            │
├─────────────────────────────────────────────────┤
│  [Type your question...]              [Send]    │
└─────────────────────────────────────────────────┘
```

---

## Agent 4: Email Attachment Processor

### Goal
Automatically process email attachments.

### Features
- Connect to email inbox (IMAP)
- Watch for new emails with attachments
- Filter by sender/subject rules
- Process invoices and contracts automatically
- Send summary email back to sender
- Integration with Invoice Processor and Contract Analyzer

### Structure
```
SovereignAgents/email_processor/
├── main.py              # Main loop
├── email_client.py      # IMAP connection
├── rules.py             # Filtering rules
├── processor.py         # Document processing
├── notifier.py          # Send response emails
├── config.py            # IMAP credentials (env vars)
├── requirements.txt
└── README.md
```

### Configuration
```python
EMAIL_CONFIG = {
    "imap_server": "imap.gmail.com",
    "username": "${EMAIL_USER}",  # From env
    "password": "${EMAIL_PASS}",  # App password
    "folder": "INBOX",
    "rules": [
        {
            "name": "invoices",
            "from_contains": ["accounting", "billing"],
            "subject_contains": ["invoice", "receipt"],
            "action": "process_invoice"
        },
        {
            "name": "contracts",
            "from_contains": ["legal", "contracts"],
            "subject_contains": ["agreement", "contract"],
            "action": "process_contract"
        }
    ]
}
```

---

# HOW TO USE THIS PROMPT

## Starting an Agent

Say: "Let's build Agent 1: Invoice Processor"

I will:
1. Create the folder structure
2. Write all the code files
3. Create requirements.txt
4. Write a README with usage instructions
5. Test the integration with Ollama

## Requirements for Each Agent

Before building, ensure:
- Ollama is running: `ollama serve`
- Model is loaded: `ollama run doc-intel "test"`
- Python 3.12+ is available
- Virtual environment is ready

## After Building Each Agent

1. Test locally
2. Document any issues
3. Move to next agent
4. Eventually integrate them together

---

# INTEGRATION ARCHITECTURE (Future)

Once all agents are built:

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Invoice   │  │  Contract   │  │   Doc Q&A   │        │
│  │  Processor  │  │  Analyzer   │  │     Bot     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                  │
│                          ▼                                  │
│                  ┌───────────────┐                         │
│                  │    Ollama     │                         │
│                  │  (doc-intel)  │                         │
│                  └───────────────┘                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    Shared Database                          │
└─────────────────────────────────────────────────────────────┘
```

---

# QUICK REFERENCE

## Ollama API Call

```python
import requests

def query_ollama(prompt: str, system: str = None) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "doc-intel",
            "prompt": prompt,
            "system": system,
            "stream": False
        },
        timeout=120
    )
    return response.json()["response"]
```

## System Prompts

**Invoice:**
```
You are an expert invoice analyst. Extract structured data as JSON:
{"vendor": "", "date": "", "items": [], "subtotal": 0, "tax": 0, "total": 0}
```

**Contract:**
```
You are an expert contract analyst. Extract as JSON:
{"parties": [], "effective_date": "", "terms": [], "obligations": [], "risks": []}
```

**Q&A:**
```
You are a document analyst. Answer questions based only on the provided document.
If the answer is not in the document, say "Not found in document."
```

---

Ready to build! Start with: "Let's build Agent 1: Invoice Processor"