import streamlit as st
from dotenv import load_dotenv
import os
import time
import requests

load_dotenv()

st.set_page_config(page_title="Song Maker", page_icon="🎸")

st.title("🎸 Song Maker")
st.markdown(
    "Paste your lyrics and produce a real song using Suno. "
    "Need lyrics first? Use the [LyricsGenerator] (https://github.com/Irfanalee/AmazingAgents/tree/main/BasicAgents/LyricsGenerator) agent."
)

SUNO_API_BASE = "https://api.sunoapi.org/api/v1"
POLL_INTERVAL = 5   # seconds between status checks
MAX_WAIT = 300      # give up after 5 minutes

GENRES = ["Pop", "Rock", "Hip-Hop", "R&B", "Country", "Jazz", "Blues", "Reggae", "Folk", "Electronic"]
MOODS  = ["Happy", "Sad", "Energetic", "Romantic", "Melancholic", "Uplifting", "Dark", "Chill"]

# --- Sidebar: API Key ---
with st.sidebar:
    st.header("API Key")
    suno_api_key = os.getenv("SUNO_API_KEY") or st.text_input(
        "Suno API Key", type="password"
    )
    st.markdown("---")
    st.caption("Get a Suno API key at [sunoapi.org](https://sunoapi.org)")

if not suno_api_key:
    st.info("Please provide your Suno API key in the sidebar or a `.env` file.")
    st.stop()


# --- Core functions ---

def start_song_generation(lyrics: str, style: str, title: str) -> str:
    """Submit a song generation job and return the task ID."""
    headers = {
        "Authorization": f"Bearer {suno_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "customMode": True,
        "instrumental": False,
        "model": "V4_5",
        "prompt": lyrics,
        "style": style,
        "title": title,
        "callBackUrl": "https://example.com/callback",
    }
    resp = requests.post(
        f"{SUNO_API_BASE}/generate",
        json=payload,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()

    data = body.get("data")
    if not data or "taskId" not in data:
        raise RuntimeError(f"Unexpected response from Suno API: {body}")

    return data["taskId"]


def poll_for_songs(task_id: str) -> list[dict]:
    """Poll until the task is done. Returns list of song dicts with audio_url."""
    headers = {"Authorization": f"Bearer {suno_api_key}"}
    elapsed = 0

    status_placeholder = st.empty()

    while elapsed < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        resp = requests.get(
            f"{SUNO_API_BASE}/generate/record-info",
            params={"taskId": task_id},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()

        task_data = body.get("data", {})
        status = task_data.get("status", "PENDING")
        status_placeholder.info(f"Status: {status} ({elapsed}s elapsed, usually ~40s)")

        if status in ("FAILED", "ERROR"):
            raise RuntimeError(f"Song generation failed: {task_data.get('errorMessage')}")

        if status == "SUCCESS":
            status_placeholder.empty()
            response = task_data.get("response", {})
            songs = response.get("sunoData", [])

            ready = [s for s in songs if s.get("audioUrl")]
            if ready:
                return ready

            raise RuntimeError(
                f"Song marked SUCCESS but no audioUrl found. Response: {response}"
            )

    raise TimeoutError("Song generation timed out after 5 minutes.")


def display_songs(songs: list[dict]):
    for i, song in enumerate(songs, 1):
        st.markdown(f"**Version {i}** — *{song.get('title', '')}*")
        audio_url = song["audioUrl"]
        audio_bytes = requests.get(audio_url, timeout=60).content
        st.audio(audio_bytes, format="audio/mpeg")
        st.download_button(
            label=f"Download Version {i}",
            data=audio_bytes,
            file_name=f"song_v{i}.mp3",
            mime="audio/mpeg",
            key=f"dl_{i}_{song['id']}",
        )


# --- Main UI ---
title = st.text_input("Song title", placeholder="e.g. Tokyo Rain")
lyrics_input = st.text_area("Paste your lyrics here", height=300)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("Genre / Style", GENRES)
with col2:
    mood = st.selectbox("Mood", MOODS)

if st.button("Make Song", type="primary"):
    if not title.strip():
        st.warning("Please enter a song title.")
    elif not lyrics_input.strip():
        st.warning("Please paste your lyrics.")
    else:
        with st.spinner("Submitting to Suno..."):
            task_id = start_song_generation(
                lyrics=lyrics_input,
                style=f"{genre} {mood}",
                title=title,
            )

        songs = poll_for_songs(task_id)

        st.subheader("Your Song")
        display_songs(songs)
