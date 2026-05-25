import json
import os
from datetime import datetime

def generate_report():
    videos = load_json('public/data/videos.json')
    relations = load_json('public/data/relations.json')
    metadata = load_json('public/data/metadata.json')
    
    html = build_html(videos, relations, metadata)
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Report generated with {len(videos)} videos and {len(relations)} channel relationships")

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return []

def build_html(videos, relations, metadata):
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Landscape Tracker</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#f5f5f5; padding:20px; }}
        .container {{ max-width:1400px; margin:0 auto; }}
        .header {{ background:linear-gradient(135deg,#1a1a2e,#16213e); color:white; padding:30px; border-radius:15px; margin-bottom:20px; text-align:center; }}
        .header h1 {{ font-size:2em; margin-bottom:10px; }}
        .stats {{ display:flex; justify-content:center; gap:20px; margin-top:20px; flex-wrap:wrap; }}
        .stat {{ background:rgba(255,255,255,0.1); padding:15px 25px; border-radius:10px; }}
        .stat-value {{ font-size:28px; font-weight:bold; }}
        
        table {{ width:100%; border-collapse:collapse; background:white; border-radius:10px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,0.1); margin-bottom:30px; }}
        th {{ background:#1a1a2e; color:white; padding:12px 15px; text-align:left; font-size:14px; }}
        td {{ padding:12px 15px; border-bottom:1px solid #eee; font-size:14px; }}
        tr:hover {{ background:#f8f9fa; }}
        
        .channel-tag {{ display:inline-block; padding:4px 10px; background:#e3f2fd; color:#1565c0; border-radius:12px; font-size:12px; font-weight:600; }}
        .topic-tag {{ display:inline-block; padding:3px 8px; background:#f0f0f0; border-radius:10px; font-size:11px; margin:2px; }}
        .depth-beginner {{ color:#4caf50; }}
        .depth-intermediate {{ color:#ff9800; }}
        .depth-advanced {{ color:#f44336; }}
        
        .relations-section {{ background:white; padding:25px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.1); }}
        .relation-card {{ padding:15px; margin:10px 0; background:#f8f9fa; border-radius:8px; border-left:4px solid #667eea; }}
        
        @media (max-width:768px) {{ table {{ font-size:12px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Landscape Tracker</h1>
            <p>Deep analysis of what creators actually say about LLMs</p>
            <div class="stats">
                <div class="stat"><div class="stat-value">{len(videos)}</div><div>Videos Analyzed</div></div>
                <div class="stat"><div class="stat-value">{metadata.get('total_channels', 0)}</div><div>LLM Channels</div></div>
                <div class="stat"><div class="stat-value">{len(relations)}</div><div>Channel Relations</div></div>
                <div class="stat"><div class="stat-value">{sum(1 for v in videos if v.get('transcript_available'))}</div><div>With Transcripts</div></div>
            </div>
            <p style="margin-top:15px;opacity:0.8;">Updated: {metadata.get('last_updated', '')[:19]} UTC</p>
        </div>
        
        <h2 style="margin:20px 0;"> Video Analysis Table</h2>
        <table>
            <thead>
                <tr>
                    <th>Channel</th>
                    <th>Video Title</th>
                    <th>LLM Topics Discussed</th>
                    <th>Technical Depth</th>
                    <th>Creator Stance</th>
                    <th>Key Insights</th>
                </tr>
            </thead>
            <tbody>
                {build_table_rows(videos)}
            </tbody>
        </table>
        
        <h2 style="margin:30px 0 20px 0;">🔗 Channel Relationships on LLM Themes</h2>
        <div class="relations-section">
            {build_relations_html(relations)}
        </div>
        
        <p style="text-align:center;margin-top:30px;color:#888;"> Auto-updated via GitHub Actions | Deep LLM Content Analysis</p>
    </div>
</body>
</html>"""

def build_table_rows(videos):
    rows = []
    for v in videos[:50]:
        channel = v.get('channel_name', 'Unknown')
        title = v.get('title', 'Untitled')[:80]
        topics = v.get('llm_topics_discussed', [])
        depth = v.get('technical_depth', 'Unknown')
        stance = v.get('creator_stance', 'Unknown')
        insights = v.get('practical_insights', '')[:120]
        
        topics_html = ''.join([f'<span class="topic-tag">{t["topic"]}</span>' for t in topics[:3]])
        
        depth_class = f"depth-{depth.lower()}" if depth else ""
        
        rows.append(f"""
            <tr>
                <td><span class="channel-tag">{channel}</span></td>
                <td>{title}</td>
                <td>{topics_html}</td>
                <td class="{depth_class}">{depth}</td>
                <td>{stance}</td>
                <td style="font-size:12px;">{insights}</td>
            </tr>
        """)
    
    return ''.join(rows) if rows else '<tr><td colspan="6">No videos analyzed yet</td></tr>'

def build_relations_html(relations):
    if not relations:
        return '<p>No channel relationships mapped yet</p>'
    
    cards = []
    for r in relations[:10]:
        common = ', '.join(r.get('common_topics', [])[:3])
        cards.append(f"""
            <div class="relation-card">
                <strong>{r['channel_1']}</strong> ↔ <strong>{r['channel_2']}</strong>
                <span style="margin-left:10px;color:#667eea;">Similarity: {r['similarity_score']:.1%}</span>
                <br><small>Common topics: {common}</small>
                <br><small style="color:#666;">{r.get('description', '')}</small>
            </div>
        """)
    
    return ''.join(cards)

if __name__ == "__main__":
    generate_report()
    
    if os.path.exists('public/index.html'):
        print(" public/index.html created successfully")
    else:
        print(" ERROR: public/index.html was not created!")
