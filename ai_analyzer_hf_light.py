import logging
import re
import json

logger = logging.getLogger(__name__)

class LightweightAnalyzer:
    def __init__(self):
        logger.info("Initializing lightweight analyzer")
        
        self.topic_keywords = {
            "Model Architecture": ["architecture", "transformer", "attention mechanism", "neural network", "layers", "parameters"],
            "Training & Fine-tuning": ["training", "fine-tuning", "RLHF", "reinforcement learning", "pre-training", "supervised fine-tuning"],
            "Prompt Engineering": ["prompt", "few-shot", "zero-shot", "chain of thought", "instruction", "system prompt"],
            "RAG Systems": ["RAG", "retrieval augmented", "vector database", "embeddings", "knowledge retrieval", "semantic search"],
            "Model Evaluation": ["benchmark", "evaluation", "accuracy", "performance", "MMLU", "HumanEval", "test results"],
            "Safety & Alignment": ["safety", "alignment", "bias", "fairness", "ethical", "responsible AI", "guardrails"],
            "Open Source vs Closed": ["open source", "proprietary", "Llama", "Mistral", "GPT-4", "Claude", "Gemini", "released"],
            "Code Generation": ["code", "programming", "developer", "GitHub Copilot", "software development", "debugging"],
            "AI Agents": ["agent", "autonomous", "LangChain", "tool use", "function calling", "AutoGPT", "planning"],
            "Multimodal": ["multimodal", "vision", "image", "video", "audio", "visual understanding"],
        }
    
    def generate_summary(self, text, max_length=300):
        """Generate extractive summary"""
        if not text or len(text) < 100:
            return text or "No content available"
        
        try:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
            
            if len(sentences) <= 3:
                return ' '.join(sentences)[:max_length]

            scored = []
            for i, sent in enumerate(sentences):
                score = len(sent) 
                if i == 0 or i == len(sentences) - 1:
                    score *= 1.5
                scored.append((score, sent))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            top_sentences = [s[1] for s in scored[:4]]
            
            original_order = sorted(
                [(sentences.index(s), s) for s in top_sentences],
                key=lambda x: x[0]
            )
            
            summary = ' '.join([s[1] for s in original_order])
            return summary[:max_length]
            
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return text[:max_length]
    
    def classify_topics(self, transcript, title, description):
        """Classify video into LLM topics"""
        text = f"{title} {description} {transcript or ''}".lower()
        
        matched_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            
            if score > 0:
                confidence = min(score / len(keywords) * 1.5, 0.95)
                matched_topics.append({
                    'topic': topic,
                    'confidence': round(confidence, 3)
                })
        
        matched_topics.sort(key=lambda x: x['confidence'], reverse=True)
        
        if matched_topics:
            return matched_topics[:5]
        else:
            return [{'topic': 'LLM Discussion', 'confidence': 0.7}]
    
    def extract_key_insights(self, transcript, summary):
        """Extract key insights from transcript"""
        if not transcript:
            return "• See video description for details"
        
        important_terms = [
            'important', 'key', 'critical', 'essential', 'fundamental',
            'breakthrough', 'significant', 'notable', 'remarkable',
            'new', 'novel', 'state-of-the-art', 'best',
            'we found', 'results show', 'demonstrate', 'prove',
            'future', 'next generation', 'coming soon'
        ]
        
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        important_sentences = []
        
        for sentence in sentences:
            if len(sentence) < 30:
                continue
            
            sentence_lower = sentence.lower()
            score = sum(1 for term in important_terms if term in sentence_lower)
            
            if score > 0:
                important_sentences.append(sentence.strip())
        
        if important_sentences:
            return '\n'.join([f"• {s}" for s in important_sentences[:5]])
        else:
            substantial = [s.strip() for s in sentences if len(s.strip()) > 40]
            return '\n'.join([f"• {s}" for s in substantial[:3]])
