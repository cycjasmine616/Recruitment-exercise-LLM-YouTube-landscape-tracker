import os
import json
import feedparser
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from datetime import datetime

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com"
)

CHANNELS = {
    "Matthew Berman": "https://www.youtube.com/feeds/videos.xml?channel_id=UCabgeZzWzN_A3W1kG2_G3Gg",
    "Yannic Kilcher": "https://www.youtube.com/feeds/videos.xml?channel_id=UCzhxO7x8Y0-s_L06T_yA8GA",
    "The AI Epiphany": "https://www.youtube.com/feeds/videos.xml?channel_id=UC0Z0Q9r-mO6QnL5D49e49OQ"
}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CSV_FILE = os.path.join(BASE_DIR, "tracker_data.csv")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

def get_transcript(video_id):
    """Uses basic networking to download the YouTube captions."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript_list])
        return text[:15000] 
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None

def analyze_with_ai(transcript, channel_name, video_title):
    """Sends the transcript to DeepSeek AI and asks it to extract specific details."""
    
    prompt = f"""
    Analyze this YouTube video transcript.
    Channel: {channel_name}
    Title: {video_title}
    
    Extract these details and reply ONLY in JSON format:
    - "speaker": The name of the person speaking.
    - "topics": A list of technical topics discussed.
    - "summary": A 2-sentence summary of the video.
    - "channel_relations": How this channel relates to other AI channels.
    
    Transcript: {transcript}
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={ "type": "json_object" }, 
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

def run_watcher():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        processed_vids = set(df['video_id'].tolist())
    else:
        columns = ["video_id", "channel", "video_title", "speaker", "topics", "summary", "channel_relations"]
        df = pd.DataFrame(columns=columns)
        processed_vids = set()
        
    new_rows = []
    
    for channel_name, feed_url in CHANNELS.items():
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue
        
        for video in feed.entries[:5]:
            video_id = video.yt_videoid
            title = video.title
            
            if video_id not in processed_vids:
                print(f"Processing video: {title}")
                transcript = get_transcript(video_id)
                
                if transcript:
                    print("Analyzing with DeepSeek AI...")
                    analysis = analyze_with_ai(transcript, channel_name, title)
                    
                    new_row = {
                        "video_id": video_id,
                        "channel": channel_name,
                        "video_title": title,
                        "speaker": analysis.get("speaker", "Unknown"),
                        "topics": analysis.get("topics", ""),
                        "summary": analysis.get("summary", ""),
                        "channel_relations": analysis.get("channel_relations", "")
                    }
                    new_rows.append(new_row)
                    processed_vids.add(video_id)
                else:
                    print(f"Skipping video: {title} (No transcript found)")

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([new_df, df], ignore_index=True)
        
        df.to_csv(CSV_FILE, index=False)
        
        display_df = df.drop(columns=['video_id']) 
        html_table = display_df.to_html(index=False, border=0, classes="dataframe")
        
        html_page = f"""
        <html>
        <head>
            <title>LLM YouTube Tracker</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table.dataframe {{ width: 100%; border-collapse: collapse; text-align: left; }}
                table.dataframe th {{ background-color: #333; color: white; padding: 10px; }}
                table.dataframe td {{ border-bottom: 1px solid #ddd; padding: 10px; }}
            </style>
        </head>
        <body>
            <h1>YouTube LLM Landscape Tracker</h1>
            <p>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            {html_table}
        </body>
        </html>
        """
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html_page)
            
        print("Successfully updated CSV and HTML!")
    else:
        print("No new videos found.")

if __name__ == "__main__":
    run_watcher()
