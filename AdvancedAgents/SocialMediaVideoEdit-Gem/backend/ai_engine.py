import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AIEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def upload_file(self, path: str):
        print(f"Uploading file: {path}")
        video_file = genai.upload_file(path=path)
        print(f"Completed upload: {video_file.uri}")
        
        # Wait for file to be active
        while video_file.state.name == "PROCESSING":
            print("Processing video...", end="\r")
            time.sleep(5)
            video_file = genai.get_file(video_file.name)
            
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
            video_file = self.upload_file(video_path)
            
            prompt = """
            Analyze this video and identify 3-5 most engaging or important highlights that would be suitable for a social media teaser.
            For each highlight, provide the start and end timestamps in "MM:SS" format, and a brief description.
            
            Return the response ONLY as a valid JSON list of objects with the following structure:
            [
                {"start": "MM:SS", "end": "MM:SS", "description": "Brief description"}
            ]
            Do not include any markdown formatting or other text.
            """
            
            response = self.model.generate_content([video_file, prompt])
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
