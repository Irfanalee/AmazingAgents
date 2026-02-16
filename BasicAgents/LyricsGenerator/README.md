# Lyrics Generator

A Streamlit app that generates original song lyrics using OpenAI's GPT model. Provide a topic, pick a genre and mood, and get creative lyrics instantly.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your API key (choose one):
   - Copy `.env.example` to `.env` and add your OpenAI key:
     ```bash
     cp .env.example .env
     ```
   - Or paste it directly in the app sidebar when prompted

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Features

- **Topic input** — describe what the song should be about
- **Genre selection** — Pop, Rock, Hip-Hop, R&B, Country, Jazz, Blues, Reggae, Folk, Electronic
- **Mood selection** — Happy, Sad, Energetic, Romantic, Melancholic, Uplifting, Dark, Chill
- Generates structured lyrics with verses, chorus, and bridge
