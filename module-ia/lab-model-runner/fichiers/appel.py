"""Lab A2 : une « application » qui appelle un modèle via une API compatible OpenAI.

L'adresse du modèle vient d'une variable d'environnement, comme le fera Docker Compose
au lab A3 (endpoint_var).
"""
import json
import os
import urllib.request

url = os.environ.get("MODEL_URL", "http://model-runner.docker.internal/engines/v1")
modele = os.environ.get("MODEL_NAME", "ai/smollm2")

corps = json.dumps(
    {
        "model": modele,
        "messages": [{"role": "user", "content": "Dis bonjour en une phrase."}],
    }
).encode("utf-8")

requete = urllib.request.Request(
    f"{url}/chat/completions",
    data=corps,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(requete, timeout=120) as reponse:
    donnees = json.load(reponse)

print("Adresse :", url)
print("Réponse :", donnees["choices"][0]["message"]["content"])
