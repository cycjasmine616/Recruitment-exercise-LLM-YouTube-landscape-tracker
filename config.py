import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'
    
    LLM_CHANNELS = {
        'UCSHZKyawb77ixDdsGog4iWA': 'Andrej Karpathy',
    }
    
    USE_SEARCH = True
    LLM_SEARCH_QUERIES = [
        "Andrej Karpathy LLM tutorial",
        "large language model deep dive",
        "transformer architecture explained",
        "GPT model training explained"
    ]
    
    MAX_VIDEOS_PER_CHANNEL = 3
    MAX_SEARCH_RESULTS = 3
