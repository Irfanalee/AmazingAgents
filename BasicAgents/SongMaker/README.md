# Song Maker

An AI agent that generates song lyrics and produces a **real, full song** (vocals + music) using OpenAI GPT-4o-mini for lyrics and [Suno](https://suno.com) for music generation via the [sunoapi.org](https://sunoapi.org) API.

> **Related agent:** If you only want lyrics without music, see the standalone [LyricsGenerator](../LyricsGenerator) agent.

## Features

- **Generate Lyrics & Song** — pick a topic, genre, and mood; GPT-4o-mini writes the lyrics, Suno produces the full song
- **Use Your Own Lyrics** — paste any existing lyrics and generate a song directly
- Suno generates **two song versions** per request so you can pick your favourite
- In-browser audio playback and one-click MP3 download for each version

## Requirements

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys) — used for lyrics generation
- A [Suno API key](https://sunoapi.org) — used for music generation (~5 credits per song)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API keys to a .env file
echo "OPENAI_API_KEY=sk-..." >> .env
echo "SUNO_API_KEY=your_suno_key..." >> .env

# 4. Run the app
streamlit run app.py
```

API keys can also be entered directly in the sidebar if you prefer not to use a `.env` file.

## How It Works

1. **Lyrics** — GPT-4o-mini writes structured lyrics (verses, chorus, bridge) based on your topic, genre, and mood.
2. **Song generation** — The lyrics are submitted to [sunoapi.org](https://sunoapi.org) with the genre/mood as the style prompt. Suno generates a complete song with vocals and instrumentation.
3. **Polling** — The app polls for the result every 5 seconds (songs are typically ready in ~40 seconds) and surfaces both generated versions for playback and download.

## Notes

- Each song generation costs ~5 Suno credits (two versions are produced per request).
- Songs are stored on Suno's servers for 15 days before being deleted — download anything you want to keep.
- The LyricsGenerator agent (`../LyricsGenerator`) is a separate, standalone tool if you only need lyrics.
