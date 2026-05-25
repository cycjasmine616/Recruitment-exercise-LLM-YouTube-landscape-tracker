import json
import os
from datetime import datetime

def generate_report():
    videos = load_json_file('public/data/videos.json')
    relations = load_json_file('public/data/relations.json')
    metadata = load_json_file('public/data/metadata.json')
    
    if isinstance(metadata, list):
        metadata = {}
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Tracker</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#f0f2f5; padding:20px; }}
        .container {{ max-width:1200px; margin:0 auto; }}
        .header {{ background:linear-gradient(135deg,#1a1a2e,#16213e); color:white; padding:30px; border-radius:15px; margin-bottom:20px; text-align:center; }}
        table {{ width:100%; border-collapse:collapse; background:white; border-radius:10px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,0.1); margin-bottom:30px; }}
        th {{ background:#1a1a2e; color:white; padding:12px; text-align:left; }}
        td {{ padding:10px 12px; border-bottom:1px solid #eee; font-size:13px; }}
        tr:hover {{ background:#f8f9fa; }}
        .relation-card {{ padding:15px; margin:10px 0; background:#f8f9fa; border-radius:8px; border-left:4px solid #667eea; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Landscape Tracker</h1>
            <p>Analyzing what creators actually say about LLMs</p>
            <div style="display:flex;justify-content:center;gap:20px;margin-top:20px;">
                <div style="background:rgba(255,255,255,0.1);padding:15px 25px;border-radius:10px;">
                    <div style="font-size:28px;font-weight:bold;">{len(videos)}</div>
                    <div>Videos</div>
                </div>
                <div style="background:rgba(255,255,255,0.1);padding:15px 25px;border-radius:10px;">
                    <div style="font-size:28px;font-weight:bold;">{metadata.get('total_channels', 0) if isinstance(metadata, dict) else 0}</div>
                    <div>Channels</div>
                </div>
                <div style="background:rgba(255,255,255,0.1);padding:15px 25px;border-radius:10px;">
                    <div style="font-size:28px;font-weight:bold;">{len(relations)}</div>
                    <div>Relations</div>
                </div>
            </div>
            <p style="margin-top:15px;opacity:0.8;">Updated: {metadata.get('last_updated', '')[:19] if isinstance(metadata, dict) else 'Processing...'}</p>
        </div>
        
        <h2> Video Analysis Table</h2>
        <table>
            <thead><tr><th>Channel</th><th>Video</th><th>LLM Topics</th><th>Depth</th><th>Stance</th></tr></thead>
            <tbody>
                {build_video_rows(videos)}
            </tbody>
        </table>
        
        <h2>Channel Relationships</h2>
        {build_relations(relations)}
    </div>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Generated index.html with {len(videos)} videos and {len(relations)} relations")

def load_json_file(path):
    """Safely load JSON file"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return [] if 'relations' in path or 'videos' in path else {}

def build_video_rows(videos):
    if not videos:
        return '<tr><td colspan="5" style="text-align:center;padding:30px;">No videos yet. Data is being collected...</td></tr>'
    
    rows = []
    for v in videos[:20]:
        topics = v.get('llm_topics_discussed', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = []
        
        topic_html = ' '.join([f'<span style="background:#e9ecef;padding:2px 8px;border-radius:10px;font-size:11px;margin:2px;">{t.get("topic", "")}</span>' for t in topics[:3]])
        
        rows.append(f"""
            <tr>
                <td><strong>{v.get('channel_name', 'Unknown')}</strong></td>
                <td><a href="{v.get('url', '#')}" target="_blank" style="color:#333;">{v.get('title', 'Untitled')[:80]}</a></td>
                <td>{topic_html}</td>
                <td>{v.get('technical_depth', 'N/A')}</td>
                <td>{v.get('creator_stance', 'N/A')}</td>
            </tr>
        """)
    
    return ''.join(rows)

def build_relations(relations):
    if not relations:
        return '<p style="text-align:center;padding:20px;">Channel relationships will appear after data collection...</p>'
    
    cards = []
    for r in relations[:10]:
        common = ', '.join(r.get('common_topics', [])[:3]) if r.get('common_topics') else 'Analyzing...'
        cards.append(f"""
            <div class="relation-card">
                <strong>{r.get('channel_1', '')}</strong> ↔ <strong>{r.get('channel_2', '')}</strong>
                <span style="margin-left:10px;color:#667eea;">Similarity: {(r.get('similarity_score', 0)*100):.0f}%</span>
                <br><small>Common topics: {common}</small>
            </div>
        """)
    
    return ''.join(cards)

if __name__ == "__main__":
    generate_report()
