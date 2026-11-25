# Notes formateur — Lab A5 (à valider avant la formation)

> Exécution du 21/11/2026 : OK avec `ai/qwen3:1.7b` (1,1 Go) et `docker/mcp-gateway:v0.44.3` (`latest` non retenu : version fixée). `ai/qwen3` sans étiquette = 8B, 5 Go : trop lourd pour la classe. Question « dernière version de Docker Desktop » : appel `search` effectué, réponse en ~185 s sur processeur, **fausse** (24.0.0) ; sans outils (8091) : ~75 s, fausse aussi. Question « conteneur » : aucun outil, ~54 s. Délai de l'application porté à 300 s. Le port 8091 répond « Empty reply » pendant ~5 s après `up` : attendre.

Sources : diapos 132-134 ; documentation Docker (MCP Gateway, `docker mcp gateway run`), exemples Compose de la communauté (Collabnix, Docker blog). L'application `app.py` a été testée hors conteneur avec un faux modèle et un faux serveur MCP (transport « streamable HTTP », SDK `mcp` 1.30) : boucle d'appel d'outils, cas sans passerelle et affichage validés.

À valider / points d'attention :
1. **Modèle avec appel d'outils** : `ai/qwen3:1.7b` appelle bien l'outil (testé le 21/11/2026). `ai/qwen3` sans étiquette = 8B, trop lourd. Tous les modèles ne gèrent pas l'appel d'outils : si « Aucun outil appelé » à l'étape 5, changer de modèle dans les deux fichiers Compose.
2. **Qualité des réponses** : la question « dernière version de Docker Desktop » donne une réponse fausse avec et sans outil. Prévenir la classe, ou choisir une question dont la réponse est plus robuste.
3. **Image de la passerelle** : version fixée `v0.44.3` ; ne pas passer à `latest` sans retester.
4. **Jeton** : transport `streaming` = jeton Bearer exigé (`MCP_GATEWAY_AUTH_TOKEN`). Le jeton du lab est factice et ne sert qu'en local.
5. **Démarrage** : la passerelle peut mettre quelques secondes à écouter ; le port 8091 répond « Empty reply » ~5 s après `up`.
6. **Socket Docker sous Windows** : fonctionne avec Docker Desktop (moteur Linux) ; à confirmer sur les postes de la formation.
7. **SDK `mcp`** : borné `>=1.12,<2` (API différente en 2.x).
8. **Variable `MODEL_URL`** : même point d'attention qu'au lab A3 (`/engines/v1`).
9. **Sécurité** : insister sur le socket Docker monté et sur l'injection par le contenu des pages web (lien avec le lab S6).
10. **Ports** : 8090 et 8091 libres.
11. **Durée** : prévoir 60 minutes (téléchargements + 1 à 3 min par réponse sur processeur).
12. **Lien avec la suite** : A8 combinera ce lab avec un agent en sandbox (lab S7).
