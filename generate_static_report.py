import json
import os
from datetime import datetime

def generate_report():
    """Generate a simple HTML report that will definitely work"""
    
    videos = []
    try:
        with open('public/data/videos.json', 'r') as f:
            videos = json.load(f)
    except:
        pass
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM YouTube Tracker</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .stats {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
        .stat {{ background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 8px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        table {{ width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        th {{ background: #333; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f8f8; }}
        .tag {{ display: inline-block; padding: 3px 8px; background: #e8e8e8; border-radius: 10px; font-size: 11px; margin: 2px; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Landscape Tracker</h1>
            <p>Tracking what creators say about Large Language Models</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(videos)}</div>
                    <div>Videos Analyzed</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{datetime.utcnow().strftime('%H:%M')}</div>
                    <div>Last Updated (UTC)</div>
                </div>
            </div>
        </div>
        
        <h2> Latest Videos</h2>
        <table>
            <thead>
                <tr>
                    <th>Channel</th>
                    <th>Video Title</th>
                    <th>LLM Topics</th>
                    <th>Analysis</th>
                </tr>
            </thead>
            <tbody>
                {build_rows(videos)}
            </tbody>
        </table>
        
        <div class="footer">
            <p>Auto-updated every 12 hours via GitHub Actions</p>
        </div>
    </div>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    if os.path.exists('public/index.html'):
        size = os.path.getsize('public/index.html')
        print(f" Created public/index.html ({size} bytes)")
    else:
        print(" Failed to create index.html")

def build_rows(videos):
    if not videos:
        return '<tr><td colspan="4" style="text-align:center;padding:30px;color:#888;">🔄 No videos yet. Pipeline is collecting data...</td></tr>'
    
    rows = []
    for v in videos[:30]:
        channel = v.get('channel_name', 'Unknown')
        title = v.get('title', 'Untitled')[:100]
        url = v.get('url', '#')
        
        topics = v.get('llm_topics_discussed', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = []
        
        tags = ' '.join([f'<span class="tag">{t.get("topic", "")}</span>' for t in topics[:4]])
        
        insights = v.get('practical_insights', '')[:120] if v.get('practical_insights') else v.get('description', '')[:120]
        
        rows.append(f"""
            <tr>
                <td><strong>{channel}</strong></td>
                <td><a href="{url}" target="_blank" style="color:#333;text-decoration:none;">{title}</a></td>
                <td>{tags if tags else '-'}</td>
                <td style="font-size:12px;color:#666;">{insights}...</td>
            </tr>
        """)
    
    return ''.join(rows)

if __name__ == "__main__":
    generate_report()
