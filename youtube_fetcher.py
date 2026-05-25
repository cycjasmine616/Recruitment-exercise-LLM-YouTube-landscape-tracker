import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YouTubeFetcher:
    def __init__(self):
        from config import Config
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def fetch_channel_videos(self, channel_id, max_results=5):
        videos = []
        try:
            channel_url = f"{self.base_url}/channels?part=snippet&id={channel_id}&key={self.api_key}"
            channel_resp = requests.get(channel_url).json()
            
            if not channel_resp.get('items'):
                logger.warning(f"No channel found for {channel_id}")
                return videos
            
            channel_name = channel_resp['items'][0]['snippet']['title']
            
            playlist_url = f"{self.base_url}/channels?part=contentDetails&id={channel_id}&key={self.api_key}"
            playlist_resp = requests.get(playlist_url).json()
            uploads_id = playlist_resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            videos_url = f"{self.base_url}/playlistItems?part=snippet&playlistId={uploads_id}&maxResults={max_results}&key={self.api_key}"
            videos_resp = requests.get(videos_url).json()
            
            video_ids = [item['snippet']['resourceId']['videoId'] for item in videos_resp.get('items', [])]
            
            if video_ids:
                details_url = f"{self.base_url}/videos?part=snippet,statistics,contentDetails&id={','.join(video_ids)}&key={self.api_key}"
                details_resp = requests.get(details_url).json()
                
                for video in details_resp.get('items', []):
                    snippet = video['snippet']
                    stats = video.get('statistics', {})
                    
                    videos.append({
                        'id': video['id'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'channel_id': channel_id,
                        'channel_name': channel_name,
                        'published_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                        'duration': 0,
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'thumbnail_url': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else snippet['thumbnails']['default']['url'],
                        'url': f"https://www.youtube.com/watch?v={video['id']}"
                    })
            
            logger.info(f"Fetched {len(videos)} videos from {channel_name}")
            
        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
        
        return videos
