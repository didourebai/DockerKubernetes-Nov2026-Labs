# Compteur de visites -- Module recap Docker
# Petite application web : chaque visite incremente un compteur stocke dans Redis.
# Vous n'avez pas besoin de modifier ce fichier.
import os
import socket

import redis
from flask import Flask

app = Flask(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
APP_TITLE = os.environ.get("APP_TITLE", "Compteur de visites")
APP_COLOR = os.environ.get("APP_COLOR", "#2496ed")

cache = redis.Redis(host=REDIS_HOST, port=6379, socket_connect_timeout=2)


@app.route("/")
def index():
    try:
        visites = cache.incr("visites")
        message = f"Visite numero <strong>{visites}</strong>"
    except redis.exceptions.ConnectionError:
        message = f"Redis injoignable (hote : <code>{REDIS_HOST}</code>)"
    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>{APP_TITLE}</title></head>
<body style="font-family: sans-serif; text-align: center; margin-top: 15vh;">
  <h1 style="color: {APP_COLOR};">{APP_TITLE}</h1>
  <p style="font-size: 1.5em;">{message}</p>
  <p>Servi par le conteneur : <code>{socket.gethostname()}</code></p>
</body>
</html>"""


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
