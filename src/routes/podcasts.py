import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
import requests
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.podcast import Podcast
from src.services.spotify_service import obter_token_acesso, obter_top_podcasts
from pathlib import Path
import json 
from fastapi.responses import FileResponse
from fastapi import Request
import random

router = APIRouter(prefix="/api/v1", tags=["Podcasts"])

ARTIGOS_CACHE = []
BIBLIOTECAS_CACHE = []
LIVROS_CACHE = []
PODCASTS_CACHE = []
AULAS_CACHE = []

def carregar_conteudos_em_memoria():
    base_path = Path(__file__).resolve().parent.parent / "utils"

    def carregar_json(nome_arquivo):
        caminho = base_path / nome_arquivo
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)

    global ARTIGOS_CACHE, BIBLIOTECAS_CACHE, LIVROS_CACHE, PODCASTS_CACHE, AULAS_CACHE

    ARTIGOS_CACHE = carregar_json("artigos.json")
    BIBLIOTECAS_CACHE = carregar_json("bibliotecas.json")
    LIVROS_CACHE = carregar_json("livros.json")
    PODCASTS_CACHE = carregar_json("podcast.json")
    AULAS_CACHE = carregar_json("aula.json")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def obter_aulas_youtube():
    aulas = []

    caminho_json = os.path.join(os.path.dirname(__file__), "..", "utils", "aula.json")
    caminho_json = os.path.abspath(caminho_json)

    if not os.path.exists(caminho_json):
        print("[DEBUG] Aula JSON não encontrado:", caminho_json)
        return aulas

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            aulas = json.load(f)
            print(f"[DEBUG] {len(aulas)} aula(s) carregado(s) do JSON.")
    except Exception as e:
        print("[ERRO] Falha ao ler o JSON:", e)

    return aulas

def obter_podcasts():
    podcasts = []

    caminho_json = os.path.join(os.path.dirname(__file__), "..", "utils", "podcast.json")
    caminho_json = os.path.abspath(caminho_json)

    if not os.path.exists(caminho_json):
        print("[DEBUG] Podcast JSON não encontrado:", caminho_json)
        return podcasts

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            podcasts = json.load(f)
            print(f"[DEBUG] {len(podcasts)} podcast(s) carregado(s) do JSON.")
    except Exception as e:
        print("[ERRO] Falha ao ler o JSON:", e)

    return podcasts


def obter_livros_pdf():
    livros = []

    caminho_json = os.path.join(os.path.dirname(__file__), "..", "utils", "livros.json")
    caminho_json = os.path.abspath(caminho_json)

    if not os.path.exists(caminho_json):
        print("[DEBUG] Arquivo JSON não encontrado:", caminho_json)
        return livros

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            livros = json.load(f)
            print(f"[DEBUG] {len(livros)} livro(s) carregado(s) do JSON.")
    except Exception as e:
        print("[ERRO] Falha ao ler o JSON:", e)

    return livros

def obter_artigos_pdf():
    artigos = []

    caminho_json = os.path.join(os.path.dirname(__file__), "..", "utils", "artigos.json")
    caminho_json = os.path.abspath(caminho_json)

    if not os.path.exists(caminho_json):
        print("[DEBUG] Arquivo JSON não encontrado:", caminho_json)
        return artigos

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            artigos = json.load(f)
            print(f"[DEBUG] {len(artigos)} livro(s) carregado(s) do JSON.")
    except Exception as e:
        print("[ERRO] Falha ao ler o JSON:", e)

    return artigos

def inserir_videos_youtube(palavra_chave="negócios", max_results=10):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API Key não encontrada.")

    paises = ['BR', 'US']
    aulas = []

    for pais in paises:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": palavra_chave,
            "type": "video",
            "videoCategoryId": "27",
            "regionCode": pais,
            "maxResults": max_results,
            "key": api_key
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            continue

        data = response.json()
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            aulas.append({
                "id": video_id,
                "tipo": "aula",
                "titulo": snippet["title"],
                "descricao": snippet.get("description", ""),
                "canal": snippet.get("channelTitle", ""),
                "imagem_url": snippet["thumbnails"]["high"]["url"],
                "categorias": ["negócios"],
                "pais": pais,
                "embed_url": f"https://www.youtube.com/embed/{video_id}"
            })

    return aulas


def inserir_podcasts(db: Session, lista_podcasts: list, pais: str):
    for show in lista_podcasts:
        total_episodes = show.get('total_episodes', 0)

        podcast_existente = db.query(Podcast).filter(Podcast.id == show['id']).first()
        if podcast_existente:
            podcast_existente.titulo = show['name']
            podcast_existente.descricao = show['description']
            podcast_existente.publicador = show['publisher']
            podcast_existente.url = show['external_urls']['spotify']
            podcast_existente.imagem_url = show['images'][0]['url'] if show['images'] else None
            podcast_existente.categorias = "negócios"
            podcast_existente.pais = pais
            podcast_existente.total_episodes = total_episodes
        else:
            novo_podcast = Podcast(
                id=show['id'],
                titulo=show['name'],
                descricao=show['description'],
                publicador=show['publisher'],
                url=show['external_urls']['spotify'],
                imagem_url=show['images'][0]['url'] if show['images'] else None,
                categorias="negócios",
                pais=pais,
                total_episodes=total_episodes
            )
            db.add(novo_podcast)
    db.commit()


@router.get("/obter_top_podcasts")
def atualizar_podcasts(db: Session = Depends(get_db)):
    token = obter_token_acesso()

    podcasts_br = obter_top_podcasts(token=token, pais='BR', limite=25)
    podcasts_us = obter_top_podcasts(token=token, pais='US', limite=25)

    db.query(Podcast).delete()
    db.commit()

    inserir_podcasts(db, podcasts_br, 'BR')
    inserir_podcasts(db, podcasts_us, 'US')

    db.commit()

    total = len(podcasts_br) + len(podcasts_us)
    return {"mensagem": f"{total} podcasts atualizados e salvos no banco de dados."}


def flatten_podcasts(podcasts: list[dict]) -> list[dict]:
    episodios_flat = []

    for podcast in podcasts:
        for episodio in podcast.get("episodios", []):
            episodios_flat.append({
                "tipo": "podcast",
                "podcast_id": podcast["id"],
                "podcast_titulo": podcast["titulo"],
                "publicador": podcast["publicador"],
                "episodio_id": episodio["id"],
                "episodio_titulo": episodio["titulo"],
                "descricao": episodio["descricao"],
                "data_lancamento": episodio["data_lancamento"],
                "duracao_ms": episodio["duracao_ms"],
                "url": episodio["url"],
                "embed_url": episodio["embed_url"],
                "imagem_url": episodio["imagem_url"],
                "categorias": episodio.get("categorias", [])
            })
    return episodios_flat


@router.get("/conteudo-lbs")
def obter_conteudo_lbs(
    db: Session = Depends(get_db),
    tipo: Literal["podcast", "livro", "aula", "biblioteca", "artigos"] = Query("podcast"),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100)
):
    conteudo_formatado = {
        "podcast": flatten_podcasts(PODCASTS_CACHE),
        "livro": LIVROS_CACHE,
        "aula": AULAS_CACHE,
        "biblioteca": BIBLIOTECAS_CACHE,
        "artigos": ARTIGOS_CACHE,
    }

    todos_itens = conteudo_formatado[tipo]

    random.shuffle(todos_itens)

    total = len(todos_itens)
    start = (page - 1) * limit
    end = start + limit
    itens_paginados = todos_itens[start:end]

    return {
        "tipo": tipo,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit,
        "conteudo": itens_paginados
    }


@router.get("/conteudo-lbs/todos")
def obter_todos_conteudos_randomizados(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
):
    podcasts = flatten_podcasts(obter_podcasts())
    aulas = obter_aulas_youtube()
    livros = obter_livros_pdf()
    artigos = obter_artigos_pdf()

    caminho_bibliotecas = Path(__file__).resolve().parent.parent / "utils" / "bibliotecas.json"
    try:
        with open(caminho_bibliotecas, encoding="utf-8") as f:
            bibliotecas = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar bibliotecas: {str(e)}")
    
    for item in podcasts:
        item["tipo"] = "podcast"

    for item in aulas:
        item["tipo"] = "aula"

    for item in livros:
        item["tipo"] = "livro"

    for item in artigos:
        item["tipo"] = "artigo"

    for item in bibliotecas:
        item["tipo"] = "biblioteca"

    todos_itens = podcasts + aulas + livros + artigos + bibliotecas
    random.shuffle(todos_itens)

    total = len(todos_itens)
    start = (page - 1) * limit
    end = start + limit
    itens_paginados = todos_itens[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit,
        "conteudo": itens_paginados
    }


@router.get("/conteudo-lbs/item/{item_id}")
def obter_item_unico_por_id(item_id: str):
    podcasts = obter_podcasts()

    podcast = next((p for p in podcasts if str(p.get("id")) == item_id), None)
    if podcast:
        return {
            "tipo": "podcast",
            **podcast
        }

    for p in podcasts:
        episodio = next((e for e in p.get("episodios", []) if str(e.get("id")) == item_id), None)
        if episodio:
            return {
                "tipo": "podcast",
                "podcast_id": p["id"],
                "podcast_titulo": p["titulo"],
                "publicador": p["publicador"],
                "episodio_id": episodio["id"],
                "episodio_titulo": episodio["titulo"],
                "descricao": episodio["descricao"],
                "data_lancamento": episodio["data_lancamento"],
                "duracao_ms": episodio["duracao_ms"],
                "url": episodio["url"],
                "embed_url": episodio["embed_url"],
                "imagem_url": episodio["imagem_url"],
                "categorias": episodio.get("categorias", [])
            }

    aulas = obter_aulas_youtube()
    for aula in aulas:
        if str(aula.get("id")) == item_id:
            aula["tipo"] = "aula"
            return aula

    livros = obter_livros_pdf()
    for livro in livros:
        if str(livro.get("id")) == item_id:
            livro["tipo"] = "livro"
            return livro

    artigos = obter_artigos_pdf()
    for artigo in artigos:
        if str(artigo.get("id")) == item_id:
            artigo["tipo"] = "artigo"
            return artigo

    caminho_bibliotecas = Path(__file__).resolve().parent.parent / "utils" / "bibliotecas.json"
    try:
        with open(caminho_bibliotecas, encoding="utf-8") as f:
            bibliotecas = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar bibliotecas: {str(e)}")

    for biblioteca in bibliotecas:
        if str(biblioteca.get("id")) == item_id:
            biblioteca["tipo"] = "biblioteca"
            return biblioteca

    raise HTTPException(status_code=404, detail="Item não encontrado.")


@router.get("/fonts/{font_name}")
def get_font(font_name: str):
    font_path = os.path.join("src", "fonts", font_name)
    
    if not os.path.exists(font_path) or not font_name.endswith(".otf"):
        return {"error": "Arquivo não encontrado ou formato inválido."}
    
    return FileResponse(font_path, media_type="font/otf", filename=font_name)



@router.get("/conteudo-lbs/livro/{livro_id}")
def obter_livro_por_id(livro_id: str):
    livros = obter_livros_pdf()
    livro = next((l for l in livros if str(l.get("id")) == livro_id), None)

    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    return livro


@router.get("/conteudo-lbs/aula/{aula_id}")
def obter_aula_por_id(aula_id: str):
    aulas = obter_aulas_youtube()
    aula = next((a for a in aulas if str(a.get("id")) == aula_id), None)

    if not aula:
        raise HTTPException(status_code=404, detail="Aula não encontrada.")

    return aula


@router.get("/conteudo-lbs/artigos/{aula_id}")
def obter_aula_por_id(aula_id: str):
    aulas = obter_artigos_pdf()
    aula = next((a for a in aulas if str(a.get("id")) == aula_id), None)

    if not aula:
        raise HTTPException(status_code=404, detail="Aula não encontrada.")

    return aula


@router.get("/conteudo-lbs/podcast/{podcast_id}")
def obter_podcast_ou_episodio_por_id(podcast_id: str):
    podcasts = obter_podcasts()

    podcast = next((p for p in podcasts if str(p.get("id")) == podcast_id), None)
    if podcast:
        return flatten_podcasts([podcast])

    for p in podcasts:
        episodio = next((e for e in p.get("episodios", []) if str(e.get("id")) == podcast_id), None)
        if episodio:
            return [{
                "tipo": "podcast",
                "podcast_id": p["id"],
                "podcast_titulo": p["titulo"],
                "publicador": p["publicador"],
                "episodio_id": episodio["id"],
                "episodio_titulo": episodio["titulo"],
                "descricao": episodio["descricao"],
                "data_lancamento": episodio["data_lancamento"],
                "duracao_ms": episodio["duracao_ms"],
                "url": episodio["url"],
                "embed_url": episodio["embed_url"],
                "imagem_url": episodio["imagem_url"],
                "categorias": episodio.get("categorias", [])
            }]

    raise HTTPException(status_code=404, detail="Podcast ou episódio não encontrado.")


@router.get("/conteudo-lbs/search")
def buscar_conteudos_por_titulo(
    q: str = Query(..., description="Palavra-chave da busca"),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    request: Request = None
):
    q_lower = q.strip().lower()

    podcasts = flatten_podcasts(obter_podcasts())
    aulas = obter_aulas_youtube()
    livros = obter_livros_pdf()
    artigos = obter_artigos_pdf()

    caminho_bibliotecas = Path(__file__).resolve().parent.parent / "utils" / "bibliotecas.json"
    try:
        with open(caminho_bibliotecas, encoding="utf-8") as f:
            bibliotecas = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar bibliotecas: {str(e)}")

    todos_conteudos = []

    for item in podcasts:
        if q_lower in item.get("episodio_titulo", "").lower():
            item["tipo"] = "podcast"
            todos_conteudos.append(item)

    for item in aulas:
        if q_lower in item.get("titulo", "").lower():
            item["tipo"] = "aula"
            todos_conteudos.append(item)

    for item in livros:
        if q_lower in item.get("titulo", "").lower():
            item["tipo"] = "livro"
            todos_conteudos.append(item)

    for item in artigos:
        if q_lower in item.get("titulo", "").lower():
            item["tipo"] = "artigo"
            todos_conteudos.append(item)

    for item in bibliotecas:
        if q_lower in item.get("titulo", "").lower():
            item["tipo"] = "biblioteca"
            todos_conteudos.append(item)

    total = len(todos_conteudos)
    start = (page - 1) * limit
    end = start + limit
    itens_paginados = todos_conteudos[start:end]

    return {
        "query": q,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit,
        "conteudo": itens_paginados
    }