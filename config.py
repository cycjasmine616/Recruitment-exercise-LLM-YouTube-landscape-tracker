import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'
    
    SEARCH_QUERIES = [
        "large language model explained 2024",
        "GPT-4 tutorial how to",
        "LLM fine-tuning guide",
        "RAG retrieval augmented generation",
        "prompt engineering tutorial",
        "Llama 3 model review",
        "Mistral AI explained",
        "Claude AI vs GPT comparison",
        "AI agents tutorial langchain",
        "open source LLM 2024"
    ]
    
    MAX_SEARCH_RESULTS = 5
