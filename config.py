import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your-api-key-here')
    
    USE_HUGGINGFACE = True
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///youtube_tracker.db')
    
    LLM_CHANNELS = {
        'UCrD0BP5oU6PRAkSrxoQfP7A': 'AI Explained',
        'UCWN3xxRkmTPmbKwht9FuE5A': 'Two Minute Papers',
        'UCvKRFNawVcuz4b9ihUTApCg': 'Yannic Kilcher',
        'UCsBjURrPvezykJAnEr0sOmQ': 'Machine Learning Street Talk',
        'UC0rqucBdTuFTjJiefW5t-IQ': 'Andrej Karpathy',
        'UCSHZKyawb77ixDdsGog4iWA': 'Lex Fridman',
        'UCbfYPyITQ-7l4upoX8nvctg': 'Nicholas Renotte',
        'UCmOwsoHty5PrmE-3QhQeR-A': 'AssemblyAI',
        'UCHB9VepY6kYvZjj0Bgxnpbw': 'Data with Zablo',
        'UCzM-7kX5n5z_1xO8oQ9zL6g': 'Prompt Engineering'
    }
    
    UPDATE_INTERVAL_HOURS = 6
    
    MAX_VIDEOS_PER_CHANNEL = 50
