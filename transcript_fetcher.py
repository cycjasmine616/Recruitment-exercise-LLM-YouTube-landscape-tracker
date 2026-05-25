from youtube_transcript_api import YouTubeTranscriptApi
import logging
import re

logger = logging.getLogger(__name__)

class TranscriptFetcher:
    def get_transcript(self, video_id):
        """Fetch transcript for a YouTube video"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            text = ' '.join([item['text'] for item in transcript_list])
            text = re.sub(r'\s+', ' ', text)
            return text, True
        except Exception as e:
            logger.debug(f"No transcript for {video_id}: {e}")
            return None, False
