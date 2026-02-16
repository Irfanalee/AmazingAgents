import static_ffmpeg
import subprocess
import os

static_ffmpeg.add_paths()

print("Checking ffmpeg...")
try:
    subprocess.run(["ffmpeg", "-version"], check=True)
    print("ffmpeg found!")
except Exception as e:
    print(f"ffmpeg failed: {e}")

print("Checking ffprobe...")
try:
    subprocess.run(["ffprobe", "-version"], check=True)
    print("ffprobe found!")
except Exception as e:
    print(f"ffprobe failed: {e}")
