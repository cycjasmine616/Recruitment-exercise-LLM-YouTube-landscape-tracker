import json
import os
from datetime import datetime

def generate_report():
    data_dir = 'public/data'
    
    try:
        with open(f'{data_dir}/videos.json', 'r') as f:
            videos = json.load(f)
    except:
        videos = []
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Tracker</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; padding: 30px; }}
        .video-card {{ border: 1px solid #dee2e6; border-radius: 12px; overflow: hidden; transition: transform 0.2s; }}
        .video-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }}
        .video-thumbnail {{ width: 100%; height: 200px; object-fit: cover; }}
        .video-info {{ padding: 15px; }}
        .channel-name {{ color: #667eea; font-weight: 600; margin-bottom: 8px; }}
        .video-title {{ font-size: 16px; font-weight: 600; margin-bottom: 10px; }}
        .topic-tag {{ display: inline-block; padding: 4px 10px; background: #e9ecef; border-radius: 15px; font-size: 12px; margin: 2px; }}
        .summary {{ font-size: 14px; color: #4a5568; margin-top: 10px; }}
        .footer {{ text-align: center; padding: 20px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Tracker</h1>
            <p>Auto-updated every 12 hours via GitHub Actions</p>
            <p style="margin-top: 10px;">Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
            <p>{len(videos)} videos tracked</p>
        </div>
        <div class="video-grid">
            {generate_cards(videos)}
        </div>
        <div class="footer">
            <p>Powered by GitHub Actions • Free & Open Source</p>
        </div>
    </div>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w') as f:
        f.write(html)
    
    print(f"Report generated with {len(videos)} videos")

def generate_cards(videos):
    cards = []
    for v in videos[:20]:
        topics = v.get('topics', [])
        tags = ''.join([f'<span class="topic-tag">{t["topic"]}</span>' for t in topics[:3]])
        date = v.get('published_at', '')[:10] if v.get('published_at') else ''
        views = f"{(v.get('view_count', 0)/1000):.1f}K views" if v.get('view_count') else ''
        summary = v.get('summary', '')[:150]
        
        cards.append(f"""
        <div class="video-card">
            <img src="{v.get('thumbnail_url', '')}" class="video-thumbnail" onerror="this.style.display='none'">
            <div class="video-info">
                <div class="channel-name">{v.get('channel_name', 'Unknown')}</div>
                <div class="video-title">{v.get('title', 'Untitled')}</div>
                <div>{tags}</div>
                <div style="color: #6c757d; font-size: 13px; margin-top: 5px;">{date} • {views}</div>
                <div class="summary">{summary}...</div>
            </div>
        </div>""")
    
    return ''.join(cards) if cards else '<p style="text-align:center;padding:50px;">No videos yet. Check back soon!</p>'

if __name__ == "__main__":
    generate_report()
