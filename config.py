import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'
    
    LLM_CHANNELS = {
        'UCSHZKyawb77ixDdsGog4iWA': 'Lex Fridman',
        
        'UCfdQGKElLZjB1UFCx2G2hDw': 'AI Explained',
        
        'UC2vXPoFhVpIb3xMPAKaBAnA': 'Yannic Kilcher',
        
        'UCMLtBahI5DMrt0Jvx6LwQwg': 'Machine Learning Street Talk',
        
        'UCXUPKbNHQVp8eJxRqk7Zq3A': 'Andrej Karpathy',
        
        'UCHtQ8aGzXzj6B-0BZ0n1BXA': 'Nicholas Renotte',
        
        'UCtatfZMf-8EkIwASXM4ts0A': 'AssemblyAI',
        
        'UCiT9RITQ9PW6BhXK0y2jaeg': 'Data with Zablo',
        
        'UC2KfmR-Y2nSBeH1zV8JHQxA': 'Prompt Engineering',
        
        'UC1KqLiF9G5Y7B16sVkNJ2BQ': 'AI Jason',
    }
    USE_SEARCH = True  
    SEARCH_QUERIES = [
        "large language model tutorial",
        "GPT-4 explained",
        "LLM fine-tuning guide",
        "RAG system tutorial",
        "prompt engineering 2024",
        "open source LLM review",
        "Claude AI explained",
        "LLaMA model tutorial",
        "Mistral AI review",
        "AI agent tutorial"
    ]
    
    UPDATE_INTERVAL_HOURS = 12
    MAX_VIDEOS_PER_CHANNEL = 10
    MAX_SEARCH_RESULTS = 20
