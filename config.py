import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'
    
    LLM_CHANNELS = {
        'UCrD0BP5oU6PRAkSrxoQfP7A': 'AI Explained',
        'UCWN3xxRkmTPmbKwht9FuE5A': 'Two Minute Papers',
    }
    
    UPDATE_INTERVAL_HOURS = 12
    MAX_VIDEOS_PER_CHANNEL = 5
