from youtube_transcript_api import YouTubeTranscriptApi
import logging

logger = logging.getLogger(__name__)

class YouTubeLearner:
    def __init__(self):
        pass

    def get_transcript(self, video_id: str) -> str:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry["text"] for entry in transcript_list])
            logger.info(f"Successfully extracted transcript for video ID: {video_id}")
            return transcript
        except Exception as e:
            logger.error(f"Error extracting transcript for video ID {video_id}: {e}")
            return f"Error: Could not retrieve transcript. {e}"
