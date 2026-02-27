import os
import time
import json
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class AIEngine:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def upload_file(self, path: str):
        print(f"Uploading file: {path}")
        video_file = self.client.files.upload(file=path)
        print(f"Completed upload: {video_file.uri}")

        # Wait for file to be active
        while video_file.state.name == "PROCESSING":
            print("Processing video...", end="\r")
            time.sleep(5)
            video_file = self.client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError("Video processing failed")

        print(f"\nFile is active: {video_file.name}")
        return video_file

    async def analyze_video(self, video_path: str):
        """
        Uploads video to Gemini and analyzes it to find highlights.
        Returns a list of timestamps (start, end) and descriptions.
        """
        try:
            # Run blocking upload in thread pool to avoid freezing the event loop
            loop = asyncio.get_event_loop()
            video_file = await loop.run_in_executor(None, self.upload_file, video_path)

            prompt = """
            Analyze this video and identify 3-5 most engaging or important highlights that would be suitable for a social media teaser.
            For each highlight, provide the start and end timestamps in "MM:SS" format, and a brief description.

            Detect the language spoken in the video and write all descriptions in that same language.
            For example, if the video is in Persian/Dari/Farsi, write the descriptions in Persian/Dari script.
            If the video is in English, write in English. Match whatever language is spoken.

            Return the response ONLY as a valid JSON list of objects with the following structure:
            [
                {"start": "MM:SS", "end": "MM:SS", "description": "Brief description in the video's language"}
            ]
            Do not include any markdown formatting or other text.
            """

            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[video_file, prompt]
            )
            print("Gemini Response:", response.text)
            
            return self._parse_timestamps(response.text)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return []

    def _parse_timestamps(self, response_text: str):
        try:
            # Clean up potential markdown code blocks
            text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            # Convert MM:SS to seconds
            highlights = []
            for item in data:
                start_sec = self._time_to_seconds(item['start'])
                end_sec = self._time_to_seconds(item['end'])
                highlights.append({
                    "start": start_sec,
                    "end": end_sec,
                    "description": item['description']
                })
            return highlights
        except json.JSONDecodeError:
            print("Failed to parse JSON from AI response")
            return []
            
    def _time_to_seconds(self, time_str: str) -> int:
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
