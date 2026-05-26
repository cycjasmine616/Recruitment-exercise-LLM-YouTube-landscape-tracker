import json, os, re, requests
from datetime import datetime

print("Fetching LLM videos...")
API_KEY = os.getenv('YOUTUBE_API_KEY', '')
os.makedirs('public/data', exist_ok=True)

videos = []
queries = ["large language model tutorial", "GPT explained Andrej Karpathy", "transformer attention explained"]

for query in queries:
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=3&key={API_KEY}"
        r = requests.get(url).json()
        for item in r.get('items', []):
            vid = item['id']['videoId']
            videos.append({
                'id': vid, 'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'url': f"https://youtube.com/watch?v={vid}",
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'description': item['snippet'].get('description', '')[:300]
            })
    except Exception as e:
        print(f"Error: {e}")

seen = set()
unique = [v for v in videos if v['id'] not in seen and not seen.add(v['id'])]

topics_map = {
    "Transformer Architecture": ["transformer", "attention", "encoder"],
    "Model Training": ["training", "fine-tun", "RLHF"],
    "Prompt Engineering": ["prompt", "few-shot", "chain-of-thought"],
    "RAG Systems": ["RAG", "retrieval", "vector database"],
    "Safety": ["safety", "alignment", "bias"],
    "Open Source": ["open source", "Llama", "Mistral"],
    "AI Agents": ["agent", "LangChain", "tool use"],
}

videos_data = []
channels = {}
for v in unique:
    text = (v['title'] + ' ' + v['description']).lower()
    topics = [{'topic': t, 'mentions': 2} for t, kw in topics_map.items() if any(k in text for k in kw)]
    
    videos_data.append({
        'id': v['id'], 'title': v['title'], 'channel_name': v['channel'],
        'url': v['url'], 'thumbnail_url': v['thumbnail'],
        'llm_topics_discussed': topics[:4],
        'practical_insights': v['description'],
        'transcript_available': False
    })
    
    ch = v['channel']
    if ch not in channels: channels[ch] = set()
    for t in topics: channels[ch].add(t['topic'])

ch_names = list(channels.keys())
relations = []
for i, c1 in enumerate(ch_names):
    for c2 in ch_names[i+1:]:
        common = channels[c1] & channels[c2]
        all_t = channels[c1] | channels[c2]
        if common:
            relations.append({
                'channel_1': c1, 'channel_2': c2,
                'similarity': round(len(common)/len(all_t), 2),
                'common_topics': list(common)[:5],
                'relationship': f"Discuss: {', '.join(list(common)[:3])}"
            })

for name, data in [('videos', videos_data), ('relations', relations)]:
    with open(f'public/data/{name}.json', 'w') as f:
        json.dump(data, f, indent=2)

with open('public/data/metadata.json', 'w') as f:
    json.dump({'total_videos': len(videos_data), 'total_channels': len(channels),
               'total_relations': len(relations), 'last_updated': datetime.utcnow().isoformat()}, f)

rows = ""
for v in videos_data:
    t = ' '.join([f'<span class="tag">{x["topic"]}</span>' for x in v.get('llm_topics_discussed', [])[:4]])
    rows += f'<tr><td><span class="ch">{v["channel_name"]}</span></td><td><a href="{v["url"]}">{v["title"][:80]}</a></td><td>{t or "-"}</td><td style="font-size:12px;">{v.get("practical_insights","")[:200]}...</td></tr>'

rels = ""
for r in relations:
    t = ' '.join([f'<span class="tag">{x}</span>' for x in r['common_topics'][:4]])
    rels += f'<div class="rc"><h3>{r["channel_1"]} ↔ {r["channel_2"]}</h3><span class="s">{int(r["similarity"]*100)}%</span><p>{r["relationship"]}</p><div>{t}</div></div>'

html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>LLM YouTube Tracker</title><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:sans-serif;background:#f0f2f5;padding:20px;color:#333}}
.c{{max-width:1400px;margin:0 auto}}.h{{background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:30px;border-radius:12px;margin-bottom:25px;text-align:center}}
.st{{display:flex;justify-content:center;gap:25px;margin-top:20px}}
.sb{{background:rgba(255,255,255,0.12);padding:15px 25px;border-radius:10px}}
.sn{{font-size:30px;font-weight:bold}}table{{width:100%;background:white;border-collapse:collapse;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:30px}}
th{{background:#1a1a2e;color:white;padding:12px;text-align:left;font-size:13px}}td{{padding:10px 12px;border-bottom:1px solid #eee;font-size:13px}}
tr:hover{{background:#f8f9ff}}.ch{{background:#e8eaf6;color:#3949ab;padding:4px 12px;border-radius:12px;font-weight:600;font-size:12px;display:inline-block}}
.tag{{background:#e8f5e9;color:#2e7d32;padding:3px 8px;border-radius:10px;font-size:11px;margin:2px;display:inline-block}}
.rc{{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid #667eea;margin-bottom:15px}}
.s{{background:#667eea;color:white;padding:4px 12px;border-radius:15px;font-size:13px;font-weight:600}}
</style></head><body><div class="c">
<div class="h"><h1>🤖 LLM YouTube Landscape Tracker</h1><p>Analyzing LLM content across YouTube</p>
<div class="st"><div class="sb"><div class="sn">{len(videos_data)}</div>Videos</div>
<div class="sb"><div class="sn">{len(channels)}</div>Channels</div>
<div class="sb"><div class="sn">{len(relations)}</div>Relations</div></div></div>
<h2 style="margin:25px 0 15px">📊 Videos</h2>
<table><thead><tr><th>Channel</th><th>Video</th><th>LLM Topics</th><th>Description</th></tr></thead><tbody>{rows}</tbody></table>
<h2 style="margin:25px 0 15px">🔗 Channel Relationships</h2>
{rels if rels else '<p style="text-align:center;padding:20px;color:#888;">More channels needed</p>'}
</div></body></html>'''

with open('public/index.html', 'w') as f:
    f.write(html)

print(f"✅ Done! {len(videos_data)} videos, {len(channels)} channels, {len(relations)} relations")
