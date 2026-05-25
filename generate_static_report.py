import json
import os
from datetime import datetime

def generate_report():
    try:
        with open('public/data/videos.json', 'r') as f:
            videos = json.load(f)
    except:
        videos = []
    
    try:
        with open('public/data/metadata.json', 'r') as f:
            metadata = json.load(f)
    except:
        metadata = {'total_videos': 0, 'total_channels': 0, 'last_updated': ''}
    
    cards_html = ""
    for v in videos[:30]:
        topics = v.get('topics', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = []
        
        tags = ''.join([f'<span style="display:inline-block;padding:4px 10px;background:#f0f0f0;border-radius:15px;font-size:12px;margin:2px;">{t["topic"]}</span>' for t in topics[:4]])
        date = v.get('published_at', '')[:10] if v.get('published_at') else ''
        views = f"{(v.get('view_count', 0)/1000):.1f}K" if v.get('view_count') else ''
        thumbnail = v.get('thumbnail_url', '')
        
        cards_html += f"""
        <div style="border:1px solid #ddd;border-radius:10px;overflow:hidden;margin-bottom:20px;transition:0.2s;">
            <img src="{thumbnail}" style="width:100%;height:200px;object-fit:cover;background:#f5f5f5;" 
                 onerror="this.src='https://via.placeholder.com/400x200?text=YouTube+Video'">
            <div style="padding:15px;">
                <div style="color:#667eea;font-weight:600;font-size:14px;margin-bottom:5px;">📺 {v.get('channel_name', 'Unknown')}</div>
                <div style="font-weight:600;margin-bottom:10px;">{v.get('title', 'Untitled')}</div>
                <div>{tags}</div>
                <div style="color:#888;font-size:13px;margin-top:8px;"> {date} •  {views} views</div>
            </div>
        </div>"""
    
    if not cards_html:
        cards_html = '<p style="text-align:center;padding:40px;color:#888;">🔄 Videos will appear here after the pipeline runs successfully...</p>'
    
    # Build full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Tracker</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin:0; padding:20px; background:linear-gradient(135deg,#667eea,#764ba2); min-height:100vh; }}
        .container {{ max-width:1200px; margin:0 auto; background:white; border-radius:20px; overflow:hidden; }}
        .header {{ background:linear-gradient(135deg,#667eea,#764ba2); color:white; padding:40px; text-align:center; }}
        .header h1 {{ font-size:2.5em; margin:0 0 10px 0; }}
        .stats {{ display:flex; justify-content:center; gap:40px; margin-top:20px; }}
        .stat {{ text-align:center; }}
        .stat-num {{ font-size:32px; font-weight:bold; }}
        .stat-label {{ font-size:14px; opacity:0.9; }}
        .grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(350px,1fr)); gap:20px; padding:30px; }}
        .footer {{ text-align:center; padding:20px; color:#888; font-size:14px; border-top:1px solid #eee; }}
        @media (max-width:768px) {{ .grid {{ grid-template-columns:1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Tracker</h1>
            <p>Tracking the latest LLM content across YouTube</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-num">{metadata.get('total_videos', 0)}</div>
                    <div class="stat-label">Videos Tracked</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{metadata.get('total_channels', 0)}</div>
                    <div class="stat-label">Channels</div>
                </div>
                <div class="stat">
                    <div class="stat-num">12h</div>
                    <div class="stat-label">Update Cycle</div>
                </div>
            </div>
            <p style="font-size:12px;opacity:0.8;margin-top:15px;">Last updated: {metadata.get('last_updated', 'Waiting...')[:19]}</p>
        </div>
        <div class="grid">
            {cards_html}
        </div>
        <div class="footer">
            <p> Powered by GitHub Actions | Updated every 12 hours | Free & Open Source</p>
        </div>
    </div>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w') as f:
        f.write(html)
    
    print(f"Report generated with {len(videos)} videos")

if __name__ == "__main__":
    generate_report()
