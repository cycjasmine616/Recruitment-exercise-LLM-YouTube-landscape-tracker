import logging
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
import torch
import json
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceAnalyzer:
    def __init__(self):
        logger.info("Initializing Hugging Face models...")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        try:
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1,
                max_length=150,
                min_length=30
            )
            logger.info("Summarization model loaded")
        except:
            logger.warning("Failed to load BART, using smaller model")
            self.summarizer = pipeline(
                "summarization",
                model="google/pegasus-xsum",
                device=-1,
                max_length=150,
                min_length=30
            )
        
        try:
            self.zero_shot = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Zero-shot classification model loaded")
        except:
            logger.warning("Using smaller classification model")
            self.zero_shot = pipeline(
                "zero-shot-classification",
                model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
                device=-1
            )
        
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Sentence transformer loaded")
        
        self.keyword_model = KeyBERT(model=self.sentence_model)
        logger.info("KeyBERT model loaded")
        
        self.llm_topics = [
            "model architecture and design",
            "training techniques and methodologies",
            "fine-tuning and transfer learning",
            "prompt engineering and optimization",
            "retrieval augmented generation (RAG)",
            "model evaluation and testing",
            "safety and alignment",
            "multimodal models and capabilities",
            "open source vs closed source models",
            "deployment and production",
            "benchmarks and performance",
            "ethics and bias in AI",
            "tool use and agents",
            "code generation and programming",
            "future trends and predictions"
        ]
    
    def generate_summary(self, transcript, max_length=150):
        if not transcript:
            return "No transcript available"
        
        try:
            if len(transcript) > 1024:
                chunks = self._split_text(transcript, 800)
                summaries = []
                
                for chunk in chunks[:3]: 
                    if len(chunk) > 50:
                        summary = self.summarizer(chunk, max_length=max_length//3, 
                                                min_length=20, do_sample=False)
                        summaries.append(summary[0]['summary_text'])
                
                combined_summary = " ".join(summaries)
                
                if len(combined_summary) > 100:
                    final_summary = self.summarizer(combined_summary, max_length=max_length,
                                                  min_length=50, do_sample=False)
                    return final_summary[0]['summary_text']
                
                return combined_summary[:max_length]
            else:
                summary = self.summarizer(transcript, max_length=max_length,
                                        min_length=30, do_sample=False)
                return summary[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._extractive_summary(transcript)
    
    def _extractive_summary(self, text, num_sentences=3):
        try:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) <= num_sentences:
                return text[:500]
            
            sentence_embeddings = self.sentence_model.encode(sentences)
            
            similarity_matrix = cosine_similarity(sentence_embeddings)
            scores = np.sum(similarity_matrix, axis=1)
            
            ranked_sentences = [sentences[i] for i in np.argsort(scores)[-num_sentences:]]
            
            return " ".join(ranked_sentences)[:500]
        except Exception as e:
            logger.error(f"Extractive summary failed: {e}")
            return text[:500] + "..."
    
    def classify_topics(self, transcript, title, description):
        if not transcript and not description:
            return []
        
        text = f"{title}. {description[:500]}"
        if transcript:
            text += f" {transcript[:1000]}"
        
        if len(text) < 50:
            return []
        
        try:
            result = self.zero_shot(
                text,
                candidate_labels=self.llm_topics,
                multi_label=True
            )
            
            topics = []
            for label, score in zip(result['labels'], result['scores']):
                if score > 0.3:  
                    topic_name = label.replace(" and ", " & ").title()
                    topics.append({
                        'topic': topic_name,
                        'confidence': round(float(score), 3)
                    })
            
            topics.sort(key=lambda x: x['confidence'], reverse=True)
            
            return topics[:5] 
            
        except Exception as e:
            logger.error(f"Error classifying topics: {e}")
            return self._keyword_classification(text)
    
    def _keyword_classification(self, text):
        topic_keywords = {
            "Model Architecture": ["architecture", "transformer", "attention", "layer", "parameter", "neural network"],
            "Training Techniques": ["training", "optimization", "gradient", "loss function", "backpropagation"],
            "Fine-Tuning": ["fine-tuning", "transfer learning", "pre-trained", "adaptation"],
            "Prompt Engineering": ["prompt", "few-shot", "zero-shot", "instruction", "template"],
            "RAG Systems": ["RAG", "retrieval", "augmented", "knowledge base", "vector database"],
            "Model Evaluation": ["evaluation", "benchmark", "metric", "accuracy", "performance"],
            "Safety & Alignment": ["safety", "alignment", "harmful", "bias", "fairness", "ethical"],
            "Multimodal Models": ["multimodal", "vision", "image", "audio", "video understanding"],
            "Open Source Models": ["open source", "Llama", "Mistral", "Falcon", "community"],
            "Deployment": ["deployment", "production", "serving", "inference", "API"],
            "Code Generation": ["code", "programming", "GitHub", "Copilot", "developer"]
        }
        
        text_lower = text.lower()
        matched_topics = []
        
        for topic, keywords in topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            if score > 0:
                confidence = min(score / len(keywords) * 2, 0.95)
                matched_topics.append({
                    'topic': topic,
                    'confidence': confidence
                })
        
        return sorted(matched_topics, key=lambda x: x['confidence'], reverse=True)[:5]
    
    def extract_key_insights(self, transcript, summary):
        if not transcript:
            return "No insights available"
        
        try:
            keywords = self.keyword_model.extract_keywords(
                transcript,
                keyphrase_ngram_range=(1, 3),
                stop_words='english',
                top_n=10
            )
            
            sentences = re.split(r'(?<=[.!?])\s+', transcript)
            important_sentences = []
            
            for sentence in sentences:
                for keyword, score in keywords:
                    if keyword.lower() in sentence.lower() and len(sentence) > 30:
                        important_sentences.append({
                            'sentence': sentence.strip(),
                            'keyword': keyword,
                            'score': score
                        })
            
            seen = set()
            unique_insights = []
            for item in sorted(important_sentences, key=lambda x: x['score'], reverse=True):
                if item['sentence'] not in seen:
                    seen.add(item['sentence'])
                    unique_insights.append(f"• {item['sentence']}")
            
            if not unique_insights:
                return "• " + "\n• ".join(sentences[:3])
            
            return "\n".join(unique_insights[:5]) 
            
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            sentences = re.split(r'(?<=[.!?])\s+', transcript)
            return "• " + "\n• ".join(sentences[:3])
    
    def calculate_channel_similarity(self, videos1, videos2):
        if not videos1 or not videos2:
            return 0.0
        
        try:
            texts1 = []
            for video in videos1:
                text = f"{video.title} {video.description or ''}"
                texts1.append(text[:500])
            
            texts2 = []
            for video in videos2:
                text = f"{video.title} {video.description or ''}"
                texts2.append(text[:500])
            
            if not texts1 or not texts2:
                return 0.0
            
            embeddings1 = self.sentence_model.encode(texts1)
            embeddings2 = self.sentence_model.encode(texts2)
            
            centroid1 = np.mean(embeddings1, axis=0)
            centroid2 = np.mean(embeddings2, axis=0)
            
            similarity = cosine_similarity([centroid1], [centroid2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating channel similarity: {e}")
            return 0.0
    
    def _split_text(self, text, chunk_size):
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
