# Module IA — Lab basique A2 : Docker Model Runner

> **Niveau :** Débutant | **Durée estimée :** 30 minutes
> **Prérequis :** Docker Desktop récent (Model Runner activé) **ou** Docker Engine avec `docker model install-runner` ; environ 1 Go d'espace disque pour le modèle ; connexion Internet pour le télécharger
> **Accès à un modèle externe :** **non requis** : le modèle tourne sur votre poste

## 🎯 Objectifs

- Télécharger et exécuter un modèle d'IA **localement** avec `docker model`
- Appeler le modèle par une **API compatible OpenAI**, depuis l'hôte puis depuis un conteneur
- Comprendre ce que cela change pour une application : **la même API** qu'un service de modèle de langage habituel, mais locale

> **Rappel (diapo 131) :** les modèles se tirent depuis Docker Hub ou Hugging Face comme des **artefacts OCI** ; vos applications les appellent comme une API de modèle de langage habituelle.

> **Note Windows / Mac :** une commande par ligne. Sous Windows PowerShell, utilisez `curl.exe` (et non `curl`, qui est un alias d'une autre commande).

---

## Étape 1 — Vérifier que Model Runner fonctionne

```bash
docker model status
```

**Résultat attendu :** `Docker Model Runner is running`.

Si la commande `docker model` n'est pas reconnue ou si le service ne tourne pas :
- **Docker Desktop :** activez Docker Model Runner dans les paramètres de Docker Desktop
- **Docker Engine (Linux) :** installez-le avec `docker model install-runner`

Pour appeler l'API **depuis l'hôte** (étape 4), l'accès TCP doit être activé (port **12434**). Sur Docker Engine, il l'est par défaut ; sur Docker Desktop, activez-le dans les paramètres de Model Runner ou avec `docker desktop enable model-runner --tcp 12434`.

---

## Étape 2 — Télécharger un modèle

```bash
docker model pull ai/smollm2
docker model list
docker model inspect ai/smollm2
```

**Résultat attendu :** `ai/smollm2` apparaît dans la liste, avec sa taille. Le premier téléchargement peut prendre un peu de temps ; ensuite le modèle est en cache local.

**Observez :** le nom ressemble à celui d'une image (`espace-de-noms/nom`). Les modèles sont des artefacts OCI stockés dans un registre, comme vos images.

---

## Étape 3 — Discuter avec le modèle

Une question unique :

```bash
docker model run ai/smollm2 "Bonjour !"
```

Mode interactif (sans question, une conversation s'ouvre ; quittez avec la commande indiquée à l'écran ou `Ctrl+D`) :

```bash
docker model run ai/smollm2
```

**À noter :** le premier appel charge le modèle en mémoire et peut être lent (environ 30 secondes sur un poste sans carte graphique) ; les suivants sont plus rapides. Un petit modèle comme `smollm2` répond vite mais reste limité : jugez la **qualité** de ses réponses (en français, en précision).

---

## Étape 4 — Appeler l'API depuis l'hôte

Model Runner expose une API compatible OpenAI. Depuis l'hôte, l'adresse de base est `http://localhost:12434/engines/v1`.

Liste des modèles disponibles :

**Mac / Linux**

```bash
curl http://localhost:12434/engines/v1/models
```

**Windows (PowerShell)**

```powershell
curl.exe http://localhost:12434/engines/v1/models
```

Demande de complétion de conversation. Le corps de la requête est fourni dans `module-ia/lab-model-runner/fichiers/requete.json` (depuis la racine du dépôt des labs) :

**Mac / Linux**

```bash
curl http://localhost:12434/engines/v1/chat/completions -H "Content-Type: application/json" -d @module-ia/lab-model-runner/fichiers/requete.json
```

**Windows (PowerShell)**

```powershell
curl.exe http://localhost:12434/engines/v1/chat/completions -H "Content-Type: application/json" -d "@module-ia\lab-model-runner\fichiers\requete.json"
```

**Résultat attendu :** un document JSON avec un champ `choices`, dont le premier élément contient `message.content` : la réponse du modèle.

**Questions :**
- Quel est le **rôle** de chaque champ de la requête (`model`, `messages`, `role`, `content`) ?
- En quoi cette requête ressemble-t-elle à un appel à un service de modèle de langage en ligne ? (Même format : seule l'**adresse de base** change.)

---

## Étape 5 — Appeler le modèle depuis un conteneur

Une application conteneurisée ne parle pas à `localhost` : sur Docker Desktop, elle joint Model Runner par `http://model-runner.docker.internal`. Copiez le script `appel.py` dans un dossier de travail, puis exécutez-le dans un conteneur :

**Windows (PowerShell)**

```powershell
mkdir C:\Labs\modele
Copy-Item module-ia\lab-model-runner\fichiers\appel.py C:\Labs\modele\
cd C:\Labs\modele
docker run --rm -v "${PWD}:/app" -w /app python:3.12-slim python appel.py
```

**Mac / Linux**

```bash
mkdir -p ~/labs/modele
cp module-ia/lab-model-runner/fichiers/appel.py ~/labs/modele/
cd ~/labs/modele
docker run --rm -v "$(pwd):/app" -w /app python:3.12-slim python appel.py
```

**Résultat attendu :** le script affiche l'adresse utilisée et la réponse du modèle.

Si l'adresse par défaut ne fonctionne pas dans votre environnement, passez une autre adresse par la variable `MODEL_URL`. Avec Docker Desktop (accès TCP activé, étape 1), `host.docker.internal` fonctionne aussi :

**Windows (PowerShell)**

```powershell
docker run --rm -e MODEL_URL=http://host.docker.internal:12434/engines/v1 -v "${PWD}:/app" -w /app python:3.12-slim python appel.py
```

**Mac / Linux**

```bash
docker run --rm -e MODEL_URL=http://host.docker.internal:12434/engines/v1 -v "$(pwd):/app" -w /app python:3.12-slim python appel.py
```

> Sur **Docker Engine (Linux, sans Docker Desktop)**, l'adresse documentée est `http://172.17.0.1:12434/engines/v1`. Elle est **refusée** avec Docker Desktop.

**Observez :** l'application lit l'adresse du modèle dans une **variable d'environnement** (`MODEL_URL`). C'est exactement le mécanisme que Docker Compose automatisera au lab A3 (`endpoint_var`).

---

## Étape 6 — Sécurité et ressources

**Une API sans authentification.** L'API de Model Runner n'est pas authentifiée : tout client qui peut l'atteindre, y compris d'autres conteneurs du même réseau Docker, peut télécharger, charger et exécuter des modèles, et envoyer des requêtes d'inférence.

**Questions :**
- Faut-il exposer le port 12434 sur un réseau partagé ? (Non : accès local seulement.)
- Que risque-t-on si un conteneur non fiable (voir le lab S6 sur l'injection de prompt) peut appeler cette API ?

**Ressources :** un modèle consomme disque, mémoire et processeur (ou GPU), et sa **fenêtre de contexte** influe sur la mémoire. Comparez la taille indiquée par `docker model list` avec la mémoire disponible de votre poste.

---

## Étape 7 — Nettoyer

```bash
docker model rm ai/smollm2
docker model list
```

(Gardez le modèle si vous enchaînez avec le lab A3 : il l'utilise.) Supprimez les dossiers `modele` créés à l'étape 5.

---

## ✅ Récapitulatif

| Commande / adresse | Action |
|----------|--------|
| `docker model status` | Vérifier que Model Runner tourne |
| `docker model pull ai/smollm2` | Télécharger un modèle |
| `docker model list` / `inspect` | Lister / détailler les modèles |
| `docker model run ai/smollm2 "question"` | Poser une question (ou ouvrir une conversation sans question) |
| `docker model rm ai/smollm2` | Supprimer un modèle |
| `http://localhost:12434/engines/v1` | API OpenAI-compatible, **depuis l'hôte** |
| `http://model-runner.docker.internal/engines/v1` | La même API, **depuis un conteneur** |

**À retenir :**
- un modèle se manipule comme une image : `pull`, `list`, `rm`
- l'API est **compatible OpenAI** : une application change seulement l'adresse de base
- l'API locale n'est **pas authentifiée** : ne l'exposez pas

---

➡️ **Suivant :** Lab A3 — Docker Compose et les modèles d'IA
