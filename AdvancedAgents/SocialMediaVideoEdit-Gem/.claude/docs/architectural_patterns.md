# Architectural Patterns

## Agent-Based Processing Pipeline

The backend separates AI analysis from video editing into two named agents, each invokable independently or as a chain.

- **Agent Qazi** (`backend/ai_engine.py`) — uploads video to Gemini, prompts for 3–5 highlight timestamps in structured JSON, parses `MM:SS` → seconds
- **Agent Trond** (`backend/video_processor.py`) — receives highlight list, cuts segments with FFmpeg, concatenates into final reel
- Orchestrated in `backend/main.py:POST /process/{file_id}` via FastAPI `BackgroundTasks`
- Each agent also has a direct endpoint (`/agent/qazi/{file_id}`, `/agent/trond/{job_id}`) for independent invocation

## Job State Machine

All processing is tracked in an in-memory dict in `backend/main.py` (search `jobs = {}`). Status values: `queued → analyzing → processing → completed | failed`. The same dict drives WebSocket broadcasts and REST polling.

> **Note:** State is lost on restart. No persistence layer exists yet.

## WebSocket Hub Pattern

`backend/main.py` contains a `ConnectionManager` class that maps `job_id → List[WebSocket]`. Every log line and timeline update is broadcast to all sockets for that job. Frontend (`frontend/components/ProcessingLogs.tsx`) auto-reconnects every 3 seconds on disconnect.

Pattern: backend pushes `{"type": "log"|"timeline", ...}` JSON frames; frontend switches on `type` to route to the correct state slice.

## FFmpeg Copy-then-Re-encode Fallback

`backend/video_processor.py` always tries `codec=copy` first (fast, lossless). On failure it re-encodes (`libx264`, `fast` preset, CRF 23). This pattern appears in both the segment-cutting step and the concatenation step.

## Gemini Response Sanitization

`backend/ai_engine.py` strips markdown code fences (` ```json ... ``` `) before `json.loads()`. Gemini frequently wraps JSON output in fences; this strip-then-parse idiom must be preserved whenever the prompt returns structured data.

## Frontend State & Polling

- All UI state lives in `useState` hooks in `frontend/app/page.tsx` and individual components — no global store.
- Job status is polled every 2 seconds via `setInterval` + Axios GET to `/jobs/{job_id}`.
- WebSocket is a parallel channel for log lines only; authoritative status always comes from the REST poll.

## UUID + Original Filename File References

When a video is uploaded (`backend/main.py:POST /upload`), a UUID is generated and prepended to the original filename (`{uuid}_{original}.mp4`). This UUID is the `file_id` used throughout the API. Processed outputs use the same UUID prefix so they can be correlated back to the source upload.

## Component Composition Pattern (Frontend)

Every frontend component is a `"use client"` file that receives data via props and manages its own local state. There is no context or prop-drilling beyond one level. Components communicate upward via callback props (e.g., `onProcessingStart`, `onJobCreated`).

## API Response Shape

All job-related endpoints return the same envelope (see `backend/main.py`):

```
{
  "id": str,
  "status": str,
  "file_id": str,
  "highlights": [...],   # populated after Qazi completes
  "timeline": [...],     # step-by-step log entries
  "output_url": str      # populated after Trond completes
}
```

Frontend components expect this shape — maintain it when adding new endpoints.
