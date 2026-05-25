import os

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    DATABASE_URL = 'sqlite:///data/youtube_tracker.db'
    
    LLM_CHANNELS = {
        'UCSHZKyawb77ixDdsGog4iWA': 'Andrej Karpathy',
        
        'UC2vXPoFhVpIb3xMPAKaBAnA': 'Yannic Kilcher',
        
        'UCMLtBahI5DMrt0Jvx6LwQwg': 'Machine Learning Street Talk',
        
        'UCiT9RITQ9PW6BhXK0y2jaeg': 'AI Explained',
        
        'UC2KfmR-Y2nSBeH1zV8JHQxA': 'Prompt Engineering',
    }
    
    LLM_TOPICS = [
        "Transformer Architecture & Attention Mechanisms",
        "GPT Models & Capabilities",
        "LLM Training & Fine-tuning",
        "RLHF & Alignment",
        "Prompt Engineering Techniques",
        "Retrieval Augmented Generation (RAG)",
        "Model Evaluation & Benchmarks",
        "Open Source vs Proprietary LLMs",
        "LLM Safety & Ethics",
        "AI Agents & Tool Use",
        "Multimodal LLMs",
        "LLM Deployment & Scaling"
    ]
    
    MAX_VIDEOS_PER_CHANNEL = 8
    UPDATE_INTERVAL_HOURS = 12
