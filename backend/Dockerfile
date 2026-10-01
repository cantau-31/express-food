# Image de production pour l'API Django (serveur WSGI gunicorn, Linux).
# Contexte de build : le dossier backend/.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installer les dependances d'abord pour profiter du cache de couches Docker.
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

EXPOSE 8000

# DJANGO_SECRET_KEY et MONGODB_URI doivent etre fournis par l'environnement (voir .env.example).
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
