# Architectural Patterns

Patterns that appear across multiple files in this codebase.

---

## 1. SSE Streaming Pipeline

Real-time text delivery from Claude API to the browser via Server-Sent Events.

**Flow:** `backend/claude_client.py` → `backend/main.py` → `frontend/src/lib/api.ts` → `frontend/src/hooks/useAnalysis.ts`

- `claude_client.py`: async generator `stream_analysis()` yields JSON-serialized event dicts (`{type, content}`)
- `main.py` `/api/analyze/stream`: wraps generator in `StreamingResponse(media_type="text/event-stream")`
- `useAnalysis.ts`: opens `fetch()` → `response.body.getReader()`, decodes chunks, accumulates output string
- Event types: `text` (chunk), `cache_hit` (metadata), `done` (final stats), `error`
- AbortController wired to a "Stop" button; backend generator exits on client disconnect

---

## 2. SHA-256 Cache Strategy

Deterministic response caching to avoid redundant Claude API calls.

**Files:** `backend/claude_client.py:generate_cache_key()`, `backend/database.py:Cache model`

- Cache key = `SHA-256(model + prompt_id + sorted(inputs))` — same inputs always hit the same cache entry
- 7-day TTL enforced at query time: `cache.created_at > now - 7d`
- Hit counter incremented on each reuse; used by `/api/cache/stats` to compute cost savings
- Cache stored in SQLite (`data/mck.db`) alongside analyses — no separate cache layer needed

---

## 3. Prompt Template System

Two-phase: load-time parsing, run-time substitution.

**Files:** `backend/prompt_manager.py`, `prompts/*.md`

- `prompt_manager.py` reads all `prompts/` files at startup, extracts metadata (title, order, extra_inputs) from front-matter comments
- Placeholders use `{{field_name}}` syntax; `SharedContext` fields (9 standard fields) + framework-specific `extra_inputs`
- `fill_prompt(prompt_id, context, extra_inputs)` performs string substitution; unfilled placeholders raise a descriptive error
- `get_prompts()` returns ordered list used by frontend sidebar (order field drives display sequence)

---

## 4. FastAPI Dependency Injection

Database session lifecycle managed via FastAPI `Depends`.

**Files:** `backend/database.py:get_db()`, `backend/main.py` (every route that touches DB)

```
# Pattern used in every DB route:
def route(db: Session = Depends(get_db)):
```

- `get_db()` yields a session and guarantees `db.close()` in a `finally` block
- All ORM operations go through the injected session; no global session state

---

## 5. React Context + localStorage Persistence

Global state shared across pages, persisted across reloads.

**Files:** `frontend/src/App.tsx`, every page/component via `useApp()` hook

- `AppContext` holds: `apiKey`, `theme`, `sessionId`, `sharedContext`
- `App.tsx` reads initial state from `localStorage` on mount; writes back on every change
- `useApp()` is the sole consumer interface — components never touch `localStorage` directly
- Routing guards: missing `apiKey` redirects to `/setup`; missing `sessionId` redirects from `/research`

---

## 6. Custom Hook Composition

Business logic extracted from components into focused hooks.

**Files:** `frontend/src/hooks/useAnalysis.ts`, `frontend/src/hooks/useSession.ts`

- `useAnalysis(promptId)`: owns the full streaming lifecycle — fetch, stream reading, state (`output`, `isStreaming`, `cost`, `cacheHit`), abort
- `useSession(sessionId)`: owns session loading and an `analysesMap` (keyed by `prompt_id`) for tab state persistence
- Components (`AnalysisTab`, `Research`) import both hooks and compose their return values — no streaming or session logic lives in component bodies

---

## 7. Dual Validation Layer

Input shapes validated at both API boundary and frontend compile-time.

**Files:** `backend/models.py` (Pydantic), `frontend/src/types.ts` (TypeScript)

- `models.py`: `SharedContext`, `AnalyzeRequest`, `ExportRequest` — FastAPI validates incoming JSON against these; invalid requests get 422 before hitting business logic
- `types.ts`: mirrors the same shapes as TypeScript interfaces — `SharedContext`, `Prompt`, `Analysis`, `Session`
- The two layers are manually kept in sync; there is no code-generation step
- `models.py` also contains `estimate_cost(model, input_tokens, output_tokens)` — a pure function used by `claude_client.py` after each stream completes
