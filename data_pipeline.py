from database import Video, ChannelRelation, SessionLocal
from youtube_fetcher import YouTubeFetcher
from transcript_fetcher import TranscriptFetcher
from ai_analyzer_hf import HuggingFaceAnalyzer
from config import Config
import logging
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self):
        self.youtube_fetcher = YouTubeFetcher()
        self.transcript_fetcher = TranscriptFetcher()
        self.ai_analyzer = HuggingFaceAnalyzer()
    
    def run_pipeline(self):
        """Execute the full data collection and analysis pipeline"""
        logger.info("Starting data pipeline with Hugging Face models...")
        
        db = SessionLocal()
        try:
            all_videos = []
            for channel_id, channel_name in Config.LLM_CHANNELS.items():
                logger.info(f"Fetching videos from {channel_name}...")
                videos = self.youtube_fetcher.fetch_channel_videos(
                    channel_id, 
                    Config.MAX_VIDEOS_PER_CHANNEL
                )
                all_videos.extend(videos)
            
            logger.info(f"Fetched {len(all_videos)} videos total")
            
            processed_count = 0
            for video_data in all_videos:
                try:
                    self.process_video(db, video_data)
                    processed_count += 1
                    if processed_count % 10 == 0:
                        logger.info(f"Processed {processed_count}/{len(all_videos)} videos")
                except Exception as e:
                    logger.error(f"Error processing video {video_data.get('id')}: {e}")
                    continue
            
            self.update_channel_relations(db)
            
            self.update_video_relations(db)
            
            db.commit()
            logger.info(f"Pipeline complete. Processed {processed_count} videos.")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Pipeline error: {e}")
            raise
        finally:
            db.close()
    
    def process_video(self, db, video_data):
        video_id = video_data['id']
        
        existing = db.query(Video).filter(Video.id == video_id).first()
        
        if existing and existing.transcript_available:
            logger.debug(f"Video {video_id} already processed with transcript")
            return existing
        
        logger.debug(f"Fetching transcript for {video_id}")
        transcript, transcript_available = self.transcript_fetcher.get_transcript(video_id)
        
        if transcript_available:
            logger.debug(f"Transcript available for {video_id}, length: {len(transcript)}")
            # Generate AI analysis
            summary = self.ai_analyzer.generate_summary(transcript)
            topics = self.ai_analyzer.classify_topics(
                transcript, 
                video_data['title'], 
                video_data['description']
            )
            key_insights = self.ai_analyzer.extract_key_insights(transcript, summary)
        else:
            logger.debug(f"No transcript for {video_id}, using description only")
            summary = self.ai_analyzer.generate_summary(video_data.get('description', ''))
            topics = self.ai_analyzer.classify_topics(
                None, 
                video_data['title'], 
                video_data['description']
            )
            key_insights = "No transcript available for insights"
        
        video_dict = {
            'id': video_id,
            'title': video_data['title'],
            'description': video_data['description'],
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
            db_video = existing
        else:
            db_video = Video(**video_dict)
            db.add(db_video)
        
        db.flush()
        return db_video
    
    def update_channel_relations(self, db):
        logger.info("Updating channel relations...")
        
        channels = db.query(Video.channel_id, Video.channel_name).distinct().all()
        channel_ids = [c[0] for c in channels]
        
        channel_videos = {}
        for channel_id in channel_ids:
            videos = db.query(Video).filter(
                Video.channel_id == channel_id,
                Video.topics.isnot(None)
            ).all()
            channel_videos[channel_id] = videos
        
        relation_count = 0
        for i, channel1 in enumerate(channel_ids):
            for channel2 in channel_ids[i+1:]:
                similarity = self.ai_analyzer.calculate_channel_similarity(
                    channel_videos.get(channel1, []),
                    channel_videos.get(channel2, [])
                )
                
                topics1 = set()
                topics2 = set()
                
                for video in channel_videos.get(channel1, []):
                    if video.topics:
                        video_topics = json.loads(video.topics) if isinstance(video.topics, str) else video.topics
                        topics1.update([t['topic'] for t in video_topics])
                
                for video in channel_videos.get(channel2, []):
                    if video.topics:
                        video_topics = json.loads(video.topics) if isinstance(video.topics, str) else video.topics
                        topics2.update([t['topic'] for t in video_topics])
                
                common_topics = list(topics1 & topics2)
                
                relation = db.query(ChannelRelation).filter(
                    ((ChannelRelation.channel_id_1 == channel1) & (ChannelRelation.channel_id_2 == channel2)) |
                    ((ChannelRelation.channel_id_1 == channel2) & (ChannelRelation.channel_id_2 == channel1))
                ).first()
                
                if relation:
                    relation.similarity_score = similarity
                    relation.common_topics = json.dumps(common_topics)
                    relation.last_updated = datetime.utcnow()
                else:
                    relation = ChannelRelation(
                        channel_id_1=channel1,
                        channel_id_2=channel2,
                        similarity_score=similarity,
                        common_topics=json.dumps(common_topics),
                        last_updated=datetime.utcnow()
                    )
                    db.add(relation)
                relation_count += 1
        
        logger.info(f"Updated {relation_count} channel relations")
    
    def update_video_relations(self, db):
        logger.info("Updating video relations...")
        
        videos = db.query(Video).filter(
            Video.topics.isnot(None),
            Video.published_at >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        logger.info(f"Processing {len(videos)} videos for relations")
        
        updated_count = 0
        for video in videos:
            if not video.topics:
                continue
            
            video_topics = json.loads(video.topics) if isinstance(video.topics, str) else video.topics
            video_topic_set = set([t['topic'] for t in video_topics])
            
            related = []
            for other in videos:
                if other.id == video.id or not other.topics:
                    continue
                
                other_topics = json.loads(other.topics) if isinstance(other.topics, str) else other.topics
                other_topic_set = set([t['topic'] for t in other_topics])
                
                if not video_topic_set or not other_topic_set:
                    continue
                
                similarity = len(video_topic_set & other_topic_set) / len(video_topic_set | other_topic_set)
                
                if similarity > 0.5:
                    related.append({
                        'video_id': other.id,
                        'title': other.title,
                        'similarity': similarity
                    })
            
            related.sort(key=lambda x: x['similarity'], reverse=True)
            video.related_videos = json.dumps(related[:10])
            updated_count += 1
        
        logger.info(f"Updated relations for {updated_count} videos")
