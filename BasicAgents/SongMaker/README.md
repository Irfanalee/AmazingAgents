# Song Maker

An AI agent that turns lyrics into a **real, full song** (vocals + music) using [Suno](https://suno.com) via the [sunoapi.org](https://sunoapi.org) API.

> **Related agent:** Need lyrics first? Use the standalone [LyricsGenerator](../LyricsGenerator) agent, then paste the output here.

## Features

- Paste any lyrics and select a genre and mood
- Suno generates **two song versions** per request — pick your favourite
- In-browser audio playback and one-click MP3 download for each version

## Requirements

- Python 3.9+
- A [Suno API key](https://sunoapi.org) (~5 credits per song)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Suno API key to a .env file
echo "SUNO_API_KEY=your_key_here" >> .env

# 4. Run the app
streamlit run app.py
```

The API key can also be entered directly in the sidebar if you prefer not to use a `.env` file.

## How It Works

1. Paste your lyrics, set a title, genre, and mood.
2. The lyrics are submitted to [sunoapi.org](https://sunoapi.org) which sends them to Suno's music generation model.
3. The app polls for the result every 5 seconds — songs are typically ready in ~40 seconds.
4. Both generated versions are displayed for playback and download.

## Notes

- Each generation costs ~5 Suno credits and produces two song versions.
- Generated files are hosted by Suno for **15 days** — download anything you want to keep.
- This agent handles music only. Lyrics are written separately using the [LyricsGenerator](../LyricsGenerator) agent.
