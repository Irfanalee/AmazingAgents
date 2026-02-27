import os
import shutil
import uuid
import json
import asyncio
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
# Register static-ffmpeg paths
import static_ffmpeg
static_ffmpeg.add_paths()

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ai_engine import AIEngine
from video_processor import VideoProcessor
from metadata_extractor import MetadataExtractor

app = FastAPI(title="Agentic Video Editor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video playback
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
app.mount("/static", StaticFiles(directory="processed"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

ai_engine = AIEngine()
video_processor = VideoProcessor()
metadata_extractor = MetadataExtractor()

# In-memory job store (replace with DB in production)
jobs = {}
# WebSocket connections for real-time logs
# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        # Map job_id to list of active websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        print(f"Client connected to job {job_id}. Total clients: {len(self.active_connections[job_id])}")

    def disconnect(self, job_id: str, websocket: WebSocket):
        if job_id in self.active_connections:
            if websocket in self.active_connections[job_id]:
                self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        print(f"Client disconnected from job {job_id}")

    async def broadcast(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            # Create a copy of the list to iterate safely
            for connection in self.active_connections[job_id][:]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to client: {e}")
                    self.disconnect(job_id, connection)

manager = ConnectionManager()

async def send_log(job_id: str, message: str, level: str = "info"):
    """Send log message to all connected clients for a job"""
    await manager.broadcast(job_id, {
        "type": "log",
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def update_timeline(job_id: str, event: str, status: str = "completed"):
    """Update timeline event"""
    if job_id not in jobs:
        return
    
    if "timeline" not in jobs[job_id]:
        jobs[job_id]["timeline"] = []
    
    jobs[job_id]["timeline"].append({
        "event": event,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })
    
    await manager.broadcast(job_id, {
        "type": "timeline",
        "timeline": jobs[job_id]["timeline"]
    })

@app.get("/")
async def root():
    return {"message": "Agentic Video Editor API is running"}

@app.get("/videos")
async def list_videos():
    """List all uploaded videos with metadata"""
    videos = []
    
    if not os.path.exists("uploads"):
        return {"videos": []}
    
    for filename in os.listdir("uploads"):
        if filename.startswith('.'):
            continue
            
        file_path = f"uploads/{filename}"
        # Extract file_id from filename (format: {uuid}_{original_name})
        parts = filename.split('_', 1)
        file_id = parts[0] if len(parts) > 0 else filename
        
        metadata = metadata_extractor.extract_metadata(file_path)
        metadata['file_id'] = file_id
        metadata['path'] = file_path
        
        videos.append(metadata)
    
    # Sort by upload time (newest first)
    videos.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    
    return {"videos": videos}

@app.get("/processed")
async def list_processed_videos():
    """List all processed videos"""
    videos = []
    
    if not os.path.exists("processed"):
        return {"videos": []}
    
    for filename in os.listdir("processed"):
        if filename.startswith('.'):
            continue
            
        file_path = f"processed/{filename}"
        stats = os.stat(file_path)
        
        videos.append({
            "filename": filename,
            "path": f"/static/{filename}",
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat()
        })
    
    # Sort by creation time (newest first)
    videos.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return {"videos": videos}

@app.delete("/processed/{filename}")
async def delete_processed_video(filename: str):
    """Delete a processed video"""
    file_path = f"processed/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
        
    try:
        os.remove(file_path)
        return {"message": "Video deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos/{file_id}/metadata")
async def get_video_metadata(file_id: str):
    """Get detailed metadata for a specific video"""
    files = [f for f in os.listdir("uploads") if f.startswith(file_id)]
    if not files:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = f"uploads/{files[0]}"
    metadata = metadata_extractor.extract_metadata(file_path)
    metadata['file_id'] = file_id
    metadata['path'] = file_path
    
    return metadata

@app.delete("/videos/{file_id}")
async def delete_video(file_id: str):
    """Delete a video and its processed output"""
    deleted_files = []
    
    # Delete original upload
    upload_files = [f for f in os.listdir("uploads") if f.startswith(file_id)]
    for filename in upload_files:
        file_path = f"uploads/{filename}"
        os.remove(file_path)
        deleted_files.append(file_path)
    
    # Delete processed video if exists
    if os.path.exists("processed"):
        processed_files = [f for f in os.listdir("processed") if file_id in f]
        for filename in processed_files:
            file_path = f"processed/{filename}"
            os.remove(file_path)
            deleted_files.append(file_path)
    
    # Remove from jobs
    jobs_to_remove = [job_id for job_id, job in jobs.items() if job.get('file_id') == file_id]
    for job_id in jobs_to_remove:
        del jobs[job_id]
    
    if not deleted_files:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Video deleted successfully", "deleted_files": deleted_files}

@app.post("/upload")
def upload_video(file: UploadFile = File(...)):
    print(f"Receiving upload: {file.filename}")
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"Upload saved: {file_path}")
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Extract metadata
    metadata = metadata_extractor.extract_metadata(file_path)
    
    return {
        "id": file_id,
        "filename": file.filename,
        "path": file_path,
        "metadata": metadata
    }

async def run_analysis_agent(job_id: str, file_path: str):
    """Agent Qazi: Analyzes video and finds highlights"""
    jobs[job_id]["status"] = "analyzing"
    await update_timeline(job_id, "Analysis Started", "in_progress")
    await send_log(job_id, f"Starting AI analysis of video: {file_path}")
    
    try:
        await send_log(job_id, "Agent Qazi: Uploading video to Gemini...")
        highlights = await ai_engine.analyze_video(file_path)
        jobs[job_id]["highlights"] = highlights
        
        if not highlights:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No highlights found"
            await update_timeline(job_id, "Analysis Failed", "failed")
            await send_log(job_id, "No highlights detected in video", "error")
            return False

        await send_log(job_id, f"Agent Qazi: Found {len(highlights)} highlights!")
        for i, h in enumerate(highlights):
            await send_log(job_id, f"  Highlight {i+1}: {h.get('description', 'N/A')} ({h.get('start')}s - {h.get('end')}s)")
        
        await update_timeline(job_id, "Analysis Complete", "completed")
        return True
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        await update_timeline(job_id, "Analysis Error", "failed")
        await send_log(job_id, f"Analysis Error: {str(e)}", "error")
        return False

async def run_processing_agent(job_id: str, file_path: str):
    """Agent Trond: Cuts and processes video based on highlights"""
    if "highlights" not in jobs[job_id] or not jobs[job_id]["highlights"]:
        await send_log(job_id, "Agent Trond: No highlights found to process!", "error")
        return False

    jobs[job_id]["status"] = "processing"
    await update_timeline(job_id, "Video Processing Started", "in_progress")
    
    try:
        highlights = jobs[job_id]["highlights"]
        await send_log(job_id, "Agent Trond: Starting video processing with FFmpeg...")
        output_filename = f"processed_{job_id}.mp4"
        output_path = f"processed/{output_filename}"
        
        await send_log(job_id, f"Agent Trond: Cutting {len(highlights)} video segments...")
        success = video_processor.process_highlights(file_path, highlights, output_path)
        
        if success:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["output_url"] = f"/static/{output_filename}"
            await update_timeline(job_id, "Processing Complete", "completed")
            await send_log(job_id, f"✓ Video processing complete! Output: {output_filename}", "success")
            return True
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "Video processing failed"
            await update_timeline(job_id, "Processing Failed", "failed")
            await send_log(job_id, "Video processing failed", "error")
            return False
            
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        await update_timeline(job_id, "Processing Error", "failed")
        await send_log(job_id, f"Processing Error: {str(e)}", "error")
        return False

async def process_video_task(job_id: str, file_path: str):
    """Orchestrator: Runs Qazi then Trond"""
    if await run_analysis_agent(job_id, file_path):
        await run_processing_agent(job_id, file_path)

@app.post("/process/{file_id}")
async def start_processing(file_id: str, background_tasks: BackgroundTasks):
    # Find file (in a real app, look up in DB)
    files = [f for f in os.listdir("uploads") if f.startswith(file_id)]
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = f"uploads/{files[0]}"
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "id": job_id,
        "file_id": file_id,
        "status": "queued",
        "timeline": [{
            "event": "Video Uploaded",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    background_tasks.add_task(process_video_task, job_id, file_path)
    
    return jobs[job_id]

class Clip(BaseModel):
    start: float
    end: float
    description: str = "Manual clip"

class ManualProcessRequest(BaseModel):
    clips: List[Clip]

@app.post("/process/manual/{file_id}")
async def start_manual_processing(file_id: str, request: ManualProcessRequest, background_tasks: BackgroundTasks):
    """Start manual processing with user-defined clips"""
    files = [f for f in os.listdir("uploads") if f.startswith(file_id)]
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = f"uploads/{files[0]}"
    job_id = str(uuid.uuid4())
    
    # Convert Pydantic models to dicts
    highlights = [clip.model_dump() for clip in request.clips]
    
    jobs[job_id] = {
        "id": job_id,
        "file_id": file_id,
        "status": "queued",
        "highlights": highlights,
        "timeline": [{
            "event": "Manual Clips Received",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    # Skip analysis, go straight to processing
    background_tasks.add_task(run_processing_agent, job_id, file_path)
    
    return jobs[job_id]

@app.post("/agent/qazi/{file_id}")
async def invoke_qazi(file_id: str, background_tasks: BackgroundTasks):
    """Invoke Agent Qazi (Analysis Only)"""
    files = [f for f in os.listdir("uploads") if f.startswith(file_id)]
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = f"uploads/{files[0]}"
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "id": job_id,
        "file_id": file_id,
        "status": "queued",
        "timeline": [{
            "event": "Agent Qazi Summoned",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    background_tasks.add_task(run_analysis_agent, job_id, file_path)
    return jobs[job_id]

@app.post("/agent/trond/{job_id}")
async def invoke_trond(job_id: str, background_tasks: BackgroundTasks):
    """Invoke Agent Trond (Processing Only - requires existing job with highlights)"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    files = [f for f in os.listdir("uploads") if f.startswith(job['file_id'])]
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
        
    file_path = f"uploads/{files[0]}"
    
    # Reset status for processing
    job["status"] = "queued"
    await update_timeline(job_id, "Agent Trond Summoned", "completed")
    
    background_tasks.add_task(run_processing_agent, job_id, file_path)
    return job

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(job_id, websocket)
    
    # Send initial timeline if job exists
    if job_id in jobs and "timeline" in jobs[job_id]:
        try:
            await websocket.send_json({
                "type": "timeline",
                "timeline": jobs[job_id]["timeline"]
            })
        except Exception as e:
            print(f"Failed to send initial timeline: {e}")
            manager.disconnect(job_id, websocket)
            return
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(job_id, websocket)
