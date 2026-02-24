# SocialMediaVideoEdit-Gem

AI-powered video editor that analyzes long-form videos and produces social media highlight reels. Supports two modes: fully automated (Gemini AI analysis + FFmpeg editing) and manual clip selection.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI | Google Gemini Flash (`google-generativeai`) |
| Video | FFmpeg via `ffmpeg-python`, `static-ffmpeg`, FFprobe |
| Frontend | Next.js 14 (App Router), React 19, TypeScript 5 |
| Styling | Tailwind CSS 4 |
| Real-time | WebSockets (native FastAPI + browser) |
| Infra | Docker Compose (two containers) |

## Key Directories

```
backend/          Python FastAPI app (AI engine, video processing, WebSocket server)
frontend/         Next.js app (upload UI, manual clipper, video library, live logs)
.agent/workflows/ Agent role docs (Qazi = analysis, Trond = processing, Hans = frontend health)
uploads/          Raw uploaded videos (mounted Docker volume)
processed/        Generated highlight reels (mounted Docker volume)
```

**Core backend files:**
- `backend/main.py` — all API endpoints and WebSocket hub
- `backend/ai_engine.py` — Gemini API integration (Agent Qazi logic)
- `backend/video_processor.py` — FFmpeg cut/concatenate pipeline (Agent Trond logic)
- `backend/metadata_extractor.py` — FFprobe wrapper

**Core frontend files:**
- `frontend/app/page.tsx` — main page, tab routing
- `frontend/components/UploadComponent.tsx` — drag-and-drop upload
- `frontend/components/ProcessingLogs.tsx` — WebSocket log viewer
- `frontend/components/ManualClipper.tsx` — manual clip UI

## Environment

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.

## Commands

### Docker (recommended)
```bash
./setup.sh                    # first-time setup (prompts for API key)
docker-compose up --build     # start both containers
```
Ports: frontend → 3000, backend → 8000.

### Backend (local dev)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (local dev)
```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
npm run build
npm run lint
```

### Backend smoke test
```bash
cd backend && python test_ffmpeg.py
```

## Additional Documentation

Check these files when working on the relevant area:

| Topic | File |
|-------|------|
| Architectural patterns & design decisions | `.claude/docs/architectural_patterns.md` |
| Agent role definitions | `.agent/workflows/qazi.md`, `trond.md`, `hans.md` |
| Installation & Docker details | `INSTALL.md` |
| Common issues | `TROUBLESHOOTING.md` |
