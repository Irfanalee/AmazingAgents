# Agentic Video Editor

An AI-powered video editing tool that automatically analyzes long-form videos, extracts the most engaging highlights, and creates social media-ready teasers. Now featuring a **Manual Clipping Mode** for precise control.

## Features

### 🤖 Agentic AI Mode
- **AI Video Analysis**: Uses Google Gemini Flash to watch and understand video content.
- **Viral Highlight Detection**: Automatically identifies the 3-5 most engaging moments.
- **Automated Editing**: "Agent Trond" cuts and stitches clips using FFmpeg without human intervention.

### ✂️ Manual Clipping Mode
- **Precision Control**: Watch the video and select your own start/end times.
- **Multi-Clip Selection**: Choose up to 5 distinct clips from a single video.
- **Instant Processing**: Stitches your selected clips into a seamless reel immediately.

### 📂 Video Library
- **Upload Management**: View and manage all your raw video uploads.
- **Generated Library**: Access, play, and download your processed highlight reels.
- **Delete Functionality**: Easily remove old videos to save space.

### 🛠️ Tech Stack
- **Frontend**: Next.js 14, React, Tailwind CSS, Lucide Icons.
- **Backend**: FastAPI (Python), Pydantic.
- **AI Engine**: Google Gemini API (`gemini-flash-latest`).
- **Video Processing**: FFmpeg.
- **Infrastructure**: Docker & Docker Compose.

## Architecture: The Developer Agents

This project is built around the concept of specialized "Developer Agents":

- **Agent Qazi (Analysis)**: Uses Gemini AI to watch the video and identify viral highlights.
- **Agent Trond (Processing)**: Uses FFmpeg to physically cut and stitch the video segments.
- **Agent Hans (Frontend)**: Ensures the React frontend is healthy and connected.

## Prerequisites

- Docker and Docker Compose
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd SocialMediaVideoEdit-Gem
   ```

2. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

## Usage Guide

### Agentic Mode (Auto-Edit)
1. Upload a video file.
2. Select **"Agentic AI"** mode.
3. Click **"Start AI Processing"**.
4. Watch the real-time logs as Agent Qazi analyzes and Agent Trond edits.
5. Download the final result from the timeline or library.

### Manual Mode (Custom Edit)
1. Upload a video file.
2. Select **"Manual Clipping"** mode.
3. Use the video player to find your start time and click **"Set Start"**.
4. Find your end time and click **"Set End"**.
5. Click **"Add Clip"**. Repeat for up to 5 clips.
6. Click **"Create Reel"** to stitch them together.

## API Endpoints

### Core
- `GET /` - Health check
- `POST /upload` - Upload a video file
- `GET /videos` - List uploaded videos
- `GET /processed` - List processed videos

### Processing
- `POST /process/{file_id}` - Start Agentic AI processing
- `POST /process/manual/{file_id}` - Start Manual processing (requires clip data)

### Agents (Direct Access)
- `POST /agent/qazi/{file_id}` - Invoke Analysis Agent only
- `POST /agent/trond/{job_id}` - Invoke Processing Agent only

### Management
- `GET /jobs/{job_id}` - Check job status
- `DELETE /videos/{file_id}` - Delete upload and associated data
- `DELETE /processed/{filename}` - Delete a processed video

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## License

MIT
