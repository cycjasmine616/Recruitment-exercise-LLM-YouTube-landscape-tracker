import logging
import re
import json

logger = logging.getLogger(__name__)

class LightweightAnalyzer:
    def __init__(self):
        logger.info("Initializing transcript analyzer")
        
        self.llm_indicators = [
            'language model', 'LLM', 'GPT', 'transformer', 'attention',
            'fine-tuning', 'prompt', 'RAG', 'embedding', 'token',
            'ChatGPT', 'Claude', 'Llama', 'Mistral', 'Gemini',
            'neural network', 'deep learning', 'pre-training',
            'reinforcement learning', 'RLHF', 'alignment'
        ]
        
        self.topic_patterns = {
            "Transformer Architecture": r'(transformer|attention|encoder|decoder|self-attention|multi-head)',
            "Model Training": r'(training|fine-tuning|pre-training|RLHF|supervised|loss function|gradient)',
            "Prompt Engineering": r'(prompt|few-shot|zero-shot|chain.of.thought|system message|instruction)',
            "RAG Systems": r'(RAG|retrieval|vector database|embeddings|knowledge base|semantic search)',
            "Model Evaluation": r'(benchmark|evaluation|MMLU|HumanEval|performance|accuracy|compar)',
            "Safety & Ethics": r'(safety|alignment|bias|fairness|ethical|harmful|guardrail|red.team)',
            "Open Source LLMs": r'(open source|Llama|Mistral|Falcon|open model|community|released)',
            "AI Agents": r'(agent|autonomous|tool use|function call|LangChain|AutoGPT|planning)',
            "Multimodal": r'(multimodal|vision|image|visual|Gemini|GPT-4V|audio)',
            "LLM Applications": r'(chatbot|assistant|copilot|code generation|summarization|translation)'
        }
    
    def analyze_transcript(self, transcript, title, description):
        """Analyze what the creator actually says about LLMs"""
        
        if not transcript:
            return self._fallback_analysis(title, description)
        
        llm_sentences = self._extract_llm_content(transcript)
        
        topics = self._categorize_topics(transcript)
        
        key_quotes = self._extract_key_quotes(llm_sentences)
        
        summary = self._summarize_llm_points(llm_sentences, title)
        
        return {
            'topics': topics,
            'key_quotes': key_quotes,
            'summary': summary,
            'has_transcript': True
        }
    
    def _extract_llm_content(self, transcript):
        """Extract sentences that discuss LLMs"""
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        llm_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.llm_indicators:
                if indicator.lower() in sentence_lower:
                    llm_sentences.append(sentence.strip())
                    break
        
        return llm_sentences
    
    def _categorize_topics(self, transcript):
        """Categorize what LLM topics are discussed"""
        transcript_lower = transcript.lower()
        matched_topics = []
        
        for topic, pattern in self.topic_patterns.items():
            matches = re.findall(pattern, transcript_lower)
            if len(matches) >= 2: 
                matched_topics.append({
                    'topic': topic,
                    'mentions': len(matches)
                })
        
        matched_topics.sort(key=lambda x: x['mentions'], reverse=True)
        return matched_topics[:5]
    
    def _extract_key_quotes(self, llm_sentences):
        """Extract the most important things said about LLMs"""
        quotes = []
        
        opinion_patterns = [
            r'(I think|I believe|in my opinion|the key is|importantly|what matters)',
            r'(breakthrough|revolutionary|game.changing|significant|remarkable)',
            r'(we found|discovered|realized|learned|understand)',
            r'(surprisingly|interestingly|fascinatingly|notably)',
            r'(the problem is|the challenge|the issue|the limitation)'
        ]
        
        for sentence in llm_sentences:
            if len(sentence) < 40 or len(sentence) > 250:
                continue
            
            score = 0
            for pattern in opinion_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                quotes.append({
                    'text': sentence.strip(),
                    'relevance': score
                })
        
        quotes.sort(key=lambda x: x['relevance'], reverse=True)
        return quotes[:5]
    
    def _summarize_llm_points(self, llm_sentences, title):
        """Create a summary of LLM-related points"""
        if not llm_sentences:
            return f"Video discusses: {title[:100]}"
        
        substantial = [s for s in llm_sentences if len(s) > 50]
        
        if len(substantial) >= 2:
            return ' '.join(substantial[:2])[:300]
        elif substantial:
            return substantial[0][:300]
        else:
            return llm_sentences[0][:300] if llm_sentences else title[:200]
    
    def _fallback_analysis(self, title, description):
        """Analysis when no transcript is available"""
        text = f"{title} {description}"[:500]
        
        matched_topics = []
        for topic, pattern in self.topic_patterns.items():
            matches = re.findall(pattern, text.lower())
            if matches:
                matched_topics.append({
                    'topic': topic,
                    'mentions': len(matches)
                })
        
        matched_topics.sort(key=lambda x: x['mentions'], reverse=True)
        
        return {
            'topics': matched_topics[:3],
            'key_quotes': [],
            'summary': text[:300],
            'has_transcript': False
        }
    
    def find_channel_relationships(self, all_videos):
        """Find how channels relate based on LLM topics they discuss"""
        
        channels = {}
        for v in all_videos:
            ch = v.get('channel_name', 'Unknown')
            if ch not in channels:
                channels[ch] = {
                    'topics': set(),
                    'videos': []
                }
            
            topics = v.get('llm_topics', [])
            if isinstance(topics, str):
                try:
                    topics = json.loads(topics)
                except:
                    topics = []
            
            for t in topics:
                channels[ch]['topics'].add(t.get('topic', ''))
            
            channels[ch]['videos'].append(v)
        
        relationships = []
        channel_names = list(channels.keys())
        
        for i, ch1 in enumerate(channel_names):
            for ch2 in channel_names[i+1:]:
                topics1 = channels[ch1]['topics']
                topics2 = channels[ch2]['topics']
                
                if not topics1 or not topics2:
                    continue
                
                common = topics1 & topics2
                all_topics = topics1 | topics2
                
                if all_topics:
                    similarity = len(common) / len(all_topics)
                    
                    if similarity > 0.15: 
                        relationships.append({
                            'channel_1': ch1,
                            'channel_2': ch2,
                            'similarity': round(similarity, 2),
                            'common_topics': list(common),
                            'relationship': self._describe_relationship(common, ch1, ch2)
                        })
        
        return sorted(relationships, key=lambda x: x['similarity'], reverse=True)
    
    def _describe_relationship(self, common_topics, ch1, ch2):
        """Describe how channels relate"""
        if not common_topics:
            return f"{ch1} and {ch2} cover LLM content"
        
        topics_str = ', '.join(common_topics[:3])
        if len(common_topics) > 3:
            topics_str += f" and {len(common_topics) - 3} more topics"
        
        return f"Both channels frequently discuss: {topics_str}"
