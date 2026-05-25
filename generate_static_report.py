import json
import os
from datetime import datetime

def generate_report():
    # Load data
    try:
        with open('public/data/videos.json', 'r') as f:
            videos = json.load(f)
        logger.info(f"Loaded {len(videos)} videos")
    except Exception as e:
        print(f"Could not load videos: {e}")
        videos = []
    
    try:
        with open('public/data/metadata.json', 'r') as f:
            metadata = json.load(f)
    except:
        metadata = {'total_videos': len(videos), 'total_channels': 0, 'last_updated': ''}
    
    # Generate video cards
    cards_html = ""
    for v in videos[:30]:
        topics = v.get('topics', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = []
        
        tags = ''.join([
            f'<span style="display:inline-block;padding:3px 8px;background:#e9ecef;border-radius:12px;font-size:11px;margin:2px;">{t["topic"]}</span>' 
            for t in topics[:4]
        ])
        
        date = v.get('published_at', '')[:10] if v.get('published_at') else ''
        views = f"{(v.get('view_count', 0)/1000):.1f}K" if v.get('view_count') else ''
        thumbnail = v.get('thumbnail_url', '')
        title = v.get('title', 'Untitled')[:80]
        channel = v.get('channel_name', 'Unknown')
        
        cards_html += f"""
        <div style="border:1px solid #ddd;border-radius:10px;overflow:hidden;transition:0.2s;cursor:pointer;"
             onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
             onmouseout="this.style.boxShadow='none'">
            <img src="{thumbnail}" style="width:100%;height:200px;object-fit:cover;background:#f0f0f0;" 
                 onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22350%22 height=%22200%22><rect fill=%22%23f0f0f0%22 width=%22350%22 height=%22200%22/><text fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22>YouTube Video</text></svg>'">
            <div style="padding:15px;">
                <div style="color:#667eea;font-weight:600;font-size:13px;margin-bottom:5px;"> {channel}</div>
                <div style="font-weight:600;margin-bottom:8px;font-size:15px;line-height:1.4;">{title}</div>
                <div style="margin-bottom:8px;">{tags}</div>
                <div style="color:#888;font-size:12px;"> {date} • 👁 {views} views</div>
            </div>
        </div>"""
    
    if not cards_html:
        cards_html = '<p style="text-align:center;padding:40px;color:#888;"> No videos yet. Pipeline is running...</p>'
    
    # Build HTML
    total_videos = metadata.get('total_videos', len(videos))
    total_channels = metadata.get('total_channels', 0)
    last_updated = metadata.get('last_updated', 'Waiting...')[:19]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> LLM YouTube Tracker</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); min-height:100vh; padding:20px; }}
        .container {{ max-width:1200px; margin:0 auto; background:white; border-radius:20px; overflow:hidden; box-shadow:0 20px 60px rgba(0,0,0,0.3); }}
        .header {{ background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:40px 20px; text-align:center; }}
        .header h1 {{ font-size:2.5em; margin-bottom:10px; }}
        .header p {{ font-size:1.1em; opacity:0.95; }}
        .stats {{ display:flex; justify-content:center; gap:30px; margin-top:20px; flex-wrap:wrap; }}
        .stat {{ background:rgba(255,255,255,0.15); padding:15px 25px; border-radius:12px; backdrop-filter:blur(10px); }}
        .stat-value {{ font-size:32px; font-weight:bold; }}
        .stat-label {{ font-size:13px; opacity:0.9; margin-top:5px; }}
        .update-info {{ margin-top:15px; font-size:12px; opacity:0.8; }}
        .grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(350px, 1fr)); gap:20px; padding:30px; }}
        .footer {{ text-align:center; padding:20px; color:#888; font-size:14px; border-top:1px solid #eee; }}
        .status-badge {{ display:inline-block; padding:4px 12px; border-radius:12px; font-size:12px; margin-top:10px; }}
        .status-success {{ background:#d4edda; color:#155724; }}
        .status-pending {{ background:#fff3cd; color:#856404; }}
        @media (max-width:768px) {{ 
            .grid {{ grid-template-columns:1fr; }}
            .header h1 {{ font-size:1.8em; }}
            .stats {{ gap:15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Landscape Tracker</h1>
            <p>Automated tracking of LLM content across YouTube</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_videos}</div>
                    <div class="stat-label">Videos Tracked</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_channels}</div>
                    <div class="stat-label">Channels</div>
                </div>
                <div class="stat">
                    <div class="stat-value">12h</div>
                    <div class="stat-label">Update Cycle</div>
                </div>
                <div class="stat">
                    <div class="stat-value">39</div>
                    <div class="stat-label">Per Run</div>
                </div>
            </div>
            <div class="update-info">
                 Last updated: {last_updated} UTC | 
                <span class="status-badge status-success">✓ Auto-pilot Active</span>
            </div>
        </div>
        <div class="grid">
            {cards_html}
        </div>
        <div class="footer">
            <p> Powered by <strong>GitHub Actions</strong> | Updated every 12 hours</p>
            <p style="font-size:12px;margin-top:5px;">Using free Hugging Face models | No API costs | Open Source</p>
        </div>
    </div>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Report generated with {len(videos)} videos")
    print(f" File: public/index.html")

if __name__ == "__main__":
    # Setup basic logging for this script
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    generate_report()
