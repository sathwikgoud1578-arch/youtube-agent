from langchain.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1)

@tool
def get_transcript(url: str) -> str:
    """Fetches full transcript text from a YouTube video URL."""
    video_id = extract_video_id(url)
    ytt = YouTubeTranscriptApi()
    data = ytt.fetch(video_id)
    return " ".join([entry.text for entry in data])

@tool
def summarize_video(url: str) -> str:
    """Fetches and splits YouTube transcript into chapters every 5 minutes."""
    video_id = extract_video_id(url)
    ytt = YouTubeTranscriptApi()
    data = ytt.fetch(video_id)

    chapters = []
    current_text = []
    current_start = 0
    chapter_num = 1

    for entry in data:
        if entry.start >= current_start + 300 and current_text:
            chapters.append(f"Chapter {chapter_num} ({int(current_start//60)} min): " + " ".join(current_text))
            chapter_num += 1
            current_start = entry.start
            current_text = []
        current_text.append(entry.text)

    if current_text:
        chapters.append(f"Chapter {chapter_num} ({int(current_start//60)} min): " + " ".join(current_text))

    return "\n\n".join(chapters)