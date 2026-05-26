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
        """Fetch recent videos from a channel"""
        videos = []
        try:
            channel_response = requests.get(
                f"{self.base_url}/channels",
                params={'part': 'contentDetails,snippet', 'id': channel_id, 'key': self.api_key},
                timeout=10
            )
            
            if channel_response.status_code != 200:
                return videos
            
            channel_data = channel_response.json()
            if not channel_data.get('items'):
                return videos
            
            channel_info = channel_data['items'][0]
            channel_name = channel_info['snippet']['title']
            uploads_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            playlist_response = requests.get(
                f"{self.base_url}/playlistItems",
                params={'part': 'snippet', 'playlistId': uploads_id, 'maxResults': max_results, 'key': self.api_key},
                timeout=10
            )
            
            if playlist_response.status_code != 200:
                return videos
            
            playlist_data = playlist_response.json()
            video_ids = [item['snippet']['resourceId']['videoId'] 
                        for item in playlist_data.get('items', [])]
            
            if not video_ids:
                return videos
            
            details_response = requests.get(
                f"{self.base_url}/videos",
                params={'part': 'snippet,statistics', 'id': ','.join(video_ids), 'key': self.api_key},
                timeout=10
            )
            
            if details_response.status_code != 200:
                return videos
            
            details_data = details_response.json()
            
            for video in details_data.get('items', []):
                snippet = video['snippet']
                stats = video.get('statistics', {})
                
                thumbnails = snippet.get('thumbnails', {})
                thumb = ''
                for q in ['high', 'medium', 'default']:
                    if q in thumbnails:
                        thumb = thumbnails[q]['url']
                        break
                
                videos.append({
                    'id': video['id'],
                    'title': snippet['title'],
                    'description': snippet.get('description', ''),
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'published_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                    'view_count': int(stats.get('viewCount', 0)),
                    'thumbnail_url': thumb,
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                })
            
            logger.info(f"Fetched {len(videos)} from {channel_name}")
            
        except Exception as e:
            logger.error(f"Channel error: {e}")
        
        return videos
    
    def search_videos(self, query, max_results=5):
        """Search for LLM videos"""
        videos = []
        try:
            search_response = requests.get(
                f"{self.base_url}/search",
                params={'part': 'snippet', 'q': query, 'type': 'video', 
                       'maxResults': max_results, 'relevanceLanguage': 'en', 'key': self.api_key},
                timeout=10
            )
            
            if search_response.status_code != 200:
                return videos
            
            search_data = search_response.json()
            
            if 'error' in search_data:
                return videos
            
            video_ids = [item['id']['videoId'] for item in search_data.get('items', []) 
                        if 'videoId' in item.get('id', {})]
            
            if not video_ids:
                return videos
            
            details_response = requests.get(
                f"{self.base_url}/videos",
                params={'part': 'snippet,statistics', 'id': ','.join(video_ids), 'key': self.api_key},
                timeout=10
            )
            
            if details_response.status_code != 200:
                return videos
            
            details_data = details_response.json()
            
            for video in details_data.get('items', []):
                snippet = video['snippet']
                stats = video.get('statistics', {})
                
                thumbnails = snippet.get('thumbnails', {})
                thumb = ''
                for q in ['high', 'medium', 'default']:
                    if q in thumbnails:
                        thumb = thumbnails[q]['url']
                        break
                
                videos.append({
                    'id': video['id'],
                    'title': snippet['title'],
                    'description': snippet.get('description', ''),
                    'channel_id': snippet['channelId'],
                    'channel_name': snippet['channelTitle'],
                    'published_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                    'view_count': int(stats.get('viewCount', 0)),
                    'thumbnail_url': thumb,
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                })
            
            logger.info(f"Search found {len(videos)} videos")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
        
        return videos
