# McK-Consultancy

AI-powered consulting toolkit that runs 12 McKinsey-grade strategic frameworks against a user's business using Claude AI. Delivers streaming analysis, response caching, session management, and DOCX/PDF export.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.9+, FastAPI, SQLAlchemy, SQLite, Anthropic API |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router |
| Streaming | Server-Sent Events (SSE) backend → `ReadableStream` frontend |
| Export | python-docx, WeasyPrint |

## Key Directories

```
backend/          FastAPI app, Claude client, DB models, prompt engine, export service
frontend/src/     React app — components/, hooks/, pages/, lib/
prompts/          12 Markdown prompt templates with {{placeholder}} syntax
data/             SQLite DB (auto-created: data/mck.db)
exports/          Generated DOCX/PDF reports (auto-created)
```

## Essential Commands

**First-time setup:**
```bash
bash setup.sh          # installs Python + Node deps, creates data/ and exports/
```

**Backend:**
```bash
uvicorn backend.main:app --reload    # dev server on :8000
# API docs: http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm run dev            # dev server on :5173 (proxies /api → :8000)
npm run build          # production build
```

## Key Files

| File | Role |
|------|------|
| `backend/main.py` | FastAPI app, CORS, 11 API routes |
| `backend/claude_client.py` | Anthropic streaming, 7-day SHA-256 cache |
| `backend/database.py` | SQLAlchemy models: Session, Analysis, Cache |
| `backend/models.py` | Pydantic schemas + per-model cost estimation |
| `backend/prompt_manager.py` | Load prompts, extract placeholders, fill templates |
| `backend/export_service.py` | DOCX + PDF generation |
| `frontend/src/App.tsx` | Root component, AppContext provider, routing |
| `frontend/src/types.ts` | TypeScript interfaces (SharedContext, Prompt, Analysis…) |
| `frontend/src/lib/api.ts` | Axios + fetch wrappers for all endpoints |
| `frontend/src/hooks/useAnalysis.ts` | SSE streaming state + AbortController |
| `frontend/src/hooks/useSession.ts` | Session loading + analysis map |

## API Routes

`GET /api/prompts` · `GET /api/prompts/{id}` · `POST /api/analyze/stream` (SSE)
`GET|POST /api/sessions` · `GET|PUT|DELETE /api/sessions/{id}`
`POST /api/export` · `GET /api/cache/stats` · `DELETE /api/cache`

## The 12 Frameworks

Numbered 0–11 in `prompts/`: Executive Strategy, TAM/SAM/SOM, Competitive Landscape, Customer Personas, Industry Trends, SWOT + Porter's Five Forces, Pricing Strategy, Go-to-Market, Customer Journey, Financial Model, Risk Assessment, Market Entry.

## Additional Documentation

Check these files when relevant:

- `.claude/docs/architectural_patterns.md` — SSE streaming pattern, cache strategy, prompt template system, React Context + hook composition, dual validation layer
