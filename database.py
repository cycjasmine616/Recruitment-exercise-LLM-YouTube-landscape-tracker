from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config
import json

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text)
    channel_id = Column(String)
    channel_name = Column(String)
    published_at = Column(DateTime)
    duration = Column(Integer)
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)
    thumbnail_url = Column(String)
    url = Column(String)
    transcript = Column(Text)
    transcript_available = Column(Boolean, default=False)
    summary = Column(Text)
    topics = Column(JSON)
    key_insights = Column(Text)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'channel_name': self.channel_name,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'duration': self.duration,
            'view_count': self.view_count,
            'thumbnail_url': self.thumbnail_url,
            'url': self.url,
            'transcript_available': self.transcript_available,
            'summary': self.summary,
            'topics': json.loads(self.topics) if isinstance(self.topics, str) else self.topics,
            'key_insights': self.key_insights,
        }

engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
