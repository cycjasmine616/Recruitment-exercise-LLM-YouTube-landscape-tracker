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
            all_videos = []
            
            if Config.USE_SEARCH and Config.SEARCH_QUERIES:
                logger.info("=" * 60)
                logger.info("SEARCHING FOR LLM CONTENT...")
                logger.info("=" * 60)
                
                for query in Config.SEARCH_QUERIES:
                    try:
                        logger.info(f"\nSearching: '{query}'")
                        videos = fetcher.search_llm_videos(query, Config.MAX_SEARCH_RESULTS)
                        
                        llm_keywords = ['llm', 'gpt', 'language model', 'transformer', 'rag', 
                                      'prompt', 'fine-tun', 'embedding', 'chatgpt', 'claude',
                                      'llama', 'mistral', 'gemini', 'copilot']
                        
                        relevant = []
                        for v in videos:
                            title_lower = v['title'].lower()
                            desc_lower = v.get('description', '').lower()
                            combined = title_lower + ' ' + desc_lower
                            
                            if any(kw in combined for kw in llm_keywords):
                                relevant.append(v)
                                logger.info(f"  ✓ LLM: {v['title'][:80]}")
                            else:
                                logger.debug(f"  ✗ Not LLM: {v['title'][:80]}")
                        
                        all_videos.extend(relevant)
                        logger.info(f"  Found {len(relevant)} relevant out of {len(videos)} total")
                        
                    except Exception as e:
                        logger.error(f"Search failed for '{query}': {e}")
            
            if Config.LLM_CHANNELS:
                logger.info("\n" + "=" * 60)
                logger.info("FETCHING FROM MONITORED CHANNELS...")
                logger.info("=" * 60)
                
                for channel_id, channel_name in Config.LLM_CHANNELS.items():
                    try:
                        logger.info(f"\nFetching from {channel_name}...")
                        videos = fetcher.fetch_channel_videos(channel_id, Config.MAX_VIDEOS_PER_CHANNEL)
                        
                        if videos:
                            logger.info(f"  Got {len(videos)} videos")
                            all_videos.extend(videos)
                        else:
                            logger.warning(f"  No videos found for {channel_name}")
                            
                    except Exception as e:
                        logger.error(f"Channel fetch failed for {channel_name}: {e}")
            
            seen_ids = set()
            unique_videos = []
            for v in all_videos:
                if v['id'] not in seen_ids:
                    seen_ids.add(v['id'])
                    unique_videos.append(v)
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"TOTAL UNIQUE VIDEOS: {len(unique_videos)}")
            logger.info(f"{'=' * 60}")
            
            if not unique_videos:
                logger.warning("No videos found! Check API key and quotas.")
                create_empty_data()
                return
            
            logger.info("\nPROCESSING VIDEOS...")
            logger.info("-" * 60)
            
            processed = 0
            skipped = 0
            failed = 0
            
            for i, video_data in enumerate(unique_videos, 1):
                try:
                    vid = video_data['id']
                    title = video_data['title'][:80]
                    channel = video_data.get('channel_name', 'Unknown')
                    
                    logger.info(f"\n[{i}/{len(unique_videos)}] Processing: {title}")
                    logger.info(f"  Channel: {channel}")
                    
                    existing = db.query(Video).filter(Video.id == vid).first()
                    if existing and existing.transcript_available:
                        logger.info(f"  ↳ Already processed with transcript - skipping")
                        skipped += 1
                        continue
                    
                    logger.info(f"  Fetching transcript...")
                    transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                    
                    if has_transcript:
                        logger.info(f"  ✓ Transcript available ({len(transcript)} chars)")
                    else:
                        logger.info(f"  ⚠ No transcript - using description only")
                    
                    text_for_analysis = transcript if has_transcript else video_data.get('description', '')
                    
                    logger.info(f"  Generating summary...")
                    summary = analyzer.generate_summary(text_for_analysis)
                    
                    logger.info(f"  Classifying topics...")
                    topics = analyzer.classify_topics(
                        transcript, 
                        video_data['title'], 
                        video_data.get('description', '')
                    )
                    
                    logger.info(f"  Extracting insights...")
                    insights = analyzer.extract_key_insights(
                        transcript or video_data.get('description', ''),
                        summary
                    )
                    
                    topic_names = [f"{t['topic']}({t['confidence']:.0%})" for t in topics[:3]]
                    logger.info(f"  Topics: {', '.join(topic_names)}")
                    logger.info(f"  Summary: {summary[:100]}...")
                    
                    record = {
                        'id': vid,
                        'title': video_data['title'],
                        'description': video_data.get('description', ''),
                        'channel_id': video_data['channel_id'],
                        'channel_name': channel,
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
                    logger.info(f"  ✅ Successfully saved to database")
                    
                except Exception as e:
                    logger.error(f"  ❌ Error: {e}")
                    db.rollback()
                    failed += 1
                    continue
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"PIPELINE COMPLETE")
            logger.info(f"{'=' * 60}")
            logger.info(f"  ✅ Processed: {processed}")
            logger.info(f"  ⏭️  Skipped: {skipped}")
            logger.info(f"  ❌ Failed: {failed}")
            logger.info(f"  📊 Total in DB: {db.query(Video).count()}")
            
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

def create_empty_data():
    """Create empty data files so the page still works"""
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/videos.json', 'w') as f:
        json.dump([], f)
    with open('public/data/channels.json', 'w') as f:
        json.dump([], f)
    with open('public/data/metadata.json', 'w') as f:
        json.dump({
            'last_updated': datetime.utcnow().isoformat(),
            'total_videos': 0,
            'total_channels': 0,
            'status': 'No videos found - check API key'
        }, f)
    logger.info("Created empty data files")

def export_to_json(db):
    """Export database to JSON files"""
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
    } for c in channels if c[0]]
    
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
    
    logger.info(f"Exported: {len(videos_data)} videos from {len(channels_data)} channels")
    logger.info(f"Data saved to public/data/")

if __name__ == "__main__":
    main()
