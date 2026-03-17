# McK-Consultancy Improvement Catalog

Display this improvement catalog and help me choose what to implement next.

---

## Quick Wins (< 1 hour each)

- **A** ~~Wire up Stop button~~ ✓ (done)
- **B** ~~"Test API Key" button on Setup~~ ✓ (done)
- **C** ~~Generated-at timestamp on outputs~~ ✓ (done)
- **D** ~~Success toast after batch analysis~~ ✓ (done)
- **E** ~~Keyboard Escape to close modals~~ ✓ (done)
- **F** ~~Fix prompt filename typo (`2_CompetetiveLandscapte.md` → `2_CompetitiveLandscape.md`)~~ ✓ (done)
- **G** ~~Add `.env.example` file~~ ✓ (done)

## Medium Effort

- **H** Structured logging (replace all `print()`) — `backend/claude_client.py`, `backend/main.py`, `backend/export_service.py`
- **I** Fix cost-estimate race condition (no AbortController) — `frontend/src/components/AnalysisTab.tsx` ~line 76
- **J** N+1 query fix on sessions list — `backend/main.py` ~line 231
- **K** Database indexes on `session_id`, `prompt_id`, `created_at` — `backend/database.py`
- **L** Silent SSE parse errors surfaced to user — `frontend/src/hooks/useAnalysis.ts` ~line 60
- **M** Export PDF fallback + error hint — `backend/export_service.py` ~line 282

## Larger Features

- **N** Test suite (pytest backend + Vitest frontend)
- **O** Alembic DB migrations
- **P** Retry + exponential backoff for Claude API calls
- **Q** Analysis comparison view (diff two runs of same framework)
- **R** Prompt quality improvements (thin prompts: TAM, SWOT+P5F)

---

After displaying the catalog, ask which improvement(s) the user wants to tackle next and implement them.
