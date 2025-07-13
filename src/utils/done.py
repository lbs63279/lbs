import json
import hashlib

def gerar_id_unico(item, ids_existentes):
    base_str = json.dumps(item, sort_keys=True)
    novo_id = hashlib.sha256(base_str.encode()).hexdigest()
    
    while novo_id in ids_existentes:
        base_str += "x"
        novo_id = hashlib.sha256(base_str.encode()).hexdigest()
    
    return novo_id

def remover_duplicatas_por_titulo(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        artigos = json.load(f)

    titulos_vistos = set()
    ids_existentes = set()
    artigos_processados = []

    for artigo in artigos:
        titulo = artigo.get("titulo", "").strip()

        # Ignora artigos sem título
        if not titulo:
            continue

        # Verifica se é duplicado pelo título
        if titulo in titulos_vistos:
            continue  # já foi adicionado um com esse título

        # Garante que o ID existe e é único
        if 'id' not in artigo or not artigo['id']:
            artigo_sem_id = artigo.copy()
            artigo.pop('id', None)
            novo_id = gerar_id_unico(artigo_sem_id, ids_existentes)
            artigo['id'] = novo_id
        ids_existentes.add(artigo['id'])

        # Marca título como visto e salva o artigo
        titulos_vistos.add(titulo)
        artigos_processados.append(artigo)

    # Escreve os dados limpos no mesmo arquivo
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(artigos_processados, f, indent=4, ensure_ascii=False)

    print(f"Processado com sucesso! Total final: {len(artigos_processados)} artigos únicos por título.")

# Uso
remover_duplicatas_por_titulo('artigos.json')
