# Notes formateur — Lab A5 (à valider avant la formation)

> Exécution du 21/11/2026 : OK avec `ai/qwen3:1.7b` (1,1 Go) et `docker/mcp-gateway:v0.44.3` (`latest` = v2 de juillet 2026). `ai/qwen3` sans étiquette = 8B, 5 Go : trop lourd pour la classe. Question « dernière version de Docker Desktop » : appel `search` effectué, réponse en ~185 s sur processeur, **fausse** (24.0.0) ; sans outils (8091) : ~75 s, fausse aussi. Question « conteneur » : aucun outil, ~54 s. Délai de l'application porté à 300 s. Le port 8091 répond « Empty reply » pendant ~5 s après `up` : attendre.

Sources : diapos 132-134 ; documentation Docker (MCP Gateway, `docker mcp gateway run`), exemples Compose de la communauté (Collabnix, Docker blog). **Lab non exécuté avec Docker.** L'application `app.py` a été testée hors conteneur avec un faux modèle et un faux serveur MCP (transport « streamable HTTP », SDK `mcp` 1.30) : boucle d'appel d'outils, cas sans passerelle et affichage validés.

À valider :
1. **Modèle avec appel d'outils** : le lab utilise `ai/qwen3` ; la diapo 134 montre `ai/gemma3`. Tous les modèles ne gèrent pas l'appel d'outils. Si le modèle ne demande jamais d'outil (« Aucun outil appelé » à l'étape 5), essayer un autre modèle du catalogue `ai/` compatible, et ajuster `model:` dans les deux fichiers Compose.
2. **Image de la passerelle** : `docker/mcp-gateway:latest`. Une source indique que `latest` peut être une version ancienne ; si l'image ne se comporte pas comme attendu, **fixer une version** (par ex. `docker/mcp-gateway:v2` ou un numéro précis).
3. **Options de la passerelle** : `--servers=duckduckgo`, `--transport=streaming`, `--port=8811` d'après la référence `docker mcp gateway run`. Vérifier le chemin exact du point d'accès (`/mcp`) et l'écoute sur `0.0.0.0` dans le conteneur (journaux de `mcp-gateway`).
4. **Jeton** : pour les transports `sse` et `streaming`, une source indique qu'un jeton Bearer est exigé (`MCP_GATEWAY_AUTH_TOKEN`, généré si absent). Confirmer le comportement et l'en-tête attendu ; le jeton du lab est factice et ne sert qu'en local.
5. **Catalogue des serveurs** : en Compose, la passerelle utilise son catalogue par défaut ; confirmer que `duckduckgo` y est résolu (et que l'image `mcp/duckduckgo` est téléchargée au premier appel).
6. **Socket Docker sous Windows** : le montage `/var/run/docker.sock` fonctionne avec Docker Desktop (moteur Linux) ; à confirmer sur les postes de la formation.
7. **SDK `mcp`** : version bornée `>=1.12,<2` ; l'API a changé en 2.x (non utilisée ici).
8. **Variable `MODEL_URL`** : même point d'attention qu'au lab A3 (forme de l'adresse, `/engines/v1`).
9. **Sécurité** : insister sur le socket Docker monté et sur l'injection par le contenu des pages web (lien avec le lab S6).
10. **Ports** : 8090 et 8091 libres.
11. **Lien avec la suite** : A8 combinera ce lab avec un agent en sandbox (lab S7).
