import json
import os
from datetime import datetime

def generate_report():
    videos = load_json('public/data/videos.json')
    relations = load_json('public/data/relations.json')
    metadata = load_json('public/data/metadata.json')
    
    if isinstance(metadata, list):
        metadata = {}
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Landscape Tracker</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:#f0f2f5; padding:20px; color:#333; }}
        .container {{ max-width:1400px; margin:0 auto; }}
        .header {{ background:linear-gradient(135deg,#1a1a2e,#16213e); color:white; padding:30px; border-radius:12px; margin-bottom:25px; text-align:center; }}
        .header h1 {{ font-size:2em; margin-bottom:8px; }}
        .header p {{ opacity:0.9; }}
        .stats {{ display:flex; justify-content:center; gap:25px; margin-top:20px; flex-wrap:wrap; }}
        .stat {{ background:rgba(255,255,255,0.12); padding:15px 25px; border-radius:10px; }}
        .stat-num {{ font-size:30px; font-weight:bold; }}
        .stat-label {{ font-size:13px; opacity:0.85; margin-top:3px; }}
        
        .section-title {{ font-size:1.4em; margin:30px 0 15px 0; color:#1a1a2e; }}
        
        table {{ width:100%; background:white; border-collapse:collapse; border-radius:10px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08); margin-bottom:30px; }}
        th {{ background:#1a1a2e; color:white; padding:14px 15px; text-align:left; font-size:13px; font-weight:600; }}
        td {{ padding:12px 15px; border-bottom:1px solid #eee; font-size:13px; vertical-align:top; }}
        tr:hover {{ background:#f8f9ff; }}
        
        .channel-badge {{ display:inline-block; padding:4px 12px; background:#e8eaf6; color:#3949ab; border-radius:12px; font-weight:600; font-size:12px; }}
        .topic-tag {{ display:inline-block; padding:3px 9px; background:#e8f5e9; color:#2e7d32; border-radius:10px; font-size:11px; margin:2px; }}
        .quote {{ font-size:12px; color:#555; font-style:italic; line-height:1.5; }}
        .quote::before {{ content:'"'; }}
        .quote::after {{ content:'"'; }}
        
        .relations-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(350px,1fr)); gap:15px; }}
        .relation-card {{ background:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06); border-left:4px solid #667eea; }}
        .relation-card h3 {{ color:#1a1a2e; margin-bottom:8px; font-size:16px; }}
        .relation-score {{ display:inline-block; padding:4px 12px; background:#667eea; color:white; border-radius:15px; font-size:13px; font-weight:600; }}
        .common-topics {{ margin-top:8px; }}
        
        .transcript-badge {{ display:inline-block; padding:2px 8px; border-radius:8px; font-size:11px; }}
        .has-transcript {{ background:#e8f5e9; color:#2e7d32; }}
        .no-transcript {{ background:#fff3e0; color:#e65100; }}
        
        @media (max-width:768px) {{
            table {{ font-size:11px; }}
            th, td {{ padding:8px 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Landscape Tracker</h1>
            <p>What popular creators actually say about Large Language Models</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-num">{metadata.get('total_videos', len(videos))}</div>
                    <div class="stat-label">Videos Analyzed</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{metadata.get('total_channels', 0)}</div>
                    <div class="stat-label">Channels Tracked</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{metadata.get('videos_with_transcripts', 0)}</div>
                    <div class="stat-label">With Transcripts</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{len(relations)}</div>
                    <div class="stat-label">Channel Relations</div>
                </div>
            </div>
            <p style="margin-top:15px;font-size:12px;opacity:0.75;"> Last updated: {metadata.get('last_updated', '')[:19] if metadata.get('last_updated') else 'Processing...'} UTC</p>
        </div>
        
        <h2 class="section-title"> Video Analysis: What Creators Say About LLMs</h2>
        <table>
            <thead>
                <tr>
                    <th style="width:12%;">Channel</th>
                    <th style="width:20%;">Video</th>
                    <th style="width:15%;">LLM Topics Covered</th>
                    <th style="width:38%;">What They Said About LLMs</th>
                    <th style="width:15%;">Transcript</th>
                </tr>
            </thead>
            <tbody>
                {build_table(videos)}
            </tbody>
        </table>
        
        <h2 class="section-title">🔗 How Channels Relate on LLM Themes</h2>
        <div class="relations-grid">
            {build_relations(relations)}
        </div>
        
        <p style="text-align:center;margin-top:40px;color:#888;font-size:13px;">
             Auto-updated via GitHub Actions | Analyzed from video transcripts
        </p>
    </div>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Generated report: {len(videos)} videos, {len(relations)} relations")

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return []

def build_table(videos):
    if not videos:
        return '<tr><td colspan="5" style="text-align:center;padding:40px;color:#888;"> Collecting and analyzing videos... Check back soon!</td></tr>'
    
    rows = []
    for v in videos[:30]:
        channel = v.get('channel_name', 'Unknown')
        title = v.get('title', 'Untitled')[:80]
        url = v.get('url', '#')
        has_transcript = v.get('transcript_available', False)
        
        topics = v.get('llm_topics_discussed', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = []
        
        topic_tags = ' '.join([
            f'<span class="topic-tag">{t.get("topic", t) if isinstance(t, dict) else t}</span>' 
            for t in topics[:4]
        ])
        
        quotes = v.get('transcript_excerpts', [])
        if isinstance(quotes, str):
            try:
                quotes = json.loads(quotes)
            except:
                quotes = []
        
        if quotes and len(quotes) > 0:
            quote_text = quotes[0].get('text', quotes[0]) if isinstance(quotes[0], dict) else str(quotes[0])
            what_they_said = f'<span class="quote">{quote_text[:200]}</span>'
        else:
            summary = v.get('practical_insights', v.get('description', ''))
            what_they_said = summary[:200] + '...' if len(summary) > 200 else summary
        
        transcript_badge = '<span class="transcript-badge has-transcript">✓ Transcript</span>' if has_transcript else '<span class="transcript-badge no-transcript">Description only</span>'
        
        rows.append(f"""
            <tr>
                <td><span class="channel-badge">{channel}</span></td>
                <td><a href="{url}" target="_blank" style="color:#1a73e8;text-decoration:none;font-weight:500;">{title}</a></td>
                <td>{topic_tags if topic_tags else 'General AI'}</td>
                <td style="font-size:12px;">{what_they_said}</td>
                <td>{transcript_badge}</td>
            </tr>
        """)
    
    return ''.join(rows)

def build_relations(relations):
    if not relations:
        return '<p style="grid-column:1/-1;text-align:center;padding:30px;color:#888;">Channel relationships will appear after analyzing multiple channels...</p>'
    
    cards = []
    for r in relations[:12]:
        common_topics = r.get('common_topics', [])
        topics_html = ' '.join([f'<span class="topic-tag">{t}</span>' for t in common_topics[:5]])
        
        cards.append(f"""
            <div class="relation-card">
                <h3>{r.get('channel_1', '')} ↔ {r.get('channel_2', '')}</h3>
                <span class="relation-score">{(r.get('similarity', 0)*100):.0f}% overlap</span>
                <p style="margin-top:10px;font-size:13px;color:#555;">{r.get('relationship', '')}</p>
                <div class="common-topics">{topics_html}</div>
            </div>
        """)
    
    return ''.join(cards)

if __name__ == "__main__":
    generate_report()
