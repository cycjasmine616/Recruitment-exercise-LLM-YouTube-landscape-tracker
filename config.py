import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'

    LLM_CHANNELS = {
        'UCSHZKyawb77ixDdsGog4iWA': 'Andrej Karpathy',
        
        'UCiT9RITQ9PW6BhXK0y2jaeg': 'AI Explained',
        
        'UCyo49Wx3XWqZzU2V5jqJ5zg': 'Matthew Berman',
        
        'UCM3q5wX6RJ4p2FwjP6qW6Kg': 'Sam Witteveen',
    }
    
    SEARCH_QUERIES = [
        "large language model tutorial transcript",
        "transformer attention mechanism explained",
        "GPT fine-tuning guide 2024",
        "RAG retrieval augmented generation explained",
        "prompt engineering techniques deep dive"
    ]
    
    MAX_VIDEOS_PER_CHANNEL = 5
    MAX_SEARCH_RESULTS = 5
