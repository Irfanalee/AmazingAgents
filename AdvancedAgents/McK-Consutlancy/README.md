# McKinsey Research Suite

An AI-powered consulting toolkit that runs 12 McKinsey-grade strategic frameworks against your business — powered by Claude and built with a FastAPI backend + React frontend.

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

## Quick Start

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

### 2. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env if you want server-side defaults
```

The API key can also be entered directly in the UI — it is stored in `localStorage` only and never sent to any server except Anthropic's API.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node dependencies

```bash
cd frontend && npm install && cd ..
```

### 5. Create required directories

```bash
mkdir -p data exports
```

### 6. Start the backend

```bash
uvicorn backend.main:app --reload
```

API available at **http://localhost:8000** · Interactive docs at http://localhost:8000/docs

### 7. Start the frontend

```bash
cd frontend && npm run dev
```

App available at **http://localhost:5173**

---

## First Run

1. Open **http://localhost:5173**
2. Enter your Anthropic API key — use the **Test** button to validate it before proceeding
3. Fill in your **Business Context** (Business Name, Industry, Stage, etc.) — auto-populates all 12 analysis prompts
4. Choose a UI theme (McKinsey Dark / Premium White / Data Dashboard)
5. Click **Launch Research Suite**
6. Select any framework from the sidebar and click **Generate Analysis**
7. Use **⚡ Pre-fill All** in the top bar to run all 12 frameworks in batch using Haiku (fast + cheap)

---

## The 12 Analysis Frameworks

| # | Framework | What you get |
|---|---|---|
| 0 | Executive Strategy Master | Full strategic overview — vision, positioning, priorities |
| 1 | TAM / SAM / SOM Analysis | Top-down + bottom-up market sizing with CAGR scenarios |
| 2 | Competitive Landscape | Competitor matrix, positioning map, differentiation strategy |
| 3 | Customer Personas | 3–5 detailed ICPs with jobs-to-be-done and buying triggers |
| 4 | Industry Trend Analysis | Macro forces, disruption signals, 3-year outlook |
| 5 | SWOT + Porter's Five Forces | Cross-analysis matrix + industry attractiveness score + strategic imperatives |
| 6 | Pricing Strategy Analysis | Pricing model options, elasticity, competitive benchmarks |
| 7 | Go-to-Market Strategy | Channel mix, messaging, launch sequencing |
| 8 | Customer Journey Mapping | Touchpoint analysis, friction points, conversion optimisation |
| 9 | Financial Model & Unit Economics | Revenue projections, CAC/LTV, break-even analysis |
| 10 | Risk Assessment & Scenario Planning | Risk register, likelihood/impact matrix, mitigation playbook |
| 11 | Market Entry & Expansion | Entry strategy, localisation requirements, partnership options |

---

## Features

| Feature | Details |
|---|---|
| **Real-time streaming** | Results stream token-by-token via SSE with a live stop button |
| **API key validation** | Test button on Setup page — instant green/red feedback before you run anything |
| **Response caching** | Identical requests return instantly with a "⚡ Cached" badge; 7-day TTL |
| **Cost estimates** | Pre-generation cost estimate shown per framework; race-condition safe |
| **Batch pre-fill** | Run all 12 frameworks in one click (Haiku model); success toast auto-clears |
| **AI feedback & refinement** | Ask follow-up questions on any output — streamed inline |
| **Session history** | Save, resume, rename, and delete research sessions |
| **Export** | Download selected analyses as a formatted Word (`.docx`) or PDF report |
| **Generated-at timestamp** | Each output shows the time it was generated in the metadata bar |
| **3 UI themes** | McKinsey Dark, Premium White, Data Dashboard — switchable without losing state |
| **Keyboard shortcuts** | Escape closes modals |

---

## Project Structure

```
McK-Consutlancy/
├── backend/
│   ├── main.py              # FastAPI app + 11 API routes
│   ├── claude_client.py     # Anthropic streaming client + 7-day SHA-256 cache
│   ├── database.py          # SQLAlchemy models: Session, Analysis, Cache, FeedbackMessage
│   ├── models.py            # Pydantic schemas + per-model cost estimation
│   ├── prompt_manager.py    # Loads/fills prompts from /prompts/*.md
│   └── export_service.py    # DOCX + PDF generation
├── frontend/
│   └── src/
│       ├── types.ts         # Shared TypeScript interfaces
│       ├── App.tsx          # Root component + AppContext provider
│       ├── hooks/
│       │   ├── useAnalysis.ts   # SSE streaming state + AbortController
│       │   └── useSession.ts    # Session loading + analysis map
│       ├── lib/
│       │   ├── api.ts       # Axios + fetch wrappers for all endpoints
│       │   └── utils.ts     # formatCost, formatTokens, downloadBlob
│       ├── components/
│       │   ├── AnalysisTab.tsx   # Per-framework tab: generate, stream, feedback
│       │   ├── OutputRenderer.tsx
│       │   ├── FeedbackPanel.tsx
│       │   ├── ExportModal.tsx   # Escape-to-close, format + selection picker
│       │   ├── Sidebar.tsx
│       │   ├── CostTracker.tsx
│       │   └── ThemeToggle.tsx
│       └── pages/
│           ├── Setup.tsx        # API key (with Test button) + business context
│           ├── Research.tsx     # Main workspace
│           └── History.tsx      # Session library
├── prompts/                 # 12 Markdown prompt templates
├── data/                    # SQLite database (auto-created)
├── exports/                 # Generated reports (auto-created)
├── .env.example             # Environment variable reference
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
| `POST` | `/api/analyze/batch` | Run multiple frameworks at once |
| `POST` | `/api/analyze/estimate` | Pre-generation cost estimate |
| `GET` | `/api/sessions` | List sessions |
| `POST` | `/api/sessions` | Create session |
| `GET` | `/api/sessions/{id}` | Session + all analyses |
| `PUT` | `/api/sessions/{id}` | Update session name / context |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `GET` | `/api/analyses/{id}/feedback` | Feedback message history |
| `POST` | `/api/analyses/{id}/feedback/stream` | SSE feedback refinement |
| `POST` | `/api/export` | Generate DOCX or PDF report |
| `GET` | `/api/cache/stats` | Cache hit rate + savings |
| `DELETE` | `/api/cache` | Clear all cached responses |

---

## Environment Variables

See `.env.example` for the full reference. All variables are optional — the API key can be entered in the UI instead.

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Server-side API key override |
| `DATABASE_URL` | `sqlite:///./data/mck.db` | SQLite database path |
| `EXPORTS_DIR` | `exports` | Output directory for generated reports |
| `HOST` | `0.0.0.0` | FastAPI bind host |
| `PORT` | `8000` | FastAPI bind port |
