import re
import requests
import os
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1)

def fetch_transcript(url: str) -> str:
    video_id = extract_video_id(url)
    response = requests.get(
        "https://api.supadata.ai/v1/youtube/transcript",
        params={"videoId": video_id, "text": True},
        headers={"x-api-key": SUPADATA_API_KEY}
    )
    data = response.json()
    return data.get("content", "Transcript not available")

@tool
def get_transcript(url: str) -> str:
    """Fetches full transcript text from a YouTube video URL."""
    return fetch_transcript(url)

@tool
def summarize_video(url: str) -> str:
    """Fetches YouTube transcript for summarization."""
    return fetch_transcript(url)