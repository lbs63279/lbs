from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import Base, engine
from src.routes import podcasts
import os

app = FastAPI(
    title="API da Biblioteca – LBS",
    description="Serviço para buscar e armazenar podcasts de negócios do Spotify",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

Base.metadata.create_all(bind=engine)

app.include_router(podcasts.router)
