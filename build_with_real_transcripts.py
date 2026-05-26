from youtube_transcript_api import YouTubeTranscriptApi
import json
import os
import re
from datetime import datetime

# REAL LLM videos with known good transcripts
LLM_VIDEOS = [
    "zjkBMFhNj_g",

    "kCc8FmEb1nY",  

    "bZQun8Y4L2A",

    "wjZofJX0v4M",
   
    "cH1p1kGZlUc",
    
    "ptuGllU5SQQ",
]

LLM_TOPICS = {
    "Transformer Architecture": [
        r'transformer', r'attention mechanism', r'self-attention', r'multi-head',
        r'encoder', r'decoder', r'positional encod', r'feed.forward',
        r'key.value.query', r'residual connection', r'layer norm'
    ],
    "Model Training": [
        r'pre.training', r'fine.tuning', r'RLHF', r'reinforcement learning',
        r'gradient', r'loss function', r'backprop', r'optimizer',
        r'learning rate', r'batch size', r'epoch', r'convergence'
    ],
    "Prompt Engineering": [
        r'prompt', r'few.shot', r'zero.shot', r'chain.of.thought',
        r'system message', r'instruction', r'template', r'context window'
    ],
    "RAG Systems": [
        r'RAG', r'retrieval', r'vector database', r'embedding',
        r'chunking', r'semantic search', r'knowledge base', r'pinecone'
    ],
    "Model Evaluation": [
        r'benchmark', r'evaluation', r'MMLU', r'HumanEval',
        r'accuracy', r'perplexity', r'BLEU', r'ROUGE'
    ],
    "Safety & Alignment": [
        r'safety', r'alignment', r'bias', r'fairness', r'toxicity',
        r'guardrail', r'red.team', r'RLHF', r'constitutional AI'
    ],
    "Open Source LLMs": [
        r'open.source', r'Llama', r'Mistral', r'Falcon', r'weights',
        r'Apache', r'MIT license', r'community', r'Hugging.Face'
    ],
    "AI Agents": [
        r'agent', r'autonomous', r'tool.use', r'function.call',
        r'LangChain', r'AutoGPT', r'react', r'planning'
    ]
}

def download_transcript(video_id):
    """Download actual transcript from YouTube"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = ' '.join([item['text'] for item in transcript_list])
        return full_text, transcript_list
    except Exception as e:
        print(f"  ⚠ Could not download transcript: {e}")
        return None, None

def analyze_transcript(transcript_text, transcript_segments):
    """Analyze what the speaker actually says about LLMs"""
    
    sentences = re.split(r'(?<=[.!?])\s+', transcript_text)
    
    llm_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for topic, patterns in LLM_TOPICS.items():
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    llm_sentences.append({
                        'text': sentence.strip(),
                        'topic': topic
                    })
                    break
    
    topics_found = {}
    for topic, patterns in LLM_TOPICS.items():
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, transcript_text.lower())
            count += len(matches)
        
        if count >= 2: 
            topics_found[topic] = count
    
    sorted_topics = sorted(topics_found.items(), key=lambda x: x[1], reverse=True)
    top_topics = [{'topic': t, 'mentions': c} for t, c in sorted_topics[:5]]
    
    key_quotes = []
    opinion_patterns = [
        r'(important|key|crucial|essential|fundamental)',
        r'(I think|I believe|in my opinion|the thing is)',
        r'(surprising|interesting|fascinating|remarkable)',
        r'(breakthrough|revolutionary|game.changing)',
        r'(the problem|the challenge|the limitation)',
        r'(we found|discovered|realized|learned)'
    ]
    
    for sent in llm_sentences:
        score = 0
        for pattern in opinion_patterns:
            if re.search(pattern, sent['text'], re.IGNORECASE):
                score += 1
        
        if score > 0 and len(sent['text']) > 40:
            key_quotes.append({
                'text': sent['text'][:250],
                'relevance': score,
                'topic': sent['topic']
            })
    
    key_quotes.sort(key=lambda x: x['relevance'], reverse=True)
    
    llm_only = [s['text'] for s in llm_sentences if len(s['text']) > 50]
    if llm_only:
        summary = ' '.join(llm_only[:3])[:400]
    else:
        summary = transcript_text[:400]
    
    return {
        'topics': top_topics[:5],
        'key_quotes': key_quotes[:5],
        'summary': summary,
        'total_llm_sentences': len(llm_sentences)
    }

def get_video_info(video_id):
    """Get video metadata using oEmbed (no API key needed!)"""
    import requests
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title', 'Unknown'),
                'channel_name': data.get('author_name', 'Unknown'),
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            }
    except:
        pass
    
    return {
        'title': f'Video {video_id}',
        'channel_name': 'Unknown Channel',
        'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    }

def main():
    print("=" * 60)
    print("BUILDING LLM TRACKER WITH REAL TRANSCRIPTS")
    print("=" * 60)
    
    all_videos = []
    channels_data = {}
    
    for i, video_id in enumerate(LLM_VIDEOS, 1):
        print(f"\n[{i}/{len(LLM_VIDEOS)}] Processing video {video_id}...")
        
        info = get_video_info(video_id)
        title = info['title']
        channel = info['channel_name']
        print(f"   {title[:80]}")
        print(f"   {channel}")
        
        if channel not in channels_data:
            channels_data[channel] = {'topics': set(), 'count': 0}
        channels_data[channel]['count'] += 1
        
        print("   Downloading transcript...")
        transcript_text, transcript_segments = download_transcript(video_id)
        
        if transcript_text:
            print(f"   Got transcript ({len(transcript_text)} characters)")
            
            print("   Analyzing LLM content...")
            analysis = analyze_transcript(transcript_text, transcript_segments)
            
            print(f"   Topics found: {len(analysis['topics'])}")
            for t in analysis['topics'][:3]:
                print(f"     - {t['topic']} ({t['mentions']} mentions)")
            
            print(f"   Key quotes: {len(analysis['key_quotes'])}")
            
            for t in analysis['topics']:
                channels_data[channel]['topics'].add(t['topic'])
            
            video_data = {
                'id': video_id,
                'title': title,
                'channel_name': channel,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'thumbnail_url': info['thumbnail'],
                'published_at': '2024',
                'transcript_available': True,
                'llm_topics_discussed': analysis['topics'],
                'transcript_excerpts': analysis['key_quotes'],
                'practical_insights': analysis['summary'],
                'llm_sentence_count': analysis['total_llm_sentences']
            }
        else:
            print("  ⚠ No transcript available")
            video_data = {
                'id': video_id,
                'title': title,
                'channel_name': channel,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'thumbnail_url': info['thumbnail'],
                'published_at': '2024',
                'transcript_available': False,
                'llm_topics_discussed': [],
                'transcript_excerpts': [],
                'practical_insights': f"Transcript unavailable for: {title}",
                'llm_sentence_count': 0
            }
        
        all_videos.append(video_data)
    
    print(f"\n🔗 CALCULATING CHANNEL RELATIONSHIPS...")
    channel_names = list(channels_data.keys())
    relationships = []
    
    for i, ch1 in enumerate(channel_names):
        for ch2 in channel_names[i+1:]:
            topics1 = channels_data[ch1]['topics']
            topics2 = channels_data[ch2]['topics']
            
            common = topics1 & topics2
            all_topics = topics1 | topics2
            
            if all_topics and common:
                similarity = len(common) / len(all_topics)
                if similarity > 0.1:
                    relationships.append({
                        'channel_1': ch1,
                        'channel_2': ch2,
                        'similarity': round(similarity, 2),
                        'common_topics': list(common)[:5],
                        'relationship': f"Both channels discuss: {', '.join(list(common)[:3])}"
                    })
                    print(f"  {ch1} ↔ {ch2}: {similarity:.0%} similar")
    
    # Build metadata
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(all_videos),
        'total_channels': len(channels_data),
        'channels': list(channels_data.keys()),
        'total_relations': len(relationships),
        'videos_with_transcripts': sum(1 for v in all_videos if v['transcript_available'])
    }
    
    # Save data
    os.makedirs('public/data', exist_ok=True)
    
    with open('public/data/videos.json', 'w') as f:
        json.dump(all_videos, f, indent=2)
    
    with open('public/data/relations.json', 'w') as f:
        json.dump(relationships, f, indent=2)
    
    with open('public/data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Generate HTML
    print(f"\n📄 GENERATING HTML...")
    html = generate_html(all_videos, relationships, metadata)
    
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n DONE!")
    print(f"   Videos: {len(all_videos)}")
    print(f"   With transcripts: {metadata['videos_with_transcripts']}")
    print(f"   Channels: {len(channels_data)}")
    print(f"   Relationships: {len(relationships)}")
    print(f"\n Files created in public/")
    print(f"   - index.html")
    print(f"   - data/videos.json")
    print(f"   - data/relations.json")

def generate_html(videos, relations, metadata):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Landscape Tracker</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:#f0f2f5; padding:20px; }}
        .container {{ max-width:1400px; margin:0 auto; }}
        .header {{ background:linear-gradient(135deg,#1a1a2e,#16213e); color:white; padding:30px; border-radius:12px; margin-bottom:25px; text-align:center; }}
        .stats {{ display:flex; justify-content:center; gap:25px; margin-top:20px; flex-wrap:wrap; }}
        .stat {{ background:rgba(255,255,255,0.12); padding:15px 25px; border-radius:10px; }}
        .stat-num {{ font-size:30px; font-weight:bold; }}
        table {{ width:100%; background:white; border-collapse:collapse; border-radius:10px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08); margin-bottom:30px; }}
        th {{ background:#1a1a2e; color:white; padding:12px; text-align:left; font-size:13px; }}
        td {{ padding:10px 12px; border-bottom:1px solid #eee; font-size:13px; vertical-align:top; }}
        tr:hover {{ background:#f8f9ff; }}
        .channel-badge {{ background:#e8eaf6; color:#3949ab; padding:4px 12px; border-radius:12px; font-weight:600; font-size:12px; }}
        .topic-tag {{ background:#e8f5e9; color:#2e7d32; padding:3px 9px; border-radius:10px; font-size:11px; margin:2px; display:inline-block; }}
        .quote {{ font-size:12px; color:#555; font-style:italic; }}
        .quote::before {{ content:'"'; }}
        .quote::after {{ content:'"'; }}
        .relations-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(350px,1fr)); gap:15px; }}
        .relation-card {{ background:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06); border-left:4px solid #667eea; }}
        .transcript-yes {{ background:#e8f5e9; color:#2e7d32; padding:2px 8px; border-radius:8px; font-size:11px; }}
        .transcript-no {{ background:#fff3e0; color:#e65100; padding:2px 8px; border-radius:8px; font-size:11px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 LLM YouTube Landscape Tracker</h1>
            <p>Real transcript analysis of what popular creators say about Large Language Models</p>
            <div class="stats">
                <div class="stat"><div class="stat-num">{metadata['total_videos']}</div><div class="stat-label">Videos Analyzed</div></div>
                <div class="stat"><div class="stat-num">{metadata['total_channels']}</div><div class="stat-label">Channels</div></div>
                <div class="stat"><div class="stat-num">{metadata['videos_with_transcripts']}</div><div class="stat-label">With Transcripts</div></div>
                <div class="stat"><div class="stat-num">{metadata['total_relations']}</div><div class="stat-label">Relations</div></div>
            </div>
        </div>
        
        <h2 style="margin:25px 0 15px 0;">📊 What Creators Actually Say About LLMs (From Transcripts)</h2>
        <table>
            <thead>
                <tr><th>Speaker</th><th>Video</th><th>LLM Topics Discussed</th><th>What They Said (from transcript)</th></tr>
            </thead>
            <tbody>
                {build_rows(videos)}
            </tbody>
        </table>
        
        <h2 style="margin:25px 0 15px 0;">🔗 How Channels Relate on LLM Themes</h2>
        <div class="relations-grid">
            {build_relations(relations)}
        </div>
    </div>
</body>
</html>"""

def build_rows(videos):
    rows = []
    for v in videos:
        channel = v['channel_name']
        title = v['title'][:80]
        url = v['url']
        
        topics = v.get('llm_topics_discussed', [])
        topic_html = ' '.join([f'<span class="topic-tag">{t["topic"]}</span>' for t in topics[:4]])
        
        quotes = v.get('transcript_excerpts', [])
        has_transcript = v.get('transcript_available', False)
        
        if quotes:
            q = quotes[0]
            what_said = f'<span class="quote">{q["text"][:200]}</span>'
            source = f'<span class="transcript-yes">✓ Transcript ({v.get("llm_sentence_count", "?")} LLM mentions)</span>'
        else:
            what_said = v.get('practical_insights', 'No transcript')[:200]
            source = '<span class="transcript-no">No transcript</span>'
        
        rows.append(f"""
            <tr>
                <td><span class="channel-badge">{channel}</span></td>
                <td><a href="{url}" target="_blank" style="color:#1a73e8;">{title}</a></td>
                <td>{topic_html if topic_html else '-'}</td>
                <td style="font-size:12px;">{what_said}<br><small>{source}</small></td>
            </tr>
        """)
    return ''.join(rows)

def build_relations(relations):
    if not relations:
        return '<p>No relationships found yet</p>'
    
    cards = []
    for r in relations:
        topics = ' '.join([f'<span class="topic-tag">{t}</span>' for t in r['common_topics'][:4]])
        cards.append(f"""
            <div class="relation-card">
                <h3>{r['channel_1']} ↔ {r['channel_2']}</h3>
                <p style="color:#667eea;font-weight:bold;">{int(r['similarity']*100)}% topic overlap</p>
                <p style="margin-top:8px;font-size:13px;">{r['relationship']}</p>
                <div style="margin-top:8px;">{topics}</div>
            </div>
        """)
    return ''.join(cards)

if __name__ == "__main__":
    main()
