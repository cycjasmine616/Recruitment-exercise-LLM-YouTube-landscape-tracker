import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YouTubeFetcher:
    def __init__(self):
        from config import Config
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.use_search = getattr(Config, 'USE_SEARCH', False)
        self.search_queries = getattr(Config, 'SEARCH_QUERIES', [])
    
    def search_llm_videos(self, query, max_results=10):
        """Search for LLM-related videos"""
        videos = []
        try:
            search_url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'relevanceLanguage': 'en',
                'order': 'date',
                'key': self.api_key
            }
            
            response = requests.get(search_url, params=params).json()
            
            video_ids = []
            for item in response.get('items', []):
                video_ids.append(item['id']['videoId'])
            
            if video_ids:
                details_url = f"{self.base_url}/videos"
                details_params = {
                    'part': 'snippet,statistics,contentDetails',
                    'id': ','.join(video_ids),
                    'key': self.api_key
                }
                
                details_response = requests.get(details_url, params=details_params).json()
                
                for video in details_response.get('items', []):
                    snippet = video['snippet']
                    stats = video.get('statistics', {})
                    
                    channel_id = snippet['channelId']
                    channel_name = self.get_channel_name(channel_id)
                    
                    videos.append({
                        'id': video['id'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'channel_id': channel_id,
                        'channel_name': channel_name,
                        'published_at': datetime.fromisoformat(
                            snippet['publishedAt'].replace('Z', '+00:00')
                        ),
                        'duration': 0,
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'thumbnail_url': snippet['thumbnails']['high']['url'] 
                            if 'high' in snippet['thumbnails'] 
                            else snippet['thumbnails']['default']['url'],
                        'url': f"https://www.youtube.com/watch?v={video['id']}"
                    })
                    
                    logger.info(f"Found: {snippet['title'][:60]}... from {channel_name}")
            
        except Exception as e:
            logger.error(f"Search error for '{query}': {e}")
        
        return videos
    
    def get_channel_name(self, channel_id):
        """Get channel name from ID"""
        try:
            url = f"{self.base_url}/channels"
            params = {
                'part': 'snippet',
                'id': channel_id,
                'key': self.api_key
            }
            response = requests.get(url, params=params).json()
            if response.get('items'):
                return response['items'][0]['snippet']['title']
        except:
            pass
        return "Unknown Channel"
    
    def fetch_channel_videos(self, channel_id, max_results=5):
        """Fetch videos from a specific channel"""
        videos = []
        try:
            channel_url = f"{self.base_url}/channels"
            params = {
                'part': 'snippet,contentDetails',
                'id': channel_id,
                'key': self.api_key
            }
            channel_resp = requests.get(channel_url, params=params).json()
            
            if not channel_resp.get('items'):
                logger.warning(f"No channel found for ID: {channel_id}")
                return videos
            
            channel_info = channel_resp['items'][0]
            channel_name = channel_info['snippet']['title']
            uploads_playlist = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            playlist_url = f"{self.base_url}/playlistItems"
            playlist_params = {
                'part': 'snippet',
                'playlistId': uploads_playlist,
                'maxResults': max_results,
                'key': self.api_key
            }
            playlist_resp = requests.get(playlist_url, params=playlist_params).json()
            
            video_ids = []
            for item in playlist_resp.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_ids.append(video_id)
            
            if video_ids:
                details_url = f"{self.base_url}/videos"
                details_params = {
                    'part': 'snippet,statistics,contentDetails',
                    'id': ','.join(video_ids),
                    'key': self.api_key
                }
                details_resp = requests.get(details_url, params=details_params).json()
                
                for video in details_resp.get('items', []):
                    snippet = video['snippet']
                    stats = video.get('statistics', {})
                    
                    videos.append({
                        'id': video['id'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'channel_id': channel_id,
                        'channel_name': channel_name,
                        'published_at': datetime.fromisoformat(
                            snippet['publishedAt'].replace('Z', '+00:00')
                        ),
                        'duration': 0,
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'thumbnail_url': snippet['thumbnails']['high']['url'] 
                            if 'high' in snippet['thumbnails'] 
                            else snippet['thumbnails']['default']['url'],
                        'url': f"https://www.youtube.com/watch?v={video['id']}"
                    })
            
            logger.info(f"Fetched {len(videos)} videos from {channel_name}")
            
        except Exception as e:
            logger.error(f"Error fetching channel {channel_id}: {e}")
        
        return videos
    
    def fetch_all_content(self):
        """Fetch from both channels and search"""
        all_videos = []
        
        from config import Config
        
        if Config.LLM_CHANNELS:
            logger.info("Fetching from monitored channels...")
            for channel_id, channel_name in Config.LLM_CHANNELS.items():
                logger.info(f"Fetching from {channel_name}...")
                try:
                    videos = self.fetch_channel_videos(channel_id, Config.MAX_VIDEOS_PER_CHANNEL)
                    all_videos.extend(videos)
                    logger.info(f"Got {len(videos)} videos from {channel_name}")
                except Exception as e:
                    logger.error(f"Failed to fetch {channel_name}: {e}")
        
        if self.use_search and self.search_queries:
            logger.info("Searching for LLM content...")
            for query in self.search_queries:
                try:
                    videos = self.search_llm_videos(query, Config.MAX_SEARCH_RESULTS)
                    all_videos.extend(videos)
                    logger.info(f"Found {len(videos)} videos for: {query}")
                except Exception as e:
                    logger.error(f"Search failed for '{query}': {e}")
        
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                unique_videos.append(video)
        
        logger.info(f"Total unique videos: {len(unique_videos)}")
        return unique_videos
