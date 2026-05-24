import sys
import os
import logging
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the data pipeline and export results"""
    logger.info("Starting YouTube LLM Tracker Pipeline (GitHub Actions mode)")
    
    try:
        from database import Video, ChannelRelation, SessionLocal, Base, engine
        from youtube_fetcher import YouTubeFetcher
        from transcript_fetcher import TranscriptFetcher
        from ai_analyzer_hf_light import LightweightAnalyzer
        from config import Config
        
        Base.metadata.create_all(engine)
        
        youtube_fetcher = YouTubeFetcher()
        transcript_fetcher = TranscriptFetcher()
        analyzer = LightweightAnalyzer()
        
        db = SessionLocal()
        
        try:
            all_videos = []
            for channel_id, channel_name in Config.LLM_CHANNELS.items():
                logger.info(f"Fetching videos from {channel_name}...")
                try:
                    videos = youtube_fetcher.fetch_channel_videos(
                        channel_id,
                        max_results=10 
                    )
                    all_videos.extend(videos)
                    logger.info(f"Fetched {len(videos)} videos from {channel_name}")
                except Exception as e:
                    logger.error(f"Error fetching {channel_name}: {e}")
                    continue
            
            logger.info(f"Total videos fetched: {len(all_videos)}")
            
            processed_count = 0
            for video_data in all_videos:
                try:
                    video_id = video_data['id']
                    
                    existing = db.query(Video).filter(Video.id == video_id).first()
                    
                    if existing and existing.transcript_available:
                        logger.debug(f"Skipping {video_id} - already processed")
                        continue
                    
                    transcript, transcript_available = transcript_fetcher.get_transcript(video_id)
                    
                    text_for_analysis = transcript if transcript_available else video_data.get('description', '')
                    
                    summary = analyzer.generate_summary(text_for_analysis)
                    topics = analyzer.classify_topics(
                        transcript,
                        video_data['title'],
                        video_data['description']
                    )
                    key_insights = analyzer.extract_key_insights(
                        transcript or video_data.get('description', ''),
                        summary
                    )
                    
                    video_dict = {
                        'id': video_id,
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
                        'transcript_available': transcript_available,
                        'summary': summary,
                        'topics': json.dumps(topics),
                        'key_insights': key_insights,
                        'fetched_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    if existing:
                        for key, value in video_dict.items():
                            setattr(existing, key, value)
                    else:
                        db_video = Video(**video_dict)
                        db.add(db_video)
                    
                    processed_count += 1
                    logger.info(f"Processed: {video_data['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing video {video_data.get('id')}: {e}")
                    continue
            
            db.commit()
            logger.info(f"Pipeline complete. Processed {processed_count} new videos")
            
            export_data(db)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Pipeline error: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

def export_data(db):
    """Export database to JSON files for static site generation"""
    import json
    from datetime import datetime
    
    export_dir = 'public/data'
    os.makedirs(export_dir, exist_ok=True)
    
    videos = db.query(Video).order_by(Video.published_at.desc()).limit(100).all()
    videos_data = []
    for v in videos:
        video_dict = v.to_dict()
        if isinstance(video_dict.get('published_at'), datetime):
            video_dict['published_at'] = video_dict['published_at'].isoformat()
        videos_data.append(video_dict)
    
    with open(f'{export_dir}/videos.json', 'w') as f:
        json.dump(videos_data, f, indent=2)
    
    from sqlalchemy import func
    channels = db.query(
        Video.channel_id,
        Video.channel_name,
        func.count(Video.id).label('video_count'),
        func.avg(Video.view_count).label('avg_views'),
        func.max(Video.published_at).label('latest_video')
    ).group_by(Video.channel_id, Video.channel_name).all()
    
    channels_data = []
    for ch in channels:
        channels_data.append({
            'channel_id': ch.channel_id,
            'channel_name': ch.channel_name,
            'video_count': ch.video_count,
            'average_views': int(ch.avg_views) if ch.avg_views else 0,
            'latest_video': ch.latest_video.isoformat() if ch.latest_video else None
        })
    
    with open(f'{export_dir}/channels.json', 'w') as f:
        json.dump(channels_data, f, indent=2)
    
    all_videos = db.query(Video.topics).filter(Video.topics.isnot(None)).all()
    topic_counter = {}
    for (topics_json,) in all_videos:
        try:
            topics = json.loads(topics_json) if isinstance(topics_json, str) else topics_json
            for topic in topics:
                topic_name = topic['topic']
                confidence = topic['confidence']
                if topic_name not in topic_counter:
                    topic_counter[topic_name] = {'count': 0, 'total_confidence': 0}
                topic_counter[topic_name]['count'] += 1
                topic_counter[topic_name]['total_confidence'] += confidence
        except:
            continue
    
    topics_data = []
    for topic, stats in topic_counter.items():
        topics_data.append({
            'topic': topic,
            'video_count': stats['count'],
            'average_confidence': stats['total_confidence'] / stats['count']
        })
    topics_data.sort(key=lambda x: x['video_count'], reverse=True)
    
    with open(f'{export_dir}/topics.json', 'w') as f:
        json.dumps(topics_data, f, indent=2)
    
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(videos_data),
        'total_channels': len(channels_data),
        'version': '1.0.0'
    }
    
    with open(f'{export_dir}/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Exported data to {export_dir}/")

if __name__ == "__main__":
    main()
