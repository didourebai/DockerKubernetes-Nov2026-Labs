# Module IA — Lab intermédiaire A5 : Un assistant IA pour le portail IT-Support

> **Niveau :** Intermédiaire | **Durée estimée :** 45 minutes
> **Prérequis :** Labs A2 (Model Runner), A3 (Compose et modèles) et A4 (MCP Toolkit), Docker Compose 2.38 ou plus
> **Accès à un service externe :** **oui** (le serveur DuckDuckGo fait des recherches sur Internet, sans compte)

## 🎯 Objectifs

- Assembler dans **un seul `compose.yaml`** : l'application, un **modèle** (Model Runner) et la **MCP Gateway**
- Constater qu'un modèle peut **décider d'appeler un outil** (recherche web) fourni par un serveur MCP
- Comparer la réponse **avec** et **sans** outils
- Comprendre les risques de sécurité de la passerelle (socket Docker, jeton)

> **Rappel (diapo 134) :** l'application parle à la **MCP Gateway**, qui lance le serveur MCP (ex. DuckDuckGo) dans un conteneur ; en parallèle, l'application utilise le modèle fourni par Model Runner.

```
Navigateur ──► assistant (Flask) ──► Model Runner (ai/qwen3:1.7b)
                    │
                    └──► mcp-gateway ──► serveur MCP duckduckgo (conteneur)
```

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal. Les commandes se lancent depuis `module-ia/lab-assistant-it`.

---

## Étape 1 — Vérifier les prérequis

```bash
docker compose version
docker model status
```

**Résultat attendu :** Compose 2.38.0 ou plus, Model Runner en marche.

---

## Étape 2 — Lire le fichier Compose

Ouvrez `compose.yaml` et repérez :

- le service **`assistant`** : reçoit `MODEL_URL` et `MODEL_NAME` (section `models`, comme au lab A3) et l'adresse de la passerelle `MCP_GATEWAY_URL`
- le modèle **`ai/qwen3:1.7b`** (1,1 Go) : un petit modèle qui sait **demander l'appel d'un outil**
- le service **`mcp-gateway`** : image `docker/mcp-gateway` à une **version fixée** (`v0.44.3` ; l'étiquette `latest` pointe vers une version plus ancienne), avec `--servers=duckduckgo` (serveur MCP à exposer) et `--transport=streaming` (accessible en HTTP par les autres conteneurs)
- le **montage du socket Docker** (`/var/run/docker.sock`) : la passerelle en a besoin pour **lancer** les serveurs MCP comme conteneurs
- le **jeton** `MCP_GATEWAY_AUTH_TOKEN` : partagé entre la passerelle et l'application

**Questions :**
- Pourquoi la passerelle a-t-elle besoin du socket Docker, et quel risque cela représente-t-il ? (Elle peut créer des conteneurs sur l'hôte : à réserver à une image de confiance.)
- Pourquoi un jeton est-il utile entre l'application et la passerelle ?

---

## Étape 3 — Lire le code de l'assistant

Dans `app/app.py`, repérez la boucle (fonction `repondre`) :

1. l'application demande à la passerelle la **liste des outils** disponibles
2. elle l'envoie au modèle avec la question
3. si le modèle répond par une **demande d'appel d'outil**, l'application l'exécute via la passerelle et renvoie le résultat au modèle
4. le modèle produit la **réponse finale**

**Question :** qui exécute réellement l'outil : le modèle ou l'application ? (L'application : le modèle ne fait que **demander** l'appel.)

---

## Étape 4 — Démarrer l'ensemble

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs mcp-gateway
```

**Résultat attendu :** les services `assistant` et `mcp-gateway` sont `running`. Les journaux de la passerelle indiquent le serveur chargé et les outils exposés. Le premier démarrage peut être long (téléchargement du modèle et de l'image du serveur MCP).

---

## Étape 5 — Poser une question qui demande une recherche

Ouvrez **http://localhost:8090** et posez :

```text
Quelle est la dernière version stable de Docker Desktop ?
```

> ⏱️ **Patience :** sur un poste sans carte graphique, la réponse prend **2 à 3 minutes** (le modèle réfléchit, appelle l'outil, puis rédige). Ne rechargez pas la page.

**Observez :** la réponse, et la liste **« Outils appelés »** sous la réponse, par exemple :
```
search {"query": "Docker Desktop latest version", "max_results": 1}
```

C'est le **modèle** qui a choisi l'outil (`search`) et ses arguments.

**Lisez la réponse d'un œil critique :** un petit modèle peut mal exploiter le résultat de la recherche et répondre un numéro de version faux. L'outil apporte une information, il ne garantit pas une bonne réponse.

Dans un autre terminal :

```bash
docker compose logs mcp-gateway
```

**Résultat attendu :**
```
  - Calling tool search with arguments: object with 2 field(s)
  - Running mcp/duckduckgo with [run --rm -i --init --security-opt no-new-privileges ... --network lab-assistant-it_default]
  > Calling tool search took: 13.2s
```

La passerelle a lancé un conteneur `mcp/duckduckgo` **le temps de l'appel** (`--rm`), puis l'a supprimé : c'est pourquoi `docker ps` ne le montre pas.

---

## Étape 6 — Une question qui n'a pas besoin d'outil

Posez :

```text
Explique en deux phrases ce qu'est un conteneur.
```

**Observez :** la section « Aucun outil appelé » : le modèle décide lui-même s'il a besoin d'un outil. La réponse arrive plus vite (environ 1 minute sur processeur).

---

## Étape 7 — Comparer avec et sans outils

La variante `compose-sans-outils.yaml` démarre la même application **sans passerelle**, sur le port 8091 :

```bash
docker compose -p lab-a5-sans -f compose-sans-outils.yaml up -d --build
```

Attendez quelques secondes que l'application démarre, ouvrez **http://localhost:8091** et reposez la question de l'étape 5.

**Observez :** « Aucun outil appelé » : le modèle répond de mémoire, avec ce qu'il a appris lors de son entraînement. La réponse est souvent **affirmée avec assurance** alors qu'elle est ancienne ou inventée. Comparez avec l'étape 5 : laquelle pouvez-vous **vérifier** ? (Celle avec outil : vous voyez la recherche effectuée.)

**Question :** pourquoi dit-on qu'un outil réduit le risque de réponse inventée ? Quels nouveaux risques apporte-t-il ? (Contenu externe non fiable lu par le modèle, voir le lab S6 sur l'injection.)

---

## Étape 8 — Nettoyer

```bash
docker compose down
docker compose -p lab-a5-sans -f compose-sans-outils.yaml down
```

Les modèles ne sont pas supprimés par `down` ; pour libérer l'espace :

```bash
docker model rm ai/qwen3:1.7b
docker rmi lab-assistant-it-assistant lab-a5-sans-assistant docker/mcp-gateway:v0.44.3
```

---

## ✅ Récapitulatif

| Élément | Rôle |
|---|---|
| `models:` | Fournit le modèle à l'application (lab A3) |
| `mcp-gateway` | Point d'entrée unique vers les serveurs MCP ; les lance dans des conteneurs |
| `--servers=duckduckgo` | Serveur MCP exposé par la passerelle |
| Boucle d'appel d'outils | Le modèle **demande**, l'application **exécute**, le modèle conclut |

**À retenir :**
- un assistant utile = modèle + outils, tous déclarés dans le même Compose
- la passerelle isole chaque serveur MCP, mais son accès au socket Docker est un privilège à protéger
- un modèle n'appelle un outil que s'il en **a besoin** et s'il **sait** le faire (voir les notes formateur)

---

➡️ **Suivant :** Lab A6 — Applications agentiques avec un labspace Docker
