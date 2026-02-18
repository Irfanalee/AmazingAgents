import streamlit as st
from openai import OpenAI
import replicate
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(page_title="Song Maker", page_icon="🎸")

st.title("🎸 Song Maker")
st.markdown("Generate lyrics with AI and transform them into a sung song using Bark.")

# --- Sidebar: API Keys ---
with st.sidebar:
    st.header("API Keys")
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.text_input(
        "OpenAI API Key", type="password"
    )
    replicate_api_key = os.getenv("REPLICATE_API_TOKEN") or st.text_input(
        "Replicate API Token", type="password"
    )
    st.markdown("---")
    st.caption("Get a Replicate token at [replicate.com](https://replicate.com)")

if not openai_api_key:
    st.info("Please provide your OpenAI API key in the sidebar or a `.env` file.")
    st.stop()

if not replicate_api_key:
    st.info("Please provide your Replicate API token in the sidebar or a `.env` file.")
    st.stop()

openai_client = OpenAI(api_key=openai_api_key)
os.environ["REPLICATE_API_TOKEN"] = replicate_api_key

VOICE_PRESETS = {
    "Speaker 1": "v2/en_speaker_0",
    "Speaker 2": "v2/en_speaker_1",
    "Speaker 3": "v2/en_speaker_2",
    "Speaker 4": "v2/en_speaker_3",
    "Speaker 5": "v2/en_speaker_4",
    "Speaker 6": "v2/en_speaker_5",
    "Speaker 7": "v2/en_speaker_6",
    "Speaker 8": "v2/en_speaker_7",
    "Announcer": "announcer",
}


def generate_lyrics(topic: str, genre: str, mood: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a talented songwriter. Write original, creative song lyrics "
                    "based on the user's request. Include verses, a chorus, and optionally "
                    "a bridge. Format the output clearly with section labels like [Verse 1], "
                    "[Chorus], [Bridge], etc."
                ),
            },
            {
                "role": "user",
                "content": f"Write a {genre} song with a {mood.lower()} mood about: {topic}",
            },
        ],
        temperature=0.9,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def generate_song_audio(
    lyrics: str, voice_preset: str, text_temp: float, waveform_temp: float
) -> bytes:
    output = replicate.run(
        "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
        input={
            "prompt": lyrics,
            "history_prompt": voice_preset,
            "text_temp": text_temp,
            "waveform_temp": waveform_temp,
        },
    )
    # output is a URL string; fetch the raw audio bytes
    audio_url = output["audio_out"] if isinstance(output, dict) else output
    return requests.get(audio_url).content


# --- Tabs ---
tab_generate, tab_existing = st.tabs(["Generate Lyrics & Song", "Use My Own Lyrics"])

# ---- Tab 1: Generate lyrics then song ----
with tab_generate:
    topic = st.text_input(
        "What should the song be about?",
        placeholder="e.g. a rainy day in Tokyo",
    )

    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox(
            "Genre / Style",
            ["Pop", "Rock", "Hip-Hop", "R&B", "Country", "Jazz", "Blues", "Reggae", "Folk", "Electronic"],
        )
    with col2:
        mood = st.selectbox(
            "Mood",
            ["Happy", "Sad", "Energetic", "Romantic", "Melancholic", "Uplifting", "Dark", "Chill"],
        )

    voice_label = st.selectbox("Voice Style", list(VOICE_PRESETS.keys()))

    col3, col4 = st.columns(2)
    with col3:
        text_temp = st.slider("Lyric Creativity", 0.1, 1.0, 0.7, 0.05)
    with col4:
        waveform_temp = st.slider("Audio Creativity", 0.1, 1.0, 0.7, 0.05)

    if st.button("Generate Lyrics & Song", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Writing your lyrics..."):
                lyrics = generate_lyrics(topic, genre, mood)

            st.subheader("Lyrics")
            st.text(lyrics)

            with st.spinner("Generating song audio — this may take a minute..."):
                audio_bytes = generate_song_audio(
                    lyrics, VOICE_PRESETS[voice_label], text_temp, waveform_temp
                )

            st.subheader("Your Song")
            st.audio(audio_bytes, format="audio/wav")
            st.download_button(
                label="Download Song",
                data=audio_bytes,
                file_name="song.wav",
                mime="audio/wav",
            )

# ---- Tab 2: Paste existing lyrics ----
with tab_existing:
    lyrics_input = st.text_area("Paste your lyrics here", height=300)

    voice_label_2 = st.selectbox("Voice Style ", list(VOICE_PRESETS.keys()))

    col5, col6 = st.columns(2)
    with col5:
        text_temp_2 = st.slider("Lyric Creativity ", 0.1, 1.0, 0.7, 0.05)
    with col6:
        waveform_temp_2 = st.slider("Audio Creativity ", 0.1, 1.0, 0.7, 0.05)

    if st.button("Make Song", type="primary"):
        if not lyrics_input.strip():
            st.warning("Please paste some lyrics first.")
        else:
            with st.spinner("Generating song audio — this may take a minute..."):
                audio_bytes_2 = generate_song_audio(
                    lyrics_input, VOICE_PRESETS[voice_label_2], text_temp_2, waveform_temp_2
                )

            st.subheader("Your Song")
            st.audio(audio_bytes_2, format="audio/wav")
            st.download_button(
                label="Download Song",
                data=audio_bytes_2,
                file_name="song.wav",
                mime="audio/wav",
            )
