import sys
import os
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting YouTube LLM Tracker Pipeline")
    
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
            logger.info("Fetching videos from all sources...")
            all_videos = fetcher.fetch_all_content()
            
            if not all_videos:
                logger.error("No videos found! Check API key and quotas.")
                os.makedirs('public/data', exist_ok=True)
                with open('public/data/videos.json', 'w') as f:
                    json.dump([], f)
                with open('public/data/metadata.json', 'w') as f:
                    json.dump({
                        'last_updated': datetime.utcnow().isoformat(),
                        'total_videos': 0,
                        'total_channels': 0
                    }, f)
                return
            
            logger.info(f"Processing {len(all_videos)} videos...")
            
            processed = 0
            for video_data in all_videos:
                try:
                    vid = video_data['id']
                    
                    existing = db.query(Video).filter(Video.id == vid).first()
                    if existing and existing.transcript_available:
                        logger.debug(f"Skipping {vid} - already has transcript")
                        continue
                    
                    transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                    
                    text = transcript if has_transcript else video_data.get('description', '')
                    
                    summary = analyzer.generate_summary(text)
                    topics = analyzer.classify_topics(
                        transcript, 
                        video_data['title'], 
                        video_data.get('description', '')
                    )
                    insights = analyzer.extract_key_insights(
                        transcript or video_data.get('description', ''),
                        summary
                    )
                    
                    record = {
                        'id': vid,
                        'title': video_data['title'],
                        'description': video_data.get('description', ''),
                        'channel_id': video_data['channel_id'],
                        'channel_name': video_data.get('channel_name', 'Unknown'),
                        'published_at': video_data['published_at'],
                        'duration': video_data.get('duration', 0),
                        'view_count': video_data.get('view_count', 0),
                        'like_count': video_data.get('like_count', 0),
                        'comment_count': video_data.get('comment_count', 0),
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
                    
                    channel = video_data.get('channel_name', 'Unknown')
                    title = video_data['title'][:50]
                    topic_names = [t['topic'] for t in topics[:3]]
                    logger.info(f"✓ [{channel}] {title}... | Topics: {', '.join(topic_names)}")
                    
                except Exception as e:
                    logger.error(f"Error processing {video_data.get('id')}: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"Successfully processed {processed} videos")
            
            export_to_json(db)
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def export_to_json(db):
    """Export all data to JSON files"""
    import os
    
    os.makedirs('public/data', exist_ok=True)
    
    videos = db.query(Video).order_by(Video.published_at.desc()).limit(100).all()
    videos_data = []
    for v in videos:
        d = v.to_dict()
        if isinstance(d.get('published_at'), datetime):
            d['published_at'] = d['published_at'].isoformat()
        videos_data.append(d)
    
    with open('public/data/videos.json', 'w') as f:
        json.dump(videos_data, f, indent=2)
    
    from sqlalchemy import func
    channels = db.query(
        Video.channel_name,
        func.count(Video.id).label('count'),
        func.avg(Video.view_count).label('avg_views')
    ).group_by(Video.channel_name).all()
    
    channels_data = [{
        'name': c[0],
        'video_count': c[1],
        'avg_views': int(c[2]) if c[2] else 0
    } for c in channels]
    
    with open('public/data/channels.json', 'w') as f:
        json.dump(channels_data, f, indent=2)
    
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(videos_data),
        'total_channels': len(channels_data),
        'channels': channels_data
    }
    
    with open('public/data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Exported {len(videos_data)} videos from {len(channels_data)} channels")

if __name__ == "__main__":
    main()
