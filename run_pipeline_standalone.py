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
    logger.info("LLM YOUTUBE LANDSCAPE TRACKER - DEEP ANALYSIS MODE")
    logger.info("=" * 60)
    
    try:
        from config import Config
        from database import Video, ChannelRelation, SessionLocal, Base, engine
        from youtube_fetcher import YouTubeFetcher
        from transcript_fetcher import TranscriptFetcher
        from ai_analyzer_hf_light import LightweightAnalyzer
        
        if not Config.YOUTUBE_API_KEY:
            logger.error(" No API key!")
            return
        
        Base.metadata.create_all(engine)
        db = SessionLocal()
        fetcher = YouTubeFetcher()
        transcript_fetcher = TranscriptFetcher()
        analyzer = LightweightAnalyzer()
        
        logger.info("✓ All components initialized")
        
        logger.info("\n📡 FETCHING FROM LLM CHANNELS...")
        all_videos = fetcher.fetch_all_channels()
        
        if not all_videos:
            logger.error("No videos found!")
            return
        
        logger.info(f"\n ANALYZING {len(all_videos)} VIDEOS...")
        logger.info("-" * 60)
        
        processed = 0
        for i, video_data in enumerate(all_videos, 1):
            try:
                vid = video_data['id']
                title = video_data['title'][:80]
                channel = video_data['channel_name']
                
                logger.info(f"\n[{i}/{len(all_videos)}] {channel}")
                logger.info(f"  📹 {title}")
                
                existing = db.query(Video).filter(Video.id == vid).first()
                if existing and existing.transcript_available and existing.llm_topics_discussed:
                    logger.info("  ✓ Already analyzed with transcript")
                    continue
                
                logger.info("   Fetching transcript...")
                transcript, has_transcript = transcript_fetcher.get_transcript(vid)
                
                if has_transcript:
                    logger.info(f"  ✓ Transcript: {len(transcript)} characters")
                    
                    logger.info("   Analyzing LLM content...")
                    analysis = analyzer.analyze_transcript_deep(
                        transcript, 
                        title, 
                        video_data.get('description', '')
                    )
                    
                    topics = analysis['topics_discussed']
                    if topics:
                        topic_names = [f"{t['topic']}" for t in topics[:3]]
                        logger.info(f"   LLM Topics: {', '.join(topic_names)}")
                    
                    logger.info(f"   Technical Depth: {analysis['technical_depth']}")
                    logger.info(f"   Creator Stance: {analysis['creator_stance']}")
                    
                    record = {
                        'id': vid,
                        'title': title,
                        'description': video_data.get('description', ''),
                        'channel_id': video_data.get('channel_id', ''),
                        'channel_name': channel,
                        'published_at': video_data['published_at'],
                        'view_count': video_data.get('view_count', 0),
                        'thumbnail_url': video_data.get('thumbnail_url', ''),
                        'url': video_data['url'],
                        'transcript': transcript,
                        'transcript_available': True,
                        'transcript_excerpts': json.dumps(analysis['transcript_excerpts']),
                        'llm_topics_discussed': json.dumps(analysis['topics_discussed']),
                        'technical_depth': analysis['technical_depth'],
                        'creator_stance': analysis['creator_stance'],
                        'key_claims': json.dumps(analysis['key_claims']),
                        'practical_insights': analysis['practical_insights'],
                        'fetched_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                else:
                    logger.info("  ⚠ No transcript available - using description only")
                    analysis = analyzer._analyze_from_description(
                        title, 
                        video_data.get('description', '')
                    )
                    
                    record = {
                        'id': vid,
                        'title': title,
                        'description': video_data.get('description', ''),
                        'channel_id': video_data.get('channel_id', ''),
                        'channel_name': channel,
                        'published_at': video_data['published_at'],
                        'view_count': video_data.get('view_count', 0),
                        'thumbnail_url': video_data.get('thumbnail_url', ''),
                        'url': video_data['url'],
                        'transcript': None,
                        'transcript_available': False,
                        'transcript_excerpts': json.dumps([]),
                        'llm_topics_discussed': json.dumps(analysis['topics_discussed']),
                        'technical_depth': analysis['technical_depth'],
                        'creator_stance': analysis['creator_stance'],
                        'key_claims': json.dumps([]),
                        'practical_insights': analysis['practical_insights'],
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
                logger.info("  Saved to database")
                
            except Exception as e:
                logger.error(f"   Error: {e}")
                db.rollback()
                continue
        
        logger.info(f"\n Processed {processed} videos with deep analysis")
        
        logger.info("\n🔗 CALCULATING CHANNEL RELATIONSHIPS...")
        calculate_channel_relationships(db, analyzer)
        
        logger.info("\n📤 EXPORTING DATA...")
        export_all_data(db)
        
        db.close()
        logger.info("\n" + "=" * 60)
        logger.info(" PIPELINE COMPLETE")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

def calculate_channel_relationships(db, analyzer):
    """Calculate how channels relate on LLM themes"""
    from database import ChannelRelation
    
    channels = db.query(Video.channel_id, Video.channel_name).distinct().all()
    
    channel_videos = {}
    for ch_id, ch_name in channels:
        videos = db.query(Video).filter(
            Video.channel_id == ch_id,
            Video.llm_topics_discussed.isnot(None)
        ).all()
        if videos:
            channel_videos[ch_id] = videos
    
    relationships = analyzer.calculate_channel_relationships(channel_videos)
    
    for rel in relationships:
        existing = db.query(ChannelRelation).filter(
            ((ChannelRelation.channel_name_1 == rel['channel_1']) & 
             (ChannelRelation.channel_name_2 == rel['channel_2'])) |
            ((ChannelRelation.channel_name_1 == rel['channel_2']) & 
             (ChannelRelation.channel_name_2 == rel['channel_1']))
        ).first()
        
        if existing:
            existing.similarity_score = rel['similarity_score']
            existing.common_topics = json.dumps(rel['common_topics'])
            existing.relationship_description = rel['description']
            existing.last_updated = datetime.utcnow()
        else:
            db.add(ChannelRelation(
                channel_name_1=rel['channel_1'],
                channel_name_2=rel['channel_2'],
                similarity_score=rel['similarity_score'],
                common_topics=json.dumps(rel['common_topics']),
                relationship_description=rel['description'],
                last_updated=datetime.utcnow()
            ))
        
        logger.info(f"  {rel['channel_1']} ↔ {rel['channel_2']}: {rel['similarity_score']:.2%}")
    
    db.commit()
    logger.info(f"Saved {len(relationships)} channel relationships")

def export_all_data(db):
    """Export all data to JSON files"""
    import os
    os.makedirs('public/data', exist_ok=True)
    
    videos = db.query(Video).order_by(Video.published_at.desc()).all()
    videos_data = []
    
    for v in videos:
        try:
            d = v.to_dict()
            videos_data.append(d)
        except Exception as e:
            logger.error(f"Export error for {v.id}: {e}")
    
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
    
    channels = {}
    for v in videos_data:
        ch = v.get('channel_name', 'Unknown')
        if ch not in channels:
            channels[ch] = {'count': 0, 'topics': set()}
        channels[ch]['count'] += 1
        if v.get('llm_topics_discussed'):
            for t in v['llm_topics_discussed']:
                channels[ch]['topics'].add(t['topic'])
    
    metadata = {
        'last_updated': datetime.utcnow().isoformat(),
        'total_videos': len(videos_data),
        'total_channels': len(channels),
        'total_relations': len(relations_data),
        'channels': [{
            'name': k,
            'video_count': v['count'],
            'topics_covered': list(v['topics'])
        } for k, v in channels.items()]
    }
    
    with open('public/data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f" Exported: {len(videos_data)} videos, {len(relations_data)} relations")

if __name__ == "__main__":
    main()
