import base64
import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_base64_client_credentials(client_id, client_secret):
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    return client_creds_b64.decode()

def obter_token_acesso():
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f"Basic {get_base64_client_credentials(client_id, client_secret)}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}

    resposta = requests.post(token_url, headers=headers, data=data)
    if resposta.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Erro ao obter token: {resposta.text}")
    return resposta.json()['access_token']

def obter_top_podcasts(token, pais='BR', consulta='business', limite=50):
    url = "https://api.spotify.com/v1/search"
    headers = {'Authorization': f"Bearer {token}"}
    params = {
        'q': consulta,
        'type': 'show',
        'market': pais,
        'limit': limite
    }
    resposta = requests.get(url, headers=headers, params=params)
    if resposta.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar podcasts: {resposta.text}")
    return resposta.json()['shows']['items']
