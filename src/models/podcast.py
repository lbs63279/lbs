from sqlalchemy import Column, String, Text
from src.core.database import Base

class Podcast(Base):
    __tablename__ = 'podcasts'
    id = Column(String, primary_key=True)
    titulo = Column(String)
    descricao = Column(String)
    publicador = Column(String)
    url = Column(String)
    imagem_url = Column(String)
    categorias = Column(String)
    pais = Column(String)
    total_episodes = Column(String)
