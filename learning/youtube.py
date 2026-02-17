"""
youtube.py

This module provides functionality to extract transcripts from YouTube videos
using the `youtube-transcript-api` library and store them in the memory system.
"""

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from typing import Dict, Any, List
from memory import Memory # Assuming Memory class is accessible

class YouTubeLearner:
    """
    Extracts transcripts from YouTube videos and adds them to the semantic knowledge memory.
    """

    def __init__(self, memory: Memory):
        self.memory = memory
        print("YouTubeLearner initialized.")

    def learn_from_youtube(self, video_url: str) -> Dict[str, Any]:
        """
        Extracts the transcript from a YouTube video and stores it in memory.
        """
        try:
            video_id = self._extract_video_id(video_url)
            if not video_id:
                return {"status": "error", "message": f"Invalid YouTube URL: {video_url}"}

            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([entry["text"] for entry in transcript_list])

            metadata = {"source": "youtube", "url": video_url, "video_id": video_id}
            self.memory.add_to_memory("semantic_knowledge", full_transcript, metadata=metadata)

            return {"status": "success", "url": video_url, "message": "Transcript extracted and stored in memory."}
        except NoTranscriptFound:
            return {"status": "error", "message": f"No transcript found for video: {video_url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_video_id(self, url: str) -> str:
        """
        Extracts the video ID from a YouTube URL.
        """
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("&")[0]
        return ""
