"""Lab A3 : petite application de discussion qui appelle un modèle d'IA.

L'adresse et le nom du modèle viennent de variables d'environnement
(MODEL_URL, MODEL_NAME) injectées par Docker Compose.
"""
import json
import os
import urllib.error
import urllib.request

from flask import Flask, render_template_string, request

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>Lab A3 - Compose et modèles</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
  <h1>Lab A3 : Compose et modèles d'IA</h1>
  <p>Modèle : <strong>{{ modele or "non configuré" }}</strong></p>
  <form method="post">
    <input name="question" size="60" placeholder="Posez une question" value="{{ question }}">
    <button type="submit">Envoyer</button>
  </form>
  {% if erreur %}<p style="color: #b00020;"><strong>Erreur :</strong> {{ erreur }}</p>{% endif %}
  {% if reponse %}<h2>Réponse</h2><p>{{ reponse }}</p>{% endif %}
</body>
</html>"""


def appeler_modele(question):
    url = os.environ.get("MODEL_URL")
    modele = os.environ.get("MODEL_NAME")
    if not url or not modele:
        raise RuntimeError(
            "Variables MODEL_URL et MODEL_NAME absentes : ce service n'a pas accès "
            "au modèle (voir la section models du service dans le fichier Compose)."
        )
    corps = json.dumps(
        {"model": modele, "messages": [{"role": "user", "content": question}]}
    ).encode("utf-8")
    requete = urllib.request.Request(
        url.rstrip("/") + "/chat/completions",
        data=corps,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        donnees = json.load(reponse)
    return donnees["choices"][0]["message"]["content"]


@app.route("/", methods=["GET", "POST"])
def accueil():
    question = request.form.get("question", "").strip()
    reponse = erreur = None
    if question:
        try:
            reponse = appeler_modele(question)
        except (RuntimeError, urllib.error.URLError, KeyError, ValueError) as exc:
            erreur = str(exc)
    return render_template_string(
        PAGE,
        modele=os.environ.get("MODEL_NAME"),
        question=question,
        reponse=reponse,
        erreur=erreur,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
