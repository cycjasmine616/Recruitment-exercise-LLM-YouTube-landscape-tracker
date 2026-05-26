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
    logger.info("=" * 60)
    logger.info("LLM YOUTUBE LANDSCAPE TRACKER")
    logger.info("=" * 60)
    
    try:
        from config import Config
        from database import Video, Base, engine, SessionLocal
        from youtube_fetcher import YouTubeFetcher
        from transcript_fetcher import TranscriptFetcher
        from ai_analyzer_hf_light import LightweightAnalyzer
        
        if not Config.YOUTUBE_API_KEY:
            logger.error("No YouTube API key!")
            create_empty_files()
            return
        
        Base.metadata.create_all(engine)
        db = SessionLocal()
        fetcher = YouTubeFetcher()
        transcript_fetcher = TranscriptFetcher()
        analyzer = LightweightAnalyzer()
        
        logger.info("✓ Components initialized\n")
        
        all_videos = []
        
        logger.info("📡 FETCHING FROM LLM CHANNELS...")
        for channel_id, channel_name in Config.LLM_CHANNELS.items():
            try:
                videos = fetcher.fetch_channel_videos(channel_id, Config.MAX_VIDEOS_PER_CHANNEL)
                if videos:
                    logger.info(f"   {channel_name}: {len(videos)} videos")
                    all_videos.extend(videos)
                else:
                    logger.info(f"   {channel_name}: No videos found")
            except Exception as e:
                logger.error(f"   {channel_name}: Error - {e}")
        
        logger.info("\n SEARCHING FOR LLM CONTENT...")
        for query in Config.SEARCH_QUERIES[:3]:
            try:
                videos = fetcher.search_videos(query, Config.MAX_SEARCH_RESULTS)
                if videos:
                    logger.info(f"  ✓ '{query[:40]}...': {len(videos)} videos")
                    all_videos.extend(videos)
            except Exception as e:
                logger.error(f"  ✗ Search error: {e}")
        
        seen = set()
        unique_videos = []
        for v in all_videos:
            if v['id'] not in seen:
                seen.add(v['id'])
                unique_videos.append(v)
        
        logger.info(f"\n TOTAL UNIQUE VIDEOS: {len(unique_videos)}")
        
        if not unique_videos:
            logger.warning("No videos found!")
            create_empty_files()
            db.close()
            return
        
        logger.info("\n ANALYZING TRANSCRIPTS...")
        logger.info("-" * 60)
        
        processed = 0
        with_transcript = 0
        
        for i, video_data in enumerate(unique_videos, 1):
            try:
                vid = video_data['id']
                title = video_data['title'][:80]
                channel = video_data['channel_name']
                
                logger.info(f"\n[{i}/{len(unique_videos)}] {channel}")
                logger.info(f"   {title}")
                
                existing = db.query(Video).filter(Video.id == vid).first()
                if existing and existing.transcript_available:
                    logger.info("   Already analyzed with transcript")
                    processed += 1
                    with_transcript += 1
                    continue
                
                logger.info("   Fetching transcript...")
                transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                
                if has_transcript:
                    logger.info(f"   Got transcript ({len(transcript)} chars)")
                    with_transcript += 1
                    
                    analysis = analyzer.analyze_transcript(
                        transcript, title, video_data.get('description', '')
                    )
                    
                    summary = analysis['summary']
                    topics = analysis['topics']
                    quotes = analysis['key_quotes']
                    
                    if topics:
                        topic_names = [t['topic'] for t in topics[:3]]
                        logger.info(f"   Topics: {', '.join(topic_names)}")
                    
                    if quotes:
                        logger.info(f"   Key quotes: {len(quotes)} extracted")
                else:
                    logger.info("  ⚠ No transcript")
                    analysis = analyzer._fallback_analysis(
                        title, video_data.get('description', '')
                    )
                    summary = analysis['summary']
                    topics = analysis['topics']
                    quotes = []
                
                record = {
                    'id': vid,
                    'title': video_data['title'],
                    'description': video_data.get('description', ''),
                    'channel_id': video_data.get('channel_id', ''),
                    'channel_name': channel,
                    'published_at': video_data['published_at'],
                    'view_count': video_data.get('view_count', 0),
                    'thumbnail_url': video_data.get('thumbnail_url', ''),
                    'url': video_data['url'],
                    'transcript': transcript,
                    'transcript_available': has_transcript,
                    'transcript_excerpts': json.dumps(quotes),
                    'llm_topics_discussed': json.dumps(topics),
                    'key_claims': json.dumps([q['text'] for q in quotes]),
                    'practical_insights': summary,
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
                logger.info("   Saved")
                
            except Exception as e:
                logger.error(f"   Error: {e}")
                db.rollback()
                continue
        
        logger.info(f"\n Processed {processed} videos ({with_transcript} with transcripts)")
        
        logger.info("\n🔗 FINDING CHANNEL RELATIONSHIPS...")
        relationships = analyzer.find_channel_relationships(
            [v.to_dict() for v in db.query(Video).all()]
        )
        
        for rel in relationships[:10]:
            logger.info(f"  {rel['channel_1']} ↔ {rel['channel_2']}: {rel['similarity']:.0%} similar")
            logger.info(f"    {rel['relationship']}")
        
        export_data(db, relationships)
        
        db.close()
        logger.info("\n PIPELINE COMPLETE")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        create_empty_files()

def export_data(db, relationships):
    """Export to JSON files"""
    from database import Video
    
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
    
    with open('public/data/relations.json', 'w') as f:
        json.dump(relationships, f, indent=2)
    
    channels = list(set(v.get('channel_name', '') for v in videos_data))
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(videos_data),
        'total_channels': len(channels),
        'channels': channels,
        'total_relations': len(relationships),
        'videos_with_transcripts': sum(1 for v in videos_data if v.get('transcript_available'))
    }
    
    with open('public/data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f" Exported {len(videos_data)} videos and {len(relationships)} relationships")

def create_empty_files():
    """Create empty data files"""
    os.makedirs('public/data', exist_ok=True)
    
    with open('public/data/videos.json', 'w') as f:
        json.dump([], f)
    with open('public/data/relations.json', 'w') as f:
        json.dump([], f)
    with open('public/data/metadata.json', 'w') as f:
        json.dump({
            'last_updated': datetime.utcnow().isoformat(),
            'total_videos': 0,
            'total_channels': 0,
            'total_relations': 0
        }, f)

if __name__ == "__main__":
    main()
