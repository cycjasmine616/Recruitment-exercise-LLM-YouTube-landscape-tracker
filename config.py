import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'
    
    LLM_CHANNELS = {
        'UCSHZKyawb77ixDdsGog4iWA': 'Andrej Karpathy',
        
        'UC2vXPoFhVpIb3xMPAKaBAnA': 'Yannic Kilcher',
        
        'UCMLtBahI5DMrt0Jvx6LwQwg': 'Machine Learning Street Talk',
        
        'UCiT9RITQ9PW6BhXK0y2jaeg': 'AI Explained',
        
        'UCHtQ8aGzXzj6B-0BZ0n1BXA': 'Nicholas Renotte',
    }
    
    USE_SEARCH = True  
    SEARCH_QUERIES = [
        "large language model explained 2024",
        "GPT-4 tutorial how to use",
        "LLM fine-tuning guide",
        "RAG retrieval augmented generation",
        "prompt engineering tutorial",
        "Llama 3 model review",
        "Mistral AI explained",
        "Claude AI tutorial",
        "open source LLM comparison 2024",
        "AI agents tutorial langchain"
    ]
    
    UPDATE_INTERVAL_HOURS = 12
    MAX_VIDEOS_PER_CHANNEL = 5
    MAX_SEARCH_RESULTS = 5 
