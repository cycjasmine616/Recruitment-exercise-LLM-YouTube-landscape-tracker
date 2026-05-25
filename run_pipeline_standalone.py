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
        from database import Video, ChannelRelation, SessionLocal, Base, engine
        from youtube_fetcher import YouTubeFetcher
        from transcript_fetcher import TranscriptFetcher
        from ai_analyzer_hf_light import LightweightAnalyzer
        
        if not Config.YOUTUBE_API_KEY:
            logger.error("No API key!")
            create_fallback_files()
            return
        
        Base.metadata.create_all(engine)
        db = SessionLocal()
        fetcher = YouTubeFetcher()
        transcript_fetcher = TranscriptFetcher()
        analyzer = LightweightAnalyzer()
        
        all_videos = []
        
        if Config.LLM_CHANNELS:
            logger.info("Fetching from LLM channels...")
            for channel_id, channel_name in Config.LLM_CHANNELS.items():
                try:
                    videos = fetcher.fetch_channel_videos(channel_id, Config.MAX_VIDEOS_PER_CHANNEL)
                    all_videos.extend(videos)
                    logger.info(f"  {channel_name}: {len(videos)} videos")
                except Exception as e:
                    logger.error(f"  {channel_name}: Failed - {e}")
        
        if not all_videos and Config.USE_SEARCH:
            logger.info("No channel videos found. Using search...")
            for query in Config.LLM_SEARCH_QUERIES[:2]:  
                try:
                    videos = fetcher.search_videos(query, Config.MAX_SEARCH_RESULTS)
                    all_videos.extend(videos)
                except Exception as e:
                    logger.error(f"Search failed: {e}")
        
        if not all_videos:
            logger.warning("No videos found. Creating sample data.")
            create_fallback_files()
            db.close()
            return
        
        seen = set()
        unique_videos = []
        for v in all_videos:
            if v['id'] not in seen:
                seen.add(v['id'])
                unique_videos.append(v)
        
        logger.info(f"\nProcessing {len(unique_videos)} unique videos...")
        logger.info("-" * 60)
        
        processed = 0
        for i, video_data in enumerate(unique_videos, 1):
            try:
                vid = video_data['id']
                title = video_data.get('title', 'Unknown')[:80]
                channel = video_data.get('channel_name', 'Unknown')
                
                logger.info(f"[{i}/{len(unique_videos)}] {channel}: {title}")
                
                existing = db.query(Video).filter(Video.id == vid).first()
                if existing and existing.transcript_available:
                    logger.info("  Already has transcript - skipping")
                    continue
                
                logger.info("  Fetching transcript...")
                transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                
                if has_transcript:
                    logger.info(f"  ✓ Got {len(transcript)} chars")
                    
                    analysis = analyzer.analyze_transcript_deep(
                        transcript, title, video_data.get('description', '')
                    )
                else:
                    logger.info("  ⚠ No transcript")
                    analysis = analyzer._analyze_from_description(
                        title, video_data.get('description', '')
                    )
                
                record = {
                    'id': vid,
                    'title': title,
                    'description': video_data.get('description', ''),
                    'channel_id': video_data.get('channel_id', ''),
                    'channel_name': channel,
                    'published_at': video_data.get('published_at', datetime.utcnow()),
                    'view_count': video_data.get('view_count', 0),
                    'thumbnail_url': video_data.get('thumbnail_url', ''),
                    'url': video_data.get('url', ''),
                    'transcript': transcript,
                    'transcript_available': has_transcript,
                    'transcript_excerpts': json.dumps(analysis.get('transcript_excerpts', [])),
                    'llm_topics_discussed': json.dumps(analysis.get('topics_discussed', [])),
                    'technical_depth': analysis.get('technical_depth', 'Unknown'),
                    'creator_stance': analysis.get('creator_stance', 'Unknown'),
                    'key_claims': json.dumps(analysis.get('key_claims', [])),
                    'practical_insights': analysis.get('practical_insights', ''),
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
        
        logger.info(f"\n Processed {processed} videos")
        
        try:
            from database import Video as V, ChannelRelation as CR
            channels = db.query(V.channel_id, V.channel_name).distinct().all()
            
            channel_data = {}
            for ch_id, ch_name in channels:
                videos_list = db.query(V).filter(
                    V.channel_id == ch_id,
                    V.llm_topics_discussed.isnot(None)
                ).all()
                if videos_list:
                    channel_data[ch_id] = videos_list
            
            relationships = analyzer.calculate_channel_relationships(channel_data)
            
            for rel in relationships:
                existing_rel = db.query(CR).filter(
                    ((CR.channel_name_1 == rel['channel_1']) & (CR.channel_name_2 == rel['channel_2'])) |
                    ((CR.channel_name_1 == rel['channel_2']) & (CR.channel_name_2 == rel['channel_1']))
                ).first()
                
                if existing_rel:
                    existing_rel.similarity_score = rel['similarity_score']
                    existing_rel.common_topics = json.dumps(rel['common_topics'])
                    existing_rel.relationship_description = rel.get('description', '')
                    existing_rel.last_updated = datetime.utcnow()
                else:
                    db.add(CR(
                        channel_name_1=rel['channel_1'],
                        channel_name_2=rel['channel_2'],
                        similarity_score=rel['similarity_score'],
                        common_topics=json.dumps(rel['common_topics']),
                        relationship_description=rel.get('description', '')
                    ))
            
            db.commit()
            logger.info(f"Saved {len(relationships)} channel relationships")
        except Exception as e:
            logger.error(f"Relationship calculation error: {e}")
        
        export_data(db)
        db.close()
        
        logger.info("\n PIPELINE COMPLETE")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        create_fallback_files()

def export_data(db):
    """Export all data to JSON"""
    from database import Video, ChannelRelation
    
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
    
    relations = db.query(ChannelRelation).all()
    relations_data = []
    for r in relations:
        relations_data.append({
            'channel_1': r.channel_name_1,
            'channel_2': r.channel_name_2,
            'similarity_score': r.similarity_score,
            'common_topics': json.loads(r.common_topics) if isinstance(r.common_topics, str) else r.common_topics,
            'description': r.relationship_description
        })
    
    with open('public/data/relations.json', 'w') as f:
        json.dump(relations_data, f, indent=2)
    
    channels_count = len(set(v.get('channel_name', '') for v in videos_data))
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(videos_data),
        'total_channels': channels_count,
        'total_relations': len(relations_data)
    }
    
    with open('public/data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f" Exported {len(videos_data)} videos, {len(relations_data)} relations")

def create_fallback_files():
    """Create fallback files if pipeline fails"""
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
    
    logger.info("Created fallback data files")

if __name__ == "__main__":
    main()
