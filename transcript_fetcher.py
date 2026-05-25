from youtube_transcript_api import YouTubeTranscriptApi
import logging
import re

logger = logging.getLogger(__name__)

class TranscriptFetcher:
    def get_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = ' '.join([t['text'] for t in transcript])
            text = re.sub(r'\s+', ' ', text)
            return text, True
        except Exception as e:
            logger.warning(f"No transcript for {video_id}: {e}")
            return None, False
