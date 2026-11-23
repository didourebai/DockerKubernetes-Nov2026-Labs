"""Mini application Flask servant de projet de test pour le lab Docker Sandboxes."""
import datetime

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def accueil():
    return "<h1>Projet de test - Docker Sandboxes</h1>"


@app.route("/heure")
def heure():
    return jsonify(heure=datetime.datetime.now().strftime("%H:%M:%S"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
