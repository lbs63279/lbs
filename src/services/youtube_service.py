import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def buscar_aulas_de_negocios(termo='aula de negócios', max_resultados=25, regiao='BR'):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        'part': 'snippet',
        'q': termo,
        'type': 'video',
        'regionCode': regiao,
        'videoCategoryId': '27',
        'maxResults': max_resultados,
        'key': YOUTUBE_API_KEY
    }

    resposta = requests.get(url, params=params)

    if resposta.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Erro na API do YouTube: {resposta.text}")

    dados = resposta.json()
    videos = []

    for item in dados.get('items', []):
        video = {
            'id': item['id']['videoId'],
            'titulo': item['snippet']['title'],
            'descricao': item['snippet']['description'],
            'canal': item['snippet']['channelTitle'],
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
            'categoria': 'Negócios',
            'pais': regiao,
            'publicado_em': item['snippet']['publishedAt']
        }
        videos.append(video)

    return videos
