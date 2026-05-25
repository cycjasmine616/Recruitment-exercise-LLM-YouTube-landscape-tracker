import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YouTubeFetcher:
    def __init__(self):
        from config import Config
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def search_llm_videos(self, query, max_results=5):
        """Search YouTube for LLM-related videos"""
        videos = []
        
        try:
            logger.info(f"Searching: '{query}'")
            
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'relevanceLanguage': 'en',
                'order': 'relevance',
                'key': self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/search", 
                params=search_params, 
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code}")
                return videos
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"API Error: {data['error'].get('message', '')}")
                return videos
            
            video_ids = []
            for item in data.get('items', []):
                if 'id' in item and 'videoId' in item['id']:
                    video_ids.append(item['id']['videoId'])
            
            if not video_ids:
                logger.warning(f"No videos found for: {query}")
                return videos
            
            details_params = {
                'part': 'snippet,statistics',
                'id': ','.join(video_ids),
                'key': self.api_key
            }
            
            details_response = requests.get(
                f"{self.base_url}/videos",
                params=details_params,
                timeout=10
            )
            
            if details_response.status_code != 200:
                return videos
            
            details_data = details_response.json()
            
            for video in details_data.get('items', []):
                snippet = video['snippet']
                stats = video.get('statistics', {})
                
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = ''
                if 'high' in thumbnails:
                    thumbnail_url = thumbnails['high']['url']
                elif 'medium' in thumbnails:
                    thumbnail_url = thumbnails['medium']['url']
                elif 'default' in thumbnails:
                    thumbnail_url = thumbnails['default']['url']
                
                video_obj = {
                    'id': video['id'],
                    'title': snippet['title'],
                    'description': snippet.get('description', ''),
                    'channel_id': snippet['channelId'],
                    'channel_name': snippet['channelTitle'],
                    'published_at': datetime.fromisoformat(
                        snippet['publishedAt'].replace('Z', '+00:00')
                    ),
                    'duration': 0,
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'thumbnail_url': thumbnail_url,
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                
                videos.append(video_obj)
                logger.info(f"  ✓ {snippet['title'][:60]}")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
        
        return videos
    
    def fetch_all_videos(self):
        """Fetch videos from all search queries"""
        from config import Config
        
        all_videos = []
        
        for query in Config.SEARCH_QUERIES:
            try:
                videos = self.search_llm_videos(query, Config.MAX_SEARCH_RESULTS)
                all_videos.extend(videos)
            except Exception as e:
                logger.error(f"Failed for '{query}': {e}")
                continue
        
        seen_ids = set()
        unique_videos = []
        for v in all_videos:
            if v['id'] not in seen_ids:
                seen_ids.add(v['id'])
                unique_videos.append(v)
        
        logger.info(f"Total unique videos: {len(unique_videos)}")
        return unique_videos
