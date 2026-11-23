# Notes formateur — Lab A2 (à valider avant la formation)

> Exécution du 21/11/2026 : étapes 2 à 5 OK. `ai/smollm2` = 256 Mio ; premier `docker model run` ≈ 30 s (processeur seul). `curl.exe … -d "@module-ia\…\requete.json"` OK sous PowerShell 5.1, réponse `choices[0].message.content` (le champ `model` de la réponse contient un chemin de fichier local : normal). Depuis un conteneur : `model-runner.docker.internal` OK, `host.docker.internal:12434` OK, `172.17.0.1:12434` **refusé** sur Docker Desktop (Linux Engine seulement) : étape 5 corrigée. Mode interactif : sortie non vérifiée (pas de terminal interactif lors du test).

Sources : diapo 131 ; documentation Docker sur Model Runner (API reference, IDE integrations, page d'accueil), billets et tutoriels trouvés par recherche web. **Les pages n'ont pas été lues en entier et le lab n'a pas été exécuté.**

À valider :
1. **Activation du TCP sur Docker Desktop** : un tutoriel cite `docker desktop enable model-runner --tcp 12434` ; la page *IDE integrations* indique que le TCP est activé par défaut sur Docker Engine, sur le port 12434. Vérifier le comportement et le libellé des paramètres sur la version installée.
2. **Adresse de l'API** : la forme `…/engines/v1` (documentation) et la forme `…/engines/llama.cpp/v1` (tutoriels plus anciens) coexistent. Le lab utilise `/engines/v1` ; vérifier qu'elle répond.
3. **Adresse depuis un conteneur** : la documentation donne `http://model-runner.docker.internal` pour les conteneurs ; une autre page donne `http://172.17.0.1:12434`. Le script essaie la première par défaut et accepte `MODEL_URL`. Tester sur Windows, Mac et Linux (sur Linux, `host.docker.internal` demande `extra_hosts`).
4. **Nom du modèle dans la requête** : `ai/smollm2`, conforme à la diapo 131. Vérifier que la réponse JSON a bien `choices[0].message.content`.
5. **Mode interactif** : la façon de quitter `docker model run` sans question n'est pas vérifiée ; relever la commande réelle (`/bye` ?) et corriger l'étape 3.
6. **PowerShell** : `curl.exe` (le `curl` de PowerShell 5 est un alias de `Invoke-WebRequest`). `-d "@chemin"` : vérifier l'encodage du fichier JSON (UTF-8 sans BOM).
7. **Ressources** : `ai/smollm2` est un petit modèle ; prévoir le temps du premier téléchargement et un espace disque suffisant pour la classe (réseau partagé).
8. **Sécurité** : la mention « API non authentifiée » vient de la documentation (page *Docker Model Runner*) ; ne pas exposer le port hors de l'hôte.
