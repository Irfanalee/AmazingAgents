# Song Maker

An AI agent that generates song lyrics and turns them into sung audio using OpenAI GPT-4o-mini and Suno's Bark model via Replicate.

## Features

- **Generate Lyrics & Song** — pick a topic, genre, and mood; the agent writes the lyrics and sings them
- **Use Your Own Lyrics** — paste any lyrics and have them vocalized immediately
- 8 voice presets to choose from
- Adjustable creativity sliders for both lyric writing and audio generation
- In-browser audio playback and a one-click download button

## Requirements

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Replicate API token](https://replicate.com/account/api-tokens)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API keys to a .env file
echo "OPENAI_API_KEY=sk-..." >> .env
echo "REPLICATE_API_TOKEN=r8_..." >> .env

# 4. Run the app
streamlit run app.py
```

API keys can also be entered directly in the sidebar if you prefer not to use a `.env` file.

## How It Works

1. **Lyrics** — GPT-4o-mini writes structured lyrics (verses, chorus, bridge) based on your prompt.
2. **Audio** — The lyrics are sent to [Bark](https://replicate.com/suno-ai/bark) on Replicate, which vocalizes the text using a neural text-to-audio model.
3. The generated WAV file is streamed back and displayed inline for playback and download.

## Notes

- Bark generates spoken/sung audio; it is not a full music production tool (no backing instrumentals).
- Generation typically takes 30–90 seconds depending on lyric length.
- Shorter lyrics (one verse + chorus) produce faster, cleaner results.
