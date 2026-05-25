from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean, Float
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
    thumbnail_url = Column(String)
    url = Column(String)
    
    transcript = Column(Text)
    transcript_available = Column(Boolean, default=False)
    transcript_excerpts = Column(JSON)  
    
    llm_topics_discussed = Column(JSON)  
    technical_depth = Column(String)  
    creator_stance = Column(Text) 
    key_claims = Column(JSON)  
    practical_insights = Column(Text)  
    
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
            'transcript_excerpts': json.loads(self.transcript_excerpts) if isinstance(self.transcript_excerpts, str) else self.transcript_excerpts,
            'llm_topics_discussed': json.loads(self.llm_topics_discussed) if isinstance(self.llm_topics_discussed, str) else self.llm_topics_discussed,
            'technical_depth': self.technical_depth,
            'creator_stance': self.creator_stance,
            'key_claims': json.loads(self.key_claims) if isinstance(self.key_claims, str) else self.key_claims,
            'practical_insights': self.practical_insights,
        }

class ChannelRelation(Base):
    __tablename__ = 'channel_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id_1 = Column(String, nullable=False)
    channel_name_1 = Column(String)
    channel_id_2 = Column(String, nullable=False)
    channel_name_2 = Column(String)
    similarity_score = Column(Float)
    common_topics = Column(JSON)
    relationship_description = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
