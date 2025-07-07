# 🚀 Etapa 1: Imagem base com Python
FROM python:3.11-slim

# 🏠 Diretório de trabalho
WORKDIR /app

# 🚀 Copia arquivos de configuração para cache de dependências
COPY pyproject.toml poetry.lock ./

# ⚙️ Instala o Poetry
RUN pip install --no-cache-dir poetry

# 🏗️ Instala as dependências no ambiente do Poetry (sem criar virtualenv)
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# 📝 Copia o restante dos arquivos do projeto (incluindo src, models, .env e main.py)
COPY . .

# ⚠️ Configura variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# 🔥 Comando para rodar o servidor (main.py fora da pasta src)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
