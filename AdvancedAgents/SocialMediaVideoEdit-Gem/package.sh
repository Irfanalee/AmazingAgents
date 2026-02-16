#!/bin/bash

echo "📦 Packaging Agentic Video Editor..."

# Define exclusion list
EXCLUDES="
--exclude=node_modules
--exclude=.git
--exclude=.next
--exclude=__pycache__
--exclude=processed/*
--exclude=uploads/*
--exclude=.env
--exclude=*.zip
"

# Create zip file
zip -r agentic-video-editor.zip . -x "node_modules/*" ".git/*" ".next/*" "__pycache__/*" "processed/*" "uploads/*" ".env" "*.zip"

echo "✅ Package created: agentic-video-editor.zip"
echo "Includes setup.bat for Windows users!"
