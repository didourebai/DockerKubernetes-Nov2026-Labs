# syntax=docker/dockerfile:1
# Module recap -- Compteur de visites
# Reprend les bonnes pratiques des modules 03 et 04

# --- Etape 1 : installer les dependances ---
FROM python:3.12-slim AS builder
WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/deps -r requirements.txt

# --- Etape 2 : image finale, plus legere ---
FROM python:3.12-slim
LABEL description="Compteur de visites - recap Docker"
WORKDIR /app

# Dependances recuperees de l'etape 1 (multi-stage)
COPY --from=builder /deps /usr/local

# Le code en dernier : il change souvent, le cache des couches precedentes est conserve
COPY app.py .

# Utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

ENV REDIS_HOST=redis
EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
