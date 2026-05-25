import sys
import os
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting YouTube LLM Tracker Pipeline")
    
    try:
        from config import Config
        from database import Video, SessionLocal, Base, engine
        from youtube_fetcher import YouTubeFetcher
        from transcript_fetcher import TranscriptFetcher
        from ai_analyzer_hf_light import LightweightAnalyzer
        
        if not Config.YOUTUBE_API_KEY:
            logger.error("❌ No YouTube API key found!")
            create_error_files("Missing API key")
            return
        
        logger.info(f"✓ API Key configured")

        Base.metadata.create_all(engine)
        logger.info("✓ Database ready")
        
        fetcher = YouTubeFetcher()
        transcript_fetcher = TranscriptFetcher()
        analyzer = LightweightAnalyzer()
        
        logger.info("Fetching LLM videos from YouTube...")
        all_videos = fetcher.fetch_all_videos()
        
        if not all_videos:
            logger.warning("No videos found. Creating empty data files.")
            create_empty_files()
            return
        
        logger.info(f"Found {len(all_videos)} videos. Processing...")
        
        db = SessionLocal()
        processed = 0
        
        try:
            for i, video_data in enumerate(all_videos, 1):
                try:
                    vid = video_data['id']
                    title = video_data['title'][:80]
                    
                    logger.info(f"[{i}/{len(all_videos)}] {title}")
                    
                    existing = db.query(Video).filter(Video.id == vid).first()
                    if existing and existing.transcript_available:
                        logger.info("  Already processed with transcript")
                        continue
                    
                    transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                    
                    text = transcript if has_transcript else video_data.get('description', '')
                    summary = analyzer.generate_summary(text)
                    topics = analyzer.classify_topics(transcript, title, video_data.get('description', ''))
                    insights = analyzer.extract_key_insights(transcript or text, summary)
                    
                    record = {
                        'id': vid,
                        'title': video_data['title'],
                        'description': video_data.get('description', ''),
                        'channel_id': video_data.get('channel_id', ''),
                        'channel_name': video_data.get('channel_name', 'Unknown'),
                        'published_at': video_data['published_at'],
                        'view_count': video_data.get('view_count', 0),
                        'thumbnail_url': video_data.get('thumbnail_url', ''),
                        'url': video_data['url'],
                        'transcript': transcript,
                        'transcript_available': has_transcript,
                        'summary': summary,
                        'topics': json.dumps(topics),
                        'key_insights': insights,
                        'fetched_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    if existing:
                        for k, v in record.items():
                            setattr(existing, k, v)
                    else:
                        db.add(Video(**record))
                    
                    db.commit()
                    processed += 1
                    logger.info("  ✓ Saved")
                    
                except Exception as e:
                    logger.error(f"  Error: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"Processed {processed} videos")
            
            export_videos(db)
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

def export_videos(db):
    """Export videos to JSON files"""
    os.makedirs('public/data', exist_ok=True)
    
    videos = db.query(Video).order_by(Video.published_at.desc()).all()
    
    videos_data = []
    for v in videos:
        try:
            d = v.to_dict()
            videos_data.append(d)
        except:
            continue
    
    with open('public/data/videos.json', 'w') as f:
        json.dump(videos_data, f, indent=2, default=str)
    
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(videos_data),
        'total_channels': len(set(v.channel_name for v in videos))
    }
    
    with open('public/data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Exported {len(videos_data)} videos to JSON")

def create_empty_files():
    """Create empty data files"""
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/videos.json', 'w') as f:
        json.dump([], f)
    with open('public/data/metadata.json', 'w') as f:
        json.dump({'last_updated': datetime.utcnow().isoformat(), 'total_videos': 0}, f)

def create_error_files(error):
    """Create error data files"""
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/videos.json', 'w') as f:
        json.dump([], f)
    with open('public/data/metadata.json', 'w') as f:
        json.dump({
            'last_updated': datetime.utcnow().isoformat(),
            'total_videos': 0,
            'error': error
        }, f)

if __name__ == "__main__":
    main()
