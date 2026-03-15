#!/usr/bin/env bash
# Run this ONCE before sharing the repo to bake the React UI into frontend/dist/
# Requires Node.js (https://nodejs.org)

cd "$(dirname "$0")"

if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js is not installed. Download it from https://nodejs.org"
    read -p "Press Enter to close..."
    exit 1
fi

echo "Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "Building frontend..."
npm run build

echo ""
echo "Done! frontend/dist/ is ready. You can now commit and share the repo."
read -p "Press Enter to close..."
