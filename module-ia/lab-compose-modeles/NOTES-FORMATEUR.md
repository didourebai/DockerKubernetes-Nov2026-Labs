# Notes formateur — Lab A3 (à valider avant la formation)

> Exécution du 21/11/2026 : toutes les étapes OK. `MODEL_URL` injectée = `http://model-runner.docker.internal/v1/` (app.py fonctionne tel quel). `compose-sans-acces.yaml` : aucune variable, message d'erreur affiché. Étape 8 : `llm Configured`, conteneur non recréé. `env | grep MODEL` entre guillemets doubles fonctionne sous PowerShell. Nettoyage : image `lab-compose-modeles-chat-app` ajoutée.

Sources : diapo 132 ; documentation Docker (« Define AI models in Compose », référence Compose `models`, configuration de Model Runner) trouvée par recherche web. **Lab non exécuté avec Docker** ; l'application `app.py` a été testée hors conteneur avec un faux serveur de modèle (cas « avec accès » et « sans accès » validés) et les fichiers YAML ont été validés syntaxiquement.

À valider :
1. **Version de Compose** : la documentation indique Compose 2.38.0 ou plus. Vérifier `docker compose version` sur les postes.
2. **Forme de `MODEL_URL`** : le lab suppose une adresse de base de type `…/engines/v1` (avec ou sans barre finale) à laquelle l'application ajoute `/chat/completions`. Relever la valeur réelle injectée (étape 5) et ajuster `app.py` au besoin.
3. **Téléchargement du modèle** : confirmer que `docker compose up` télécharge `ai/smollm2` s'il est absent (comportement attendu de la section `models`) ; sinon, demander `docker model pull ai/smollm2` avant (lab A2).
4. **Étape 7 :** le projet `lab-a3-sans` : vérifier que Compose accepte un modèle déclaré à la racine mais non référencé par un service (aucune variable injectée).
5. **Nom du modèle pour Model Runner** : la docs montre `ai/smollm2` (`model:`) et le service `chat-app` ; la forme courte (liste `- llm`) génère d'autres noms de variables : non utilisée ici.
6. **`docker compose exec … sh -c "env | grep MODEL"`** sous PowerShell : les guillemets doubles externes et le `|` interne sont transmis tels quels au conteneur ; à confirmer.
7. **Ports** : 8080 et 8081 doivent être libres.
8. Fichiers `compose.yaml` et `app/` : lancer les commandes depuis le dossier `module-ia/lab-compose-modeles`.
9. **Lien avec la diapo 134** : le lab A5 ajoutera la MCP Gateway au même Compose.
