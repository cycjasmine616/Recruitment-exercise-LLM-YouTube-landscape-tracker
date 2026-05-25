import sys
import os
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting pipeline")
    
    try:
        from database import Video, SessionLocal, Base, engine
        from youtube_fetcher import YouTubeFetcher
        from transcript_fetcher import TranscriptFetcher
        from ai_analyzer_hf_light import LightweightAnalyzer
        from config import Config
        
        Base.metadata.create_all(engine)
        
        fetcher = YouTubeFetcher()
        transcript_fetcher = TranscriptFetcher()
        analyzer = LightweightAnalyzer()
        
        db = SessionLocal()
        
        try:
            all_videos = []
            for channel_id, channel_name in Config.LLM_CHANNELS.items():
                logger.info(f"Fetching {channel_name}...")
                videos = fetcher.fetch_channel_videos(channel_id, Config.MAX_VIDEOS_PER_CHANNEL)
                all_videos.extend(videos)
            
            logger.info(f"Total: {len(all_videos)} videos")
            
            for video_data in all_videos:
                try:
                    vid = video_data['id']
                    existing = db.query(Video).filter(Video.id == vid).first()
                    if existing and existing.transcript_available:
                        continue
                    
                    transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                    text = transcript if has_transcript else video_data.get('description', '')
                    
                    summary = analyzer.generate_summary(text)
                    topics = analyzer.classify_topics(transcript, video_data['title'], video_data.get('description', ''))
                    insights = analyzer.extract_key_insights(transcript or '', summary)
                    
                    record = {
                        'id': vid,
                        'title': video_data['title'],
                        'description': video_data.get('description', ''),
                        'channel_id': video_data['channel_id'],
                        'channel_name': video_data['channel_name'],
                        'published_at': video_data['published_at'],
                        'duration': video_data.get('duration', 0),
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
                    logger.info(f"✓ {video_data['title'][:50]}")
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
                    db.rollback()
                    continue
            
            os.makedirs('public/data', exist_ok=True)
            videos_list = db.query(Video).order_by(Video.published_at.desc()).limit(50).all()
            
            export_data = []
            for v in videos_list:
                d = v.to_dict()
                if isinstance(d.get('published_at'), datetime):
                    d['published_at'] = d['published_at'].isoformat()
                export_data.append(d)
            
            with open('public/data/videos.json', 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(export_data)} videos")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
