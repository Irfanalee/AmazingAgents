import json
import uuid
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session as DBSession

from .database import (
    init_db,
    get_db,
    Session as SessionModel,
    Analysis as AnalysisModel,
    Cache as CacheModel,
)
from .models import AnalyzeRequest, SessionCreate, SessionUpdate, ExportRequest, estimate_cost
from .prompt_manager import get_all_prompts, get_prompt_by_id, fill_prompt
from .claude_client import stream_analysis
from .export_service import generate_docx, generate_pdf

app = FastAPI(title="ProductLaunchStrategy Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ── Prompts ───────────────────────────────────────────────────────────────────

@app.get("/api/prompts")
def list_prompts():
    return get_all_prompts()


@app.get("/api/prompts/{prompt_id}")
def get_prompt(prompt_id: str):
    p = get_prompt_by_id(prompt_id)
    if not p:
        raise HTTPException(404, "Prompt not found")
    return p


# ── Streaming analysis ────────────────────────────────────────────────────────

@app.post("/api/analyze/estimate")
async def estimate_analysis_cost(
    request: AnalyzeRequest,
    x_api_key: Optional[str] = Header(None),
):
    if not x_api_key:
        raise HTTPException(400, "X-API-Key header required")

    filled = fill_prompt(request.prompt_id, request.shared_context, request.extra_inputs)
    if not filled:
        raise HTTPException(404, f"Prompt '{request.prompt_id}' not found")

    # ~4 chars per token is a reliable estimate for English prose
    input_tokens_estimate = len(filled) // 4
    # Assume ~2000 output tokens as a midpoint of the 4096 max
    output_tokens_estimate = 2000
    cost = estimate_cost(request.model, input_tokens_estimate, output_tokens_estimate)

    return {
        "input_tokens_estimate": input_tokens_estimate,
        "output_tokens_estimate": output_tokens_estimate,
        "cost_usd_estimate": round(cost, 6),
        "model": request.model,
    }


@app.post("/api/analyze/stream")
async def analyze_stream(
    request: AnalyzeRequest,
    x_api_key: Optional[str] = Header(None),
    db: DBSession = Depends(get_db),
):
    if not x_api_key:
        raise HTTPException(400, "X-API-Key header required")

    filled = fill_prompt(request.prompt_id, request.shared_context, request.extra_inputs)
    if not filled:
        raise HTTPException(404, f"Prompt '{request.prompt_id}' not found")

    inputs_dict = {
        "shared_context": request.shared_context.model_dump(),
        "extra_inputs": request.extra_inputs,
    }

    async def event_generator():
        async for chunk in stream_analysis(
            api_key=x_api_key,
            model=request.model,
            prompt_id=request.prompt_id,
            filled_prompt=filled,
            inputs_dict=inputs_dict,
            db=db,
            session_id=request.session_id,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Sessions ──────────────────────────────────────────────────────────────────

@app.get("/api/sessions")
def list_sessions(db: DBSession = Depends(get_db)):
    sessions = (
        db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    )
    prompt_map = {p["id"]: p["title"] for p in get_all_prompts()}
    result = []
    for s in sessions:
        analyses = (
            db.query(AnalysisModel)
            .filter(AnalysisModel.session_id == s.id)
            .all()
        )
        completed_prompts = list({a.prompt_id for a in analyses})
        total_cost = sum(a.cost_usd or 0 for a in analyses)
        result.append(
            {
                "id": s.id,
                "name": s.name,
                "shared_context": (
                    json.loads(s.shared_context) if s.shared_context else {}
                ),
                "theme": s.theme,
                "created_at": s.created_at.isoformat(),
                "updated_at": (
                    s.updated_at.isoformat() if s.updated_at else s.created_at.isoformat()
                ),
                "analysis_count": len(analyses),
                "completed_prompts": completed_prompts,
                "total_cost_usd": round(total_cost, 4),
            }
        )
    return result


@app.post("/api/sessions")
def create_session(data: SessionCreate, db: DBSession = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = SessionModel(
        id=session_id,
        name=data.name,
        shared_context=(
            json.dumps(data.shared_context.model_dump())
            if data.shared_context
            else "{}"
        ),
        theme=data.theme,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "name": session.name,
        "theme": session.theme,
        "created_at": session.created_at.isoformat(),
    }


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = (
        db.query(SessionModel).filter(SessionModel.id == session_id).first()
    )
    if not session:
        raise HTTPException(404, "Session not found")

    analyses = (
        db.query(AnalysisModel)
        .filter(AnalysisModel.session_id == session_id)
        .order_by(AnalysisModel.created_at)
        .all()
    )
    prompt_map = {p["id"]: p["title"] for p in get_all_prompts()}

    return {
        "id": session.id,
        "name": session.name,
        "shared_context": (
            json.loads(session.shared_context) if session.shared_context else {}
        ),
        "theme": session.theme,
        "created_at": session.created_at.isoformat(),
        "analyses": [
            {
                "id": a.id,
                "prompt_id": a.prompt_id,
                "prompt_title": prompt_map.get(a.prompt_id, a.prompt_id),
                "output": a.output,
                "model": a.model,
                "input_tokens": a.input_tokens,
                "output_tokens": a.output_tokens,
                "cost_usd": a.cost_usd,
                "from_cache": a.from_cache,
                "created_at": a.created_at.isoformat(),
            }
            for a in analyses
        ],
    }


@app.put("/api/sessions/{session_id}")
def update_session(
    session_id: str, data: SessionUpdate, db: DBSession = Depends(get_db)
):
    session = (
        db.query(SessionModel).filter(SessionModel.id == session_id).first()
    )
    if not session:
        raise HTTPException(404, "Session not found")
    if data.name is not None:
        session.name = data.name
    if data.shared_context is not None:
        session.shared_context = json.dumps(data.shared_context.model_dump())
    if data.theme is not None:
        session.theme = data.theme
    session.updated_at = datetime.utcnow()
    db.commit()
    return {"id": session.id, "name": session.name, "theme": session.theme}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, db: DBSession = Depends(get_db)):
    session = (
        db.query(SessionModel).filter(SessionModel.id == session_id).first()
    )
    if not session:
        raise HTTPException(404, "Session not found")
    db.query(AnalysisModel).filter(
        AnalysisModel.session_id == session_id
    ).delete()
    db.delete(session)
    db.commit()
    return {"ok": True}


# ── Export ────────────────────────────────────────────────────────────────────

@app.post("/api/export")
def export_report(request: ExportRequest, db: DBSession = Depends(get_db)):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == request.session_id)
        .first()
    )
    if not session:
        raise HTTPException(404, "Session not found")

    query = db.query(AnalysisModel).filter(
        AnalysisModel.session_id == request.session_id
    )
    if request.selected_analyses:
        query = query.filter(
            AnalysisModel.prompt_id.in_(request.selected_analyses)
        )
    analyses = query.order_by(AnalysisModel.created_at).all()

    if not analyses:
        raise HTTPException(400, "No analyses found for this session")

    prompt_map = {p["id"]: p["title"] for p in get_all_prompts()}
    analyses_data = [
        {
            "prompt_id": a.prompt_id,
            "title": prompt_map.get(a.prompt_id, a.prompt_id),
            "output": a.output or "",
            "cost_usd": a.cost_usd or 0,
            "from_cache": a.from_cache or False,
        }
        for a in analyses
    ]

    safe_name = "".join(
        c for c in session.name if c.isalnum() or c in " _-"
    ).strip()[:40] or "report"

    try:
        if request.format == "docx":
            filepath = generate_docx(session.name, analyses_data)
            return FileResponse(
                filepath,
                filename=f"pls_{safe_name}.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        elif request.format == "pdf":
            filepath = generate_pdf(session.name, analyses_data)
            return FileResponse(
                filepath,
                filename=f"pls_{safe_name}.pdf",
                media_type="application/pdf",
            )
        else:
            raise HTTPException(400, "Format must be 'docx' or 'pdf'")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Export failed: {exc}") from exc


# ── Cache ─────────────────────────────────────────────────────────────────────

@app.get("/api/cache/stats")
def cache_stats(db: DBSession = Depends(get_db)):
    entries = db.query(CacheModel).all()
    total_hits = sum(e.hit_count or 0 for e in entries)
    total_saved = sum((e.cost_usd or 0) * (e.hit_count or 0) for e in entries)
    return {
        "total_entries": len(entries),
        "total_hits": total_hits,
        "estimated_savings_usd": round(total_saved, 4),
    }


@app.delete("/api/cache")
def clear_cache(db: DBSession = Depends(get_db)):
    db.query(CacheModel).delete()
    db.commit()
    return {"ok": True}
