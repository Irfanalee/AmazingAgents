#!/usr/bin/env bash
# Mac double-click launcher for NPI Strategy Suite

# Move to the directory containing this script
cd "$(dirname "$0")"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "ERROR: Virtual environment not found."
    echo "Please run the first-time setup from HOW_TO_RUN.md first."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "Starting NPI Strategy Suite on http://localhost:8000 ..."
echo "Press Ctrl+C to stop."
echo ""

# Open browser after a short delay so the server is ready
(sleep 2 && open "http://localhost:8000") &

uvicorn backend.main:app --host 0.0.0.0 --port 8000
