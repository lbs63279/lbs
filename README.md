# 📚 Link Business School API

Esta é a API pública da **Link Business School**, que oferece acesso a conteúdos como **podcasts**, **livros em PDF**, **aulas do YouTube** e **bibliotecas recomendadas**.

> 🌐 **URL base da API**:  
> `https://link-business-school.onrender.com/api/v1`

---

## 📌 Endpoints Disponíveis


#### 🎧 GET /conteudo-lbs
- Retorna uma lista paginada de conteúdos de acordo com o tipo: podcast, livro, aula ou biblioteca.

🔸 Parâmetros:
Parâmetro	Tipo	Obrigatório	Padrão	Descrição
tipo	string	Não	podcast	Tipo de conteúdo desejado
page	inteiro	Não	1	Página da listagem
limit	inteiro	Não	10	Quantidade de itens por página

🔹 Exemplo de requisição:
```
GET /conteudo-lbs?tipo=livro&page=1&limit=5
```


#### 📄 GET /conteudo-lbs/livro/{livro_id}
- Retorna um livro específico pelo seu ID.

#### 🎥 GET /conteudo-lbs/aula/{aula_id}
- Retorna uma aula do YouTube específica pelo seu ID.

#### 🎙️ GET /conteudo-lbs/podcast/{podcast_id}
- Retorna um podcast específico pelo seu ID.

#### 🔤 GET /fonts/{font_name}
- Retorna uma fonte .otf localizada em src/fonts.
- ⚠️ Apenas arquivos .otf são permitidos.

### 💡 Exemplos de Uso

🔹 Listar os 10 primeiros livros
```
GET https://link-business-school.onrender.com/api/v1/conteudo-lbs?tipo=livro&limit=10
```

🔹 Buscar um podcast por ID
```
GET https://link-business-school.onrender.com/api/v1/conteudo-lbs/podcast/abc123
````

### 🧩 Tipos de Conteúdo Retornados

- 📘 Livro
```
{
  "id": "livro001",
  "titulo": "Estratégias de Negócios",
  "descricao": "Um guia prático...",
  "arquivo_pdf": "https://link..."
}
````

- 🎓 Aula (YouTube)
```
{
  "id": "x7yt89",
  "titulo": "Como começar seu negócio",
  "descricao": "...",
  "canal": "Canal Empreenda",
  "imagem_url": "...",
  "embed_url": "https://www.youtube.com/embed/x7yt89"
}
```

- 🎧 Podcast
```
{
  "tipo": "podcast",
  "podcast_id": "xyz123",
  "podcast_titulo": "Negócios em Alta",
  "episodio_titulo": "Como vender mais",
  "data_lancamento": "2024-05-01",
  "duracao_ms": 1500000,
  "url": "https://open.spotify.com/...",
  "embed_url": "https://...",
  "imagem_url": "https://..."
}
```

### 🛠️ Tecnologias Utilizadas

- FastAPI
- SQLAlchemy
- Integrações com:
    1. Spotify Web API
    2. YouTube Data API

📫 Contato
Caso queira contribuir ou reportar algum problema, entre em contato via LinkedIn ou abra uma issue neste repositório.
