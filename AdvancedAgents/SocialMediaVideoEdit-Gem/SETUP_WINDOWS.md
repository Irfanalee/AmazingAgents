# Running Agentic Video Editor on Windows

## Prerequisites

### 1. Install Docker Desktop
1. Go to https://www.docker.com/products/docker-desktop/
2. Download **Docker Desktop for Windows**
3. Run the installer and follow the prompts
4. Restart your computer when asked
5. After restart, open Docker Desktop and wait until it says **"Engine running"** in the bottom left

> Docker Desktop requires Windows 10/11 (64-bit) with WSL 2 enabled. The installer will guide you through enabling WSL 2 if needed.

### 2. Get a Gemini API Key
1. Go to https://aistudio.google.com/apikey
2. Sign in with a Google account
3. Click **"Create API Key"**
4. Copy the key — you'll need it in the next step

---

## Setup

### 3. Get the Project Files
Either clone with Git (if installed):
```
git clone <repo-url>
cd SocialMediaVideoEdit-Gem
```
Or download and extract the ZIP from GitHub, then open a terminal in that folder.

### 4. Create the `.env` File
1. In the project folder, find the file called `.env.example`
2. Make a copy of it and rename the copy to `.env`
3. Open `.env` with Notepad and replace `your_api_key_here` with your actual Gemini API key:
```
GEMINI_API_KEY=AIza...your_key_here...
```
4. Save and close the file

---

## Running the App

### 5. Open a Terminal in the Project Folder
- Hold **Shift** and right-click inside the project folder
- Select **"Open PowerShell window here"** (or "Open Terminal here")

### 6. Start the App
```
docker-compose up --build
```

The first run will download and build everything — this takes **5–10 minutes**.
Subsequent runs are much faster.

You'll know it's ready when you see lines like:
```
frontend-1  | ready - started server on http://localhost:3000
backend-1   | Uvicorn running on http://0.0.0.0:8000
```

### 7. Open the App
Open your browser and go to:
```
http://localhost:3000
```

---

## Stopping the App
In the same terminal, press **Ctrl + C**, then run:
```
docker-compose down
```

## Starting Again Later
Next time, just run (no `--build` needed):
```
docker-compose up
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker: command not found` | Docker Desktop is not installed or not running |
| Port 3000 already in use | Another app is using port 3000 — stop it or restart your PC |
| `invalid reference format` | Make sure you're running the command inside the project folder |
| App loads but AI analysis fails | Check your `GEMINI_API_KEY` in the `.env` file is correct |
| Docker Desktop won't start | Enable virtualization in BIOS, or enable WSL 2 in Windows Features |

---

## System Requirements
- Windows 10 (version 2004+) or Windows 11
- 8 GB RAM minimum (16 GB recommended for large videos)
- 10 GB free disk space (for Docker images + video files)
- Internet connection (for Gemini AI API calls)
