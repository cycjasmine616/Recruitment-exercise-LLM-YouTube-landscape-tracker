import json
import os
from datetime import datetime

def generate_report():

    data_dir = 'public/data'
    
    with open(f'{data_dir}/videos.json', 'r') as f:
        videos = json.load(f)
    
    with open(f'{data_dir}/channels.json', 'r') as f:
        channels = json.load(f)
    
    with open(f'{data_dir}/topics.json', 'r') as f:
        topics = json.load(f)
    
    with open(f'{data_dir}/metadata.json', 'r') as f:
        metadata = json.load(f)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 LLM YouTube Landscape Tracker</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.95;
        }}
        
        .update-info {{
            text-align: center;
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 14px;
        }}
        
        .filters {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        
        .filter-btn:hover, .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .tab-nav {{
            display: flex;
            border-bottom: 2px solid #dee2e6;
            background: #f8f9fa;
            padding: 0 30px;
        }}
        
        .tab-btn {{
            padding: 15px 25px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 16px;
            color: #6c757d;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            transition: all 0.3s;
        }}
        
        .tab-btn.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-content {{
            display: none;
            padding: 30px;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .video-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .video-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        
        .video-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .video-thumbnail {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #e9ecef;
        }}
        
        .video-info {{
            padding: 15px;
        }}
        
        .channel-name {{
            color: #667eea;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .video-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #2d3748;
            line-height: 1.4;
        }}
        
        .topic-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin: 10px 0;
        }}
        
        .topic-tag {{
            padding: 4px 10px;
            background: #e9ecef;
            border-radius: 15px;
            font-size: 12px;
            color: #495057;
        }}
        
        .video-meta {{
            display: flex;
            justify-content: space-between;
            color: #6c757d;
            font-size: 13px;
            margin-top: 10px;
        }}
        
        .summary-text {{
            font-size: 13px;
            color: #4a5568;
            line-height: 1.5;
            margin-top: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .channel-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .channel-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .channel-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .topics-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 10px;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #dee2e6;
            border-radius: 25px;
            font-size: 16px;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            overflow-y: auto;
        }}
        
        .modal-content {{
            background: white;
            margin: 50px auto;
            padding: 30px;
            border-radius: 20px;
            max-width: 800px;
            position: relative;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .close-btn {{
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 28px;
            cursor: pointer;
            color: #6c757d;
            background: none;
            border: none;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .video-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LLM YouTube Landscape Tracker</h1>
            <p>Monitoring and analyzing LLM-focused content across popular YouTube channels</p>
            <div class="update-info">
                 Last updated: {metadata['last_updated'][:19].replace('T', ' ')} UTC | 
                 {metadata['total_videos']} videos | 
                 {metadata['total_channels']} channels
            </div>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-value">{metadata['total_videos']}</div>
                <div class="stat-label">Videos Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metadata['total_channels']}</div>
                <div class="stat-label">Channels Monitored</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(topics)}</div>
                <div class="stat-label">Topics Identified</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(t['video_count'] for t in topics)}</div>
                <div class="stat-label">Topic Tags Generated</div>
            </div>
        </div>
        
        <div class="tab-nav">
            <button class="tab-btn active" onclick="showTab('videos')"> Videos</button>
            <button class="tab-btn" onclick="showTab('channels')"> Channels</button>
            <button class="tab-btn" onclick="showTab('topics')"> Topics</button>
        </div>
        
        <div id="videos-tab" class="tab-content active">
            <input type="text" class="search-box" id="searchInput" 
                   placeholder=" Search videos by title, channel, or topic..." 
                   onkeyup="filterVideos()">
            
            <div class="filters" id="topicFilters">
                <button class="filter-btn active" onclick="filterByTopic('all')">All Topics</button>
                {generate_topic_buttons(topics)}
            </div>
            
            <div class="video-grid" id="videoGrid">
                {generate_video_cards(videos)}
            </div>
        </div>
        
        <div id="channels-tab" class="tab-content">
            <div class="channel-grid">
                {generate_channel_cards(channels)}
            </div>
        </div>
        
        <div id="topics-tab" class="tab-content">
            <div class="channel-grid">
                {generate_topic_cards(topics)}
            </div>
        </div>
        
        <div class="footer">
            <p> LLM YouTube Landscape Tracker | Auto-updated every 6 hours via GitHub Actions</p>
            <p>Powered by free Hugging Face models | No API keys required</p>
        </div>
    </div>
    
    <div class="modal" id="videoModal">
        <div class="modal-content">
            <button class="close-btn" onclick="closeModal()">&times;</button>
            <div id="modalContent"></div>
        </div>
    </div>
    
    <script>
        // Store videos data
        const videosData = {json.dumps(videos)};
        
        function showTab(tabName) {{
            // Update buttons
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
        }}
        
        function filterVideos() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const grid = document.getElementById('videoGrid');
            
            const filtered = videosData.filter(video => 
                video.title.toLowerCase().includes(query) ||
                video.channel_name.toLowerCase().includes(query) ||
                (video.summary && video.summary.toLowerCase().includes(query)) ||
                (video.topics && video.topics.some(t => t.topic.toLowerCase().includes(query)))
            );
            
            grid.innerHTML = filtered.map(video => createVideoCard(video)).join('');
        }}
        
        function filterByTopic(topic) {{
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const grid = document.getElementById('videoGrid');
            let filtered;
            
            if (topic === 'all') {{
                filtered = videosData;
            }} else {{
                filtered = videosData.filter(video => 
                    video.topics && video.topics.some(t => t.topic === topic)
                );
            }}
            
            grid.innerHTML = filtered.map(video => createVideoCard(video)).join('');
        }}
        
        function createVideoCard(video) {{
            const topics = video.topics || [];
            const topicTags = topics.map(t => 
                `<span class="topic-tag">${{t.topic}}</span>`
            ).join('');
            
            const publishDate = new Date(video.published_at).toLocaleDateString('en-US', {{
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            }});
            
            const views = video.view_count ? `${{(video.view_count/1000).toFixed(1)}}K views` : '';
            
            return `
                <div class="video-card" onclick="showVideoDetail('${{video.id}}')">
                    <img src="${{video.thumbnail_url}}" class="video-thumbnail" 
                         alt="${{video.title}}" loading="lazy"
                         onerror="this.src='https://via.placeholder.com/350x200?text=No+Thumbnail'">
                    <div class="video-info">
                        <div class="channel-name">📺 ${{video.channel_name}}</div>
                        <div class="video-title">${{video.title}}</div>
                        <div class="topic-tags">${{topicTags}}</div>
                        <div class="video-meta">
                            <span>📅 ${{publishDate}}</span>
                            <span>👁 ${{views}}</span>
                        </div>
                        ${{video.summary ? `<div class="summary-text">${{video.summary.substring(0, 150)}}...</div>` : ''}}
                    </div>
                </div>
            `;
        }}
        
        function showVideoDetail(videoId) {{
            const video = videosData.find(v => v.id === videoId);
            if (!video) return;
            
            const topics = video.topics || [];
            const publishDate = new Date(video.published_at).toLocaleString('en-US', {{
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }});
            
            const modalContent = document.getElementById('modalContent');
            modalContent.innerHTML = `
                <h2 style="margin-bottom: 15px; color: #2d3748;">${{video.title}}</h2>
                
                <div style="margin-bottom: 20px; color: #6c757d;">
                    <p><strong>Channel:</strong> ${{video.channel_name}}</p>
                    <p><strong>Published:</strong> ${{publishDate}}</p>
                    <p><strong>Views:</strong> ${{(video.view_count || 0).toLocaleString()}}</p>
                    <p><strong>Duration:</strong> ${{Math.floor((video.duration || 0) / 60)}} minutes</p>
                </div>
                
                <div style="margin: 15px 0;">
                    <strong>Topics:</strong>
                    <div class="topic-tags" style="margin-top: 8px;">
                        ${{topics.map(t => `<span class="topic-tag">${{t.topic}} (${{(t.confidence*100).toFixed(0)}}%)</span>`).join('')}}
                    </div>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>📝 Summary</h3>
                    <p style="line-height: 1.6; margin-top: 10px;">${{video.summary || 'No summary available'}}</p>
                </div>
                
                ${{video.key_insights ? `
                <div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #667eea;">
                    <h3>🔍 Key Insights</h3>
                    <div style="line-height: 1.8; margin-top: 10px;">${{video.key_insights.replace(/\\n/g, '<br>')}}</div>
                </div>
                ` : ''}}
                
                <a href="${{video.url}}" target="_blank" 
                   style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; 
                          text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: 600;">
                    ▶ Watch on YouTube
                </a>
            `;
            
            document.getElementById('videoModal').style.display = 'block';
        }}
        
        function closeModal() {{
            document.getElementById('videoModal').style.display = 'none';
        }}
        
        // Close modal on outside click
        window.onclick = function(event) {{
            const modal = document.getElementById('videoModal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}
        
        // Keyboard shortcut to close modal
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>"""
    
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Report generated: public/index.html")
    print(f"   Videos: {len(videos)}")
    print(f"   Channels: {len(channels)}")
    print(f"   Topics: {len(topics)}")

def generate_video_cards(videos):
    cards = []
    for video in videos[:50]:  
        topics = video.get('topics', [])
        topic_tags = ''.join([f'<span class="topic-tag">{t["topic"]}</span>' for t in topics[:3]])
        
        publish_date = video.get('published_at', '')[:10]
        views = f"{(video.get('view_count', 0)/1000):.1f}K views" if video.get('view_count') else ''
        summary = video.get('summary', '')[:150] + '...' if video.get('summary') else ''
        
        thumbnail = video.get('thumbnail_url', '')
        onerror = "this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22350%22 height=%22200%22%3E%3Crect fill=%22%23e9ecef%22 width=%22350%22 height=%22200%22/%3E%3Ctext fill=%22%236c757d%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3ENo Thumbnail%3C/text%3E%3C/svg%3E'"
        
        card = f"""
        <div class="video-card" onclick="showVideoDetail('{video['id']}')">
            <img src="{thumbnail}" class="video-thumbnail" alt="{video['title']}" loading="lazy" onerror="{onerror}">
            <div class="video-info">
                <div class="channel-name">📺 {video.get('channel_name', 'Unknown')}</div>
                <div class="video-title">{video.get('title', 'Untitled')}</div>
                <div class="topic-tags">{topic_tags}</div>
                <div class="video-meta">
                    <span> {publish_date}</span>
                    <span>👁 {views}</span>
                </div>
                <div class="summary-text">{summary}</div>
            </div>
        </div>"""
        cards.append(card)
    
    return '\n'.join(cards)

def generate_channel_cards(channels):
    cards = []
    for ch in channels:
        latest_video = ch.get('latest_video', '')[:10] if ch.get('latest_video') else 'N/A'
        cards.append(f"""
        <div class="channel-card">
            <h3>📺 {ch.get('channel_name', 'Unknown')}</h3>
            <p style="font-size: 28px; font-weight: bold; color: #667eea; margin: 10px 0;">{ch.get('video_count', 0)}</p>
            <p style="color: #6c757d;">Videos Analyzed</p>
            <p style="color: #6c757d; margin-top: 10px;">
                Avg. {(ch.get('average_views', 0)/1000):.1f}K views
            </p>
            <p style="color: #6c757d; font-size: 12px;">
                Latest: {latest_video}
            </p>
        </div>""")
    return '\n'.join(cards)

def generate_topic_cards(topics):
    cards = []
    for t in topics[:15]:  # Top 15 topics
        cards.append(f"""
        <div class="channel-card">
            <h3>🏷 {t['topic']}</h3>
            <p style="font-size: 28px; font-weight: bold; color: #667eea; margin: 10px 0;">{t['video_count']}</p>
            <p style="color: #6c757d;">Videos</p>
            <p style="color: #6c757d; margin-top: 10px;">
                Confidence: {(t['average_confidence']*100):.1f}%
            </p>
        </div>""")
    return '\n'.join(cards)

def generate_topic_buttons(topics):
    buttons = []
    for t in topics[:8]:  # Top 8 topics
        buttons.append(f'<button class="filter-btn" onclick="filterByTopic(\'{t["topic"]}\')">{t["topic"]}</button>')
    return '\n'.join(buttons)

if __name__ == "__main__":
    generate_report()
