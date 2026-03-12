# McKinsey Research Suite

An AI-powered consulting toolkit that runs 12 McKinsey-grade market research frameworks against your business — powered by Claude and built with a FastAPI backend + React frontend.

---

![Anthropic Claude](https://img.shields.io/badge/Claude-AI-black?style=for-the-badge&logo=anthropic&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **AI** | Anthropic Claude API (Sonnet 4.6 / Opus 4.6 / Haiku 4.5) |
| **Backend** | Python 3.9+ · FastAPI · Uvicorn · SQLAlchemy · SQLite |
| **Frontend** | React 18 · TypeScript · Vite · Tailwind CSS |
| **Streaming** | Server-Sent Events (SSE) via FastAPI + `fetch` ReadableStream |
| **Export** | `python-docx` (Word) · WeasyPrint (PDF) |
| **Caching** | SQLite — SHA-256 keyed, 7-day TTL |

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com) (starts with `sk-ant-`)

---

## Quick Start (automated)

```bash
bash setup.sh
```

This installs all Python and Node dependencies and creates the `data/` and `exports/` directories.

Then start both servers:

```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Manual Setup

### 1. Clone / enter the project

```bash
cd McK-Consutlancy
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

> On some systems use `pip3` instead of `pip`.

### 3. Install Node dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Create required directories

```bash
mkdir -p data exports
```

### 5. Start the backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at **http://localhost:8000**. You can explore the auto-generated docs at http://localhost:8000/docs.

### 6. Start the frontend

```bash
cd frontend
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## First Run

1. Open **http://localhost:5173**
2. Enter your Anthropic API key on the Setup page — stored locally only, never sent to any server except Anthropic's API
3. Fill in your **Business Context** (Business Name, Industry, Stage, etc.) — this auto-populates all 12 analysis prompts
4. Choose a UI theme (McKinsey Dark / Premium White / Data Dashboard)
5. Click **Launch Research Suite**
6. Select any of the 12 frameworks from the sidebar and click **Generate Analysis**

---

## The 12 Analysis Frameworks

| # | Framework |
|---|---|
| 0 | Executive Strategy Master |
| 1 | TAM / SAM / SOM Analysis |
| 2 | Competitive Landscape |
| 3 | Customer Personas |
| 4 | Industry Trend Analysis |
| 5 | SWOT + Porter's Five Forces |
| 6 | Pricing Strategy Analysis |
| 7 | Go-to-Market Strategy |
| 8 | Customer Journey Mapping |
| 9 | Financial Model & Unit Economics |
| 10 | Risk Assessment & Scenario Planning |
| 11 | Market Entry & Expansion |

---

## Features

- **Streaming output** — results stream in real time via SSE
- **Response caching** — identical requests return instantly with a "Cached" badge and cost savings estimate
- **Session history** — save, resume, and manage research sessions
- **Export** — download completed analyses as a formatted Word (`.docx`) or PDF report
- **3 UI themes** — switchable at any time without losing state

---

## Project Structure

```
McK-Consutlancy/
├── backend/
│   ├── main.py              # FastAPI app + API routes
│   ├── claude_client.py     # Anthropic streaming client
│   ├── database.py          # SQLAlchemy models + SQLite setup
│   ├── models.py            # Pydantic request/response schemas
│   ├── prompt_manager.py    # Loads prompts from /prompts/*.md
│   └── export_service.py    # DOCX + PDF generation
├── frontend/
│   ├── src/
│   │   ├── types.ts         # Shared TypeScript interfaces
│   │   ├── App.tsx          # Root + AppContext provider
│   │   ├── hooks/           # useAnalysis, useSession
│   │   ├── lib/             # api.ts, utils.ts
│   │   ├── components/      # Sidebar, AnalysisTab, OutputRenderer, …
│   │   └── pages/           # Setup, Research, History
│   ├── tsconfig.json
│   └── vite.config.ts
├── prompts/                 # 12 Markdown prompt templates
├── data/                    # SQLite database (auto-created)
├── exports/                 # Generated reports (auto-created)
├── requirements.txt
├── setup.sh
└── .gitignore
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/prompts` | List all 12 prompts |
| `GET` | `/api/prompts/{id}` | Single prompt detail |
| `POST` | `/api/analyze/stream` | SSE streaming analysis |
| `GET` | `/api/sessions` | List sessions |
| `POST` | `/api/sessions` | Create session |
| `GET` | `/api/sessions/{id}` | Session + analyses |
| `PUT` | `/api/sessions/{id}` | Update session |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `POST` | `/api/export` | Generate PDF or DOCX |
| `GET` | `/api/cache/stats` | Cache hit stats |
| `DELETE` | `/api/cache` | Clear cache |
