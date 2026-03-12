#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════╗"
echo "║   McKinsey Research Suite — Setup          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# ── Python backend ────────────────────────────────────────────────
echo "📦 Installing Python dependencies…"
if command -v pip3 &>/dev/null; then
    pip3 install -r requirements.txt --quiet
elif command -v pip &>/dev/null; then
    pip install -r requirements.txt --quiet
else
    echo "❌ pip not found. Please install Python 3.9+ and pip."
    exit 1
fi
echo "✅ Python deps installed"

# ── Frontend ──────────────────────────────────────────────────────
echo ""
echo "📦 Installing Node.js dependencies…"
cd frontend
if command -v npm &>/dev/null; then
    npm install --silent
    echo "✅ Node deps installed"
else
    echo "❌ npm not found. Please install Node.js 18+."
    exit 1
fi
cd ..

# ── Create directories ────────────────────────────────────────────
mkdir -p data exports
echo ""
echo "✅ Setup complete!"
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  To start the app:                         ║"
echo "║                                            ║"
echo "║  Terminal 1 (backend):                     ║"
echo "║    uvicorn backend.main:app --reload       ║"
echo "║                                            ║"
echo "║  Terminal 2 (frontend):                    ║"
echo "║    cd frontend && npm run dev              ║"
echo "║                                            ║"
echo "║  Then open: http://localhost:5173          ║"
echo "╚════════════════════════════════════════════╝"
