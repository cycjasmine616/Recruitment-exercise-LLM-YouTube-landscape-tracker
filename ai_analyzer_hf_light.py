import logging
import re
import json

logger = logging.getLogger(__name__)

class LightweightAnalyzer:
    def __init__(self):
        logger.info("Initializing LLM content analyzer")
        
        self.llm_topic_patterns = {
            "Transformer Architecture": {
                "keywords": ["transformer", "attention mechanism", "self-attention", "multi-head", "encoder", "decoder", "positional encoding"],
                "context_patterns": [r"transformer (architecture|model)", r"attention (mechanism|layer|head)", r"self.attention"]
            },
            "GPT Models": {
                "keywords": ["GPT-4", "GPT-3", "ChatGPT", "GPT model", "generative pre-trained"],
                "context_patterns": [r"GPT.?\d", r"chat.?gpt", r"generative pre.trained"]
            },
            "LLM Training": {
                "keywords": ["pre-training", "fine-tuning", "RLHF", "reinforcement learning", "supervised fine-tuning", "training data", "compute"],
                "context_patterns": [r"(pre.train|fine.tun|RLHF|reinforcement learning)", r"training (data|corpus|dataset)"]
            },
            "Prompt Engineering": {
                "keywords": ["prompt", "few-shot", "zero-shot", "chain of thought", "system message", "instruction tuning"],
                "context_patterns": [r"(few.shot|zero.shot|chain.of.thought)", r"prompt (engineering|design|technique)"]
            },
            "RAG Systems": {
                "keywords": ["RAG", "retrieval augmented", "vector database", "embeddings", "knowledge base", "semantic search"],
                "context_patterns": [r"retrieval.augmented", r"vector (database|store|search)", r"RAG (system|pipeline)"]
            },
            "Model Evaluation": {
                "keywords": ["benchmark", "MMLU", "HumanEval", "evaluation", "performance", "accuracy", "comparison"],
                "context_patterns": [r"(benchmark|evaluat|test) (result|score|performance)", r"MMLU|HumanEval|GSM8K"]
            },
            "LLM Safety": {
                "keywords": ["safety", "alignment", "bias", "fairness", "harmful", "jailbreak", "red team", "guardrails"],
                "context_patterns": [r"(safety|alignment|bias|fairness) (concern|issue|problem)", r"red.team|jailbreak|guardrail"]
            },
            "Open Source LLMs": {
                "keywords": ["open source", "Llama", "Mistral", "Falcon", "open model", "weights released", "community"],
                "context_patterns": [r"(open.source|open.model|open.weight)", r"(Llama|Mistral|Falcon|Gemma) model"]
            },
            "AI Agents": {
                "keywords": ["agent", "autonomous", "tool use", "function calling", "LangChain", "AutoGPT", "planning"],
                "context_patterns": [r"(AI|autonomous|intelligent) agent", r"(tool.use|function.call|plugin)"]
            },
            "Multimodal LLMs": {
                "keywords": ["multimodal", "vision", "image understanding", "visual", "audio processing", "Gemini"],
                "context_patterns": [r"(vision|image|visual) (model|understanding|capability)", r"multi.modal"]
            }
        }
    
    def analyze_transcript_deep(self, transcript, title, description):
        """Deep analysis of transcript for LLM content"""
        
        if not transcript:
            return self._analyze_from_description(title, description)
        
        llm_segments = self._extract_llm_segments(transcript)
        
        topics_discussed = self._identify_topics_in_content(transcript)
        
        transcript_excerpts = self._extract_key_quotes(transcript)
        
        technical_depth = self._assess_technical_depth(transcript)
        
        creator_stance = self._extract_creator_stance(transcript)
        
        key_claims = self._extract_claims(transcript)
        
        practical_insights = self._extract_practical_insights(transcript)
        
        return {
            'topics_discussed': topics_discussed,
            'transcript_excerpts': transcript_excerpts,
            'technical_depth': technical_depth,
            'creator_stance': creator_stance,
            'key_claims': key_claims,
            'practical_insights': practical_insights
        }
    
    def _extract_llm_segments(self, transcript):
        """Extract portions of transcript that discuss LLMs"""
        llm_indicators = [
            'language model', 'LLM', 'GPT', 'transformer', 'attention',
            'fine-tuning', 'prompt', 'RAG', 'embedding', 'token',
            'ChatGPT', 'Claude', 'Llama', 'Mistral', 'Gemini'
        ]
        
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        llm_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator.lower() in sentence_lower for indicator in llm_indicators):
                llm_sentences.append(sentence.strip())
        
        return llm_sentences
    
    def _identify_topics_in_content(self, transcript):
        """Identify which LLM topics are actually discussed"""
        topics_found = []
        transcript_lower = transcript.lower()
        
        for topic, patterns in self.llm_topic_patterns.items():
            keyword_matches = 0
            context_matches = 0
            
            for keyword in patterns['keywords']:
                if keyword.lower() in transcript_lower:
                    keyword_matches += 1
            
            for pattern in patterns['context_patterns']:
                if re.search(pattern, transcript_lower):
                    context_matches += 1
            
            total_score = keyword_matches + (context_matches * 2)
            
            if total_score >= 2: 
                topics_found.append({
                    'topic': topic,
                    'relevance_score': min(total_score / 10, 0.95),
                    'keyword_matches': keyword_matches,
                    'context_matches': context_matches
                })
        
        return sorted(topics_found, key=lambda x: x['relevance_score'], reverse=True)
    
    def _extract_key_quotes(self, transcript):
        """Extract direct quotes about LLMs"""
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        quotes = []
        
        quote_indicators = [
            r'\b(important|key|crucial|essential|fundamental)\b',
            r'\b(breakthrough|revolutionary|game.changing)\b',
            r'\b(I think|I believe|in my opinion|my view)\b',
            r'\b(the thing is|the key is|what matters is)\b',
            r'\b(surprising|interesting|fascinating|remarkable)\b'
        ]
        
        for sentence in sentences:
            if len(sentence) < 50 or len(sentence) > 300:
                continue
            
            importance_score = sum(1 for pattern in quote_indicators if re.search(pattern, sentence, re.IGNORECASE))
            
            if importance_score >= 1:
                quotes.append({
                    'text': sentence.strip(),
                    'importance': importance_score
                })
        
        return sorted(quotes, key=lambda x: x['importance'], reverse=True)[:5]
    
    def _assess_technical_depth(self, transcript):
        transcript_lower = transcript.lower()
        
        beginner_terms = ['basics', 'introduction', 'beginner', 'simple', 'overview', 'what is']
        intermediate_terms = ['architecture', 'training', 'fine-tuning', 'implementation', 'code']
        advanced_terms = ['attention mechanism', 'gradient', 'loss function', 'RLHF', 'PPO', 'latent space']
        
        beginner_score = sum(1 for term in beginner_terms if term in transcript_lower)
        intermediate_score = sum(1 for term in intermediate_terms if term in transcript_lower)
        advanced_score = sum(1 for term in advanced_terms if term in transcript_lower)
        
        if advanced_score > intermediate_score and advanced_score > beginner_score:
            return "Advanced"
        elif intermediate_score > beginner_score:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _extract_creator_stance(self, transcript):
        stance_indicators = {
            'positive': ['powerful', 'impressive', 'amazing', 'breakthrough', 'revolutionary', 'great', 'excellent'],
            'cautious': ['concern', 'worry', 'careful', 'limitation', 'challenge', 'problem', 'issue'],
            'critical': ['overhyped', 'not ready', 'dangerous', 'risk', 'threat', 'failure', 'wrong']
        }
        
        transcript_lower = transcript.lower()
        scores = {}
        
        for stance, words in stance_indicators.items():
            scores[stance] = sum(1 for word in words if word in transcript_lower)
        
        if not scores:
            return "Neutral/Informational"
        
        dominant_stance = max(scores, key=scores.get)
        
        if scores[dominant_stance] == 0:
            return "Neutral/Informational"
        
        return f"Mostly {dominant_stance.title()}"
    
    def _extract_claims(self, transcript):
        """Extract specific claims made about LLMs"""
        claim_patterns = [
            r'(LLMs?|GPT|models?|transformers?)\s+(can|cannot|will|won\'t|are|aren\'t)\s+(\w+\s?){3,15}',
            r'(better than|worse than|superior|inferior|outperform)',
            r'(in the future|next year|by \d{4}|soon|eventually)',
            r'(according to|research shows|studies show|paper|benchmark)'
        ]
        
        claims = []
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        
        for sentence in sentences:
            for pattern in claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence.strip())
                    break
        
        return claims[:5]
    
    def _extract_practical_insights(self, transcript):
        """Extract actionable insights about LLMs"""
        insight_indicators = [
            r'(you can|you should|we can|we should|try|use|implement)',
            r'(tip|trick|technique|method|approach|strategy)',
            r'(best practice|recommendation|suggestion|advice)',
            r'(here\'s how|how to|step|guide|tutorial)'
        ]
        
        insights = []
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        
        for sentence in sentences:
            if len(sentence) < 50:
                continue
            for pattern in insight_indicators:
                if re.search(pattern, sentence, re.IGNORECASE):
                    insights.append(sentence.strip())
                    break
        
        return ' '.join(insights[:3]) if insights else "No specific practical insights identified"
    
    def _analyze_from_description(self, title, description):
        """Fallback analysis using only title and description"""
        text = f"{title} {description}"
        
        topics = self._identify_topics_in_content(text)
        
        return {
            'topics_discussed': topics,
            'transcript_excerpts': [],
            'technical_depth': "Unknown (no transcript)",
            'creator_stance': "Unknown (no transcript)",
            'key_claims': [],
            'practical_insights': description[:300] if description else "No description available"
        }
    
    def calculate_channel_relationships(self, channel_videos):
        """Calculate how channels relate to each other on LLM themes"""
        relationships = []
        
        channel_ids = list(channel_videos.keys())
        
        for i, ch1 in enumerate(channel_ids):
            for ch2 in channel_ids[i+1:]:
                videos1 = channel_videos[ch1]
                videos2 = channel_videos[ch2]
                
                if not videos1 or not videos2:
                    continue
                
                topics1 = set()
                topics2 = set()
                
                for v in videos1:
                    if v.llm_topics_discussed:
                        t = json.loads(v.llm_topics_discussed) if isinstance(v.llm_topics_discussed, str) else v.llm_topics_discussed
                        topics1.update([topic['topic'] for topic in t])
                
                for v in videos2:
                    if v.llm_topics_discussed:
                        t = json.loads(v.llm_topics_discussed) if isinstance(v.llm_topics_discussed, str) else v.llm_topics_discussed
                        topics2.update([topic['topic'] for topic in t])
                
                if not topics1 or not topics2:
                    continue
                
                common = topics1 & topics2
                all_topics = topics1 | topics2
                similarity = len(common) / len(all_topics) if all_topics else 0
                
                if similarity > 0.2:
                    relationships.append({
                        'channel_1': videos1[0].channel_name if videos1 else ch1,
                        'channel_2': videos2[0].channel_name if videos2 else ch2,
                        'similarity_score': round(similarity, 3),
                        'common_topics': list(common),
                        'description': f"Both channels cover {len(common)} common LLM topics including: {', '.join(list(common)[:3])}"
                    })
        
        return sorted(relationships, key=lambda x: x['similarity_score'], reverse=True)
