import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YouTubeFetcher:
    def __init__(self):
        from config import Config
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def fetch_channel_videos(self, channel_id, max_results=8):
        videos = []
        
        try:
            channel_url = f"{self.base_url}/channels"
            params = {
                'part': 'contentDetails,snippet',
                'id': channel_id,
                'key': self.api_key
            }
            
            response = requests.get(channel_url, params=params, timeout=10)
            if response.status_code != 200:
                logger.error(f"Channel API error: {response.status_code}")
                return videos
            
            data = response.json()
            if not data.get('items'):
                logger.warning(f"Channel {channel_id} not found")
                return videos
            
            channel_info = data['items'][0]
            channel_name = channel_info['snippet']['title']
            uploads_playlist = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            playlist_url = f"{self.base_url}/playlistItems"
            playlist_params = {
                'part': 'snippet',
                'playlistId': uploads_playlist,
                'maxResults': max_results,
                'key': self.api_key
            }
            
            playlist_response = requests.get(playlist_url, params=playlist_params, timeout=10)
            if playlist_response.status_code != 200:
                return videos
            
            playlist_data = playlist_response.json()
            video_ids = []
            
            for item in playlist_data.get('items', []):
                vid = item['snippet']['resourceId']['videoId']
                video_ids.append(vid)
            
            if not video_ids:
                return videos
            
            details_url = f"{self.base_url}/videos"
            details_params = {
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(video_ids),
                'key': self.api_key
            }
            
            details_response = requests.get(details_url, params=details_params, timeout=10)
            if details_response.status_code != 200:
                return videos
            
            details_data = details_response.json()
            
            for video in details_data.get('items', []):
                snippet = video['snippet']
                stats = video.get('statistics', {})
                
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = ''
                for quality in ['maxres', 'high', 'medium', 'default']:
                    if quality in thumbnails:
                        thumbnail_url = thumbnails[quality]['url']
                        break
                
                video_obj = {
                    'id': video['id'],
                    'title': snippet['title'],
                    'description': snippet.get('description', ''),
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'published_at': datetime.fromisoformat(
                        snippet['publishedAt'].replace('Z', '+00:00')
                    ),
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'thumbnail_url': thumbnail_url,
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                
                videos.append(video_obj)
                logger.info(f"   {snippet['title'][:80]}")
            
            logger.info(f"Fetched {len(videos)} videos from {channel_name}")
            
        except Exception as e:
            logger.error(f"Error fetching channel {channel_id}: {e}")
        
        return videos
    
    def fetch_all_channels(self):
        from config import Config
        
        all_videos = []
        
        for channel_id, channel_name in Config.LLM_CHANNELS.items():
            logger.info(f"\n Fetching from: {channel_name}")
            try:
                videos = self.fetch_channel_videos(channel_id, Config.MAX_VIDEOS_PER_CHANNEL)
                all_videos.extend(videos)
            except Exception as e:
                logger.error(f"Failed for {channel_name}: {e}")
        
        logger.info(f"\n Total videos fetched: {len(all_videos)}")
        return all_videos
