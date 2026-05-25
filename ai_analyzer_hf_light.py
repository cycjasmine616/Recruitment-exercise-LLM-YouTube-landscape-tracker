import logging
import re
import json

logger = logging.getLogger(__name__)

class LightweightAnalyzer:
    def __init__(self):
        logger.info("Initializing analyzer")
        self.topics_map = {
            "Model Architecture": ["architecture", "transformer", "attention", "neural network", "layer"],
            "Training Techniques": ["training", "fine-tuning", "RLHF", "optimization", "gradient"],
            "Prompt Engineering": ["prompt", "few-shot", "zero-shot", "chain of thought"],
            "RAG Systems": ["RAG", "retrieval", "vector database", "embeddings"],
            "Model Evaluation": ["benchmark", "evaluation", "metric", "accuracy", "performance"],
            "Safety & Alignment": ["safety", "alignment", "bias", "fairness", "ethical"],
            "Open Source vs Closed": ["open source", "proprietary", "Llama", "Mistral", "GPT"],
            "Code Generation": ["code", "programming", "Copilot", "developer"],
        }
    
    def generate_summary(self, text, max_length=500):
        if not text or len(text) < 100:
            return text or "No content"
        sentences = re.split(r'(?<=[.!?])\s+', text)
        important = [s for s in sentences if len(s) > 40]
        return ' '.join(important[:3])[:max_length]
    
    def classify_topics(self, transcript, title, description):
        text = f"{title} {description} {transcript or ''}".lower()
        topics = []
        
        for topic, keywords in self.topics_map.items():
            score = sum(1 for k in keywords if k.lower() in text)
            if score > 0:
                topics.append({
                    'topic': topic,
                    'confidence': min(score / len(keywords), 0.95)
                })
        
        return sorted(topics, key=lambda x: x['confidence'], reverse=True)[:5]
    
    def extract_key_insights(self, transcript, summary):
        if not transcript:
            return "No insights"
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        key_words = ['important', 'key', 'significant', 'breakthrough', 'new']
        insights = [s for s in sentences if any(k in s.lower() for k in key_words) and len(s) > 30]
        if not insights:
            insights = sentences[:3]
        return '\n'.join([f"• {s}" for s in insights[:5]])
