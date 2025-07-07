from sqlalchemy import Column, String, Text
from src.core.database import Base

class YoutubeVideo(Base):
    __tablename__ = 'youtube_videos'
    
    id = Column(String, primary_key=True)
    titulo = Column(String)
    descricao = Column(Text)
    canal = Column(String)
    url = Column(String)
    thumbnail_url = Column(String)
    categoria = Column(String)
    pais = Column(String)     
    publicado_em = Column(String)
