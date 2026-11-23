"""Lab A5 : assistant IA du portail IT-Support.

Le modèle (Docker Model Runner) peut appeler des outils fournis par la
MCP Gateway (ex. recherche web DuckDuckGo).

Variables d'environnement :
  MODEL_URL, MODEL_NAME   injectées par Docker Compose (section models)
  MCP_GATEWAY_URL         adresse de la passerelle (ex. http://mcp-gateway:8811/mcp)
  MCP_GATEWAY_AUTH_TOKEN  jeton partagé avec la passerelle (facultatif)
"""
import asyncio
import json
import os
import urllib.request

from flask import Flask, render_template_string, request
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

app = Flask(__name__)

CONSIGNE = (
    "Tu es l'assistant du portail IT-Support. Réponds en français, de façon courte. "
    "Si tu as besoin d'une information récente ou technique, utilise l'outil de recherche."
)
MAX_TOURS = 4

PAGE = """<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>Lab A5 - Assistant IT-Support</title></head>
<body style="font-family: sans-serif; max-width: 720px; margin: 40px auto;">
  <h1>Assistant IT-Support</h1>
  <p>Modèle : <strong>{{ modele or "non configuré" }}</strong></p>
  <form method="post">
    <input name="question" size="70" placeholder="Ex. : Comment réinitialiser un mot de passe Windows ?" value="{{ question }}">
    <button type="submit">Envoyer</button>
  </form>
  {% if erreur %}<p style="color: #b00020;"><strong>Erreur :</strong> {{ erreur }}</p>{% endif %}
  {% if reponse %}<h2>Réponse</h2><p>{{ reponse }}</p>{% endif %}
  {% if outils %}<h3>Outils appelés</h3><ul>{% for o in outils %}<li>{{ o }}</li>{% endfor %}</ul>
  {% elif reponse %}<p><em>Aucun outil appelé.</em></p>{% endif %}
</body>
</html>"""


def appeler_modele(messages, outils):
    url = os.environ.get("MODEL_URL")
    modele = os.environ.get("MODEL_NAME")
    if not url or not modele:
        raise RuntimeError("Variables MODEL_URL et MODEL_NAME absentes (section models du service).")
    corps = {"model": modele, "messages": messages}
    if outils:
        corps["tools"] = outils
    requete = urllib.request.Request(
        url.rstrip("/") + "/chat/completions",
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(requete, timeout=300) as reponse:
        return json.load(reponse)["choices"][0]["message"]


def en_outil_openai(outil):
    return {
        "type": "function",
        "function": {
            "name": outil.name,
            "description": outil.description or "",
            "parameters": outil.inputSchema or {"type": "object", "properties": {}},
        },
    }


def texte_du_resultat(resultat):
    return "\n".join(b.text for b in resultat.content if getattr(b, "text", None))


async def repondre(question):
    messages = [
        {"role": "system", "content": CONSIGNE},
        {"role": "user", "content": question},
    ]
    appels = []
    adresse = os.environ.get("MCP_GATEWAY_URL")
    if not adresse:
        message = await asyncio.to_thread(appeler_modele, messages, None)
        return message.get("content", ""), appels
    jeton = os.environ.get("MCP_GATEWAY_AUTH_TOKEN")
    entetes = {"Authorization": "Bearer " + jeton} if jeton else None
    async with streamablehttp_client(adresse, headers=entetes) as (lecture, ecriture, _):
        async with ClientSession(lecture, ecriture) as session:
            await session.initialize()
            outils = [en_outil_openai(o) for o in (await session.list_tools()).tools]
            for _ in range(MAX_TOURS):
                message = await asyncio.to_thread(appeler_modele, messages, outils)
                demandes = message.get("tool_calls") or []
                if not demandes:
                    return message.get("content", ""), appels
                messages.append(message)
                for demande in demandes:
                    nom = demande["function"]["name"]
                    arguments = json.loads(demande["function"].get("arguments") or "{}")
                    appels.append(nom + " " + json.dumps(arguments, ensure_ascii=False))
                    resultat = await session.call_tool(nom, arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": demande["id"],
                            "content": texte_du_resultat(resultat)[:4000],
                        }
                    )
            return "Trop d'appels d'outils sans réponse finale.", appels


@app.route("/", methods=["GET", "POST"])
def accueil():
    question = request.form.get("question", "").strip()
    reponse = erreur = None
    outils = []
    if question:
        try:
            reponse, outils = asyncio.run(repondre(question))
        except Exception as exc:  # affichage pédagogique de toute erreur
            erreur = type(exc).__name__ + " : " + str(exc)
    return render_template_string(
        PAGE, modele=os.environ.get("MODEL_NAME"), question=question,
        reponse=reponse, erreur=erreur, outils=outils,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
