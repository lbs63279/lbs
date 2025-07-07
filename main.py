from fastapi import FastAPI
from src.core.database import Base, engine
from src.routes import podcasts
import os

app = FastAPI(
    title="API da Biblioteca – LBS",
    description="Serviço para buscar e armazenar podcasts de negócios do Spotify",
    version="1.0.0"
)

# Cria tabelas
Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(podcasts.router)
