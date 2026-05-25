def search_llm_videos(self, query, max_results=5):
    """Search for LLM-related videos"""
    videos = []
    try:
        import requests
        
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
        
        if 'error' in response:
            logger.error(f"API Error: {response['error'].get('message', 'Unknown error')}")
            return videos
        
        video_ids = []
        for item in response.get('items', []):
            if 'id' in item and 'videoId' in item['id']:
                video_ids.append(item['id']['videoId'])
        
        if not video_ids:
            logger.warning(f"No videos found for query: {query}")
            return videos
        
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
            
            videos.append({
                'id': video['id'],
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_name': snippet['channelTitle'],
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
        
        logger.info(f"Found {len(videos)} videos for: {query}")
        
    except Exception as e:
        logger.error(f"Search error: {e}")
    
    return videos
