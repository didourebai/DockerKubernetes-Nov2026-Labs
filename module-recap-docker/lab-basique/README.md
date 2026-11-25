# Module récap Docker — Lab basique : Le compteur de visites, de A à Z

> **Niveau :** Débutant  
> **Durée estimée :** 50 minutes  
> **Prérequis :** Modules 01 à 06 terminés  
> **Note :** ce lab est **indépendant du fil rouge** — il sert à réviser toute la journée Docker.


> **Note Windows / Mac :** les commandes sont écrites pour fonctionner dans les deux
> environnements. Quand ce n'est pas possible, deux variantes sont données :
> **Windows (PowerShell)** et **Mac / Linux**.

---

## 🎯 Objectifs

Refaire, sur une **nouvelle application**, tout le parcours Docker vu aujourd'hui :

| Partie | Ce que vous faites | Module révisé |
|--------|--------------------|---------------|
| 1 | Lancer, inspecter et manipuler des conteneurs | 01 – 02 |
| 2 | Construire une image optimisée et la valider | 03 – 04 |
| 3 | Relier deux conteneurs avec un réseau et un volume, **à la main** | 05 |
| 4 | Faire la même chose en une commande avec **Docker Compose** | 05 |
| 5 | Passer à l'échelle avec **Docker Swarm** | 06 |
| 6 | Tout nettoyer | — |

### L'application : un compteur de visites

```
Navigateur ──► app (Python/Flask, port 5000) ──► redis (base de données)
               "Visite numéro 42"                 stocke le compteur
               "Servi par le conteneur abc123"    dans un volume
```

Chaque rafraîchissement de la page incrémente un compteur stocké dans **Redis**.
La page affiche aussi le **nom du conteneur** qui a répondu — utile pour la Partie 5.

```
lab-basique/
├── app/
│   ├── app.py              ← Application web (pas besoin de la modifier)
│   ├── requirements.txt    ← Dépendances Python
│   ├── Dockerfile          ← Multi-stage, non-root, healthcheck
│   └── .dockerignore
├── docker-compose.yml      ← Partie 4
├── .env                    ← Variables lues par Compose
└── docker-stack.yml        ← Partie 5
```

Placez-vous dans le dossier du lab :

**Windows (PowerShell) :**
```powershell
cd labs\module-recap-docker\lab-basique
```

**Mac / Linux :**
```bash
cd labs/module-recap-docker/lab-basique
```

---

## Partie 1 — Échauffement : conteneurs et images (modules 01 – 02)

### Étape 1 — Lancer et observer un conteneur

```bash
# Vérifier que Docker répond
docker version

# Lancer Redis en arrière-plan avec un nom
docker run -d --name echauffement redis:7-alpine

# Le voir tourner
docker ps

# Lire ses journaux
docker logs echauffement
```

**Résultat attendu :** dans les logs, la ligne `Ready to accept connections`.

### Étape 2 — Entrer dans le conteneur

```bash
# Exécuter une commande dans le conteneur en marche
docker exec echauffement redis-cli set formation docker
docker exec echauffement redis-cli get formation

# Ouvrir un shell (tapez exit pour sortir)
docker exec -it echauffement sh
```

### Étape 3 — Inspecter

```bash
# Image utilisée et état du conteneur
docker inspect echauffement --format "Image: {{.Config.Image}} - Etat: {{.State.Status}}"

# Consommation CPU / mémoire (une seule mesure)
docker stats --no-stream echauffement

# Les images présentes sur votre machine
docker images
```

### Étape 4 — Le conteneur est éphémère

```bash
docker rm -f echauffement
docker run -d --name echauffement redis:7-alpine
docker exec echauffement redis-cli get formation
```

**Résultat attendu :** une ligne vide — la donnée a disparu avec l'ancien conteneur.
👉 On réglera ce problème avec un **volume** à la Partie 3.

```bash
docker rm -f echauffement
```

---

## Partie 2 — Construire l'image (modules 03 – 04)

### Étape 5 — Lire le Dockerfile

Ouvrez `app/Dockerfile` et retrouvez les bonnes pratiques vues aux modules 03 et 04 :

| Instruction | Bonne pratique |
|-------------|----------------|
| `FROM python:3.12-slim AS builder` puis un 2e `FROM` | **Multi-stage** : l'image finale ne garde que l'essentiel |
| `COPY requirements.txt` **avant** `COPY app.py` | **Ordre des couches** : le `pip install` reste en cache quand le code change |
| `USER appuser` | L'application ne tourne **pas en root** |
| `HEALTHCHECK` | Docker sait si l'application répond vraiment |
| `.dockerignore` | Les fichiers inutiles ne sont pas envoyés au build |

### Étape 6 — Valider puis construire

```bash
# Vérifier le Dockerfile sans construire (module 04)
docker buildx build --check app/
```

**Résultat attendu :** `Check complete, no warnings found.`

```bash
# Construire et tagger l'image
docker build -t compteur:v1 app/

# Sa taille et ses couches
docker images compteur
docker image history compteur:v1
```

### Étape 7 — Observer le cache

Relancez exactement la même commande :

```bash
docker build -t compteur:v1 app/
```

**Résultat attendu :** le build prend une seconde, les étapes affichent `CACHED`.

### Étape 8 — Tester l'image seule

```bash
docker run -d --name compteur-seul -p 8080:5000 compteur:v1

# L'application tourne-t-elle en root ?
docker exec compteur-seul whoami
```

**Résultat attendu :** `appuser` ✅

Attendez une dizaine de secondes, puis vérifiez l'état de santé :

```bash
docker ps --filter name=compteur-seul
```

**Résultat attendu :** la colonne STATUS affiche `(healthy)`.

Ouvrez **http://localhost:8080** : la page affiche **« Redis injoignable »** ❌  
C'est normal : le conteneur est seul, il n'existe aucun conteneur `redis` joignable.

```bash
docker rm -f compteur-seul
```

---

## Partie 3 — Réseau et volume, à la main (module 05)

### Étape 9 — Créer le réseau et le volume

```bash
docker network create reseau-recap
docker volume create donnees-redis
```

### Étape 10 — Lancer Redis puis l'application sur le même réseau

```bash
# Redis : données écrites dans le volume (dossier /data)
docker run -d --name redis --network reseau-recap -v donnees-redis:/data redis:7-alpine redis-server --appendonly yes

# L'application : elle cherche Redis sous le nom "redis"
docker run -d --name compteur --network reseau-recap -p 8080:5000 compteur:v1
```

Attendez que `compteur` soit `(healthy)` (`docker ps`), puis ouvrez **http://localhost:8080**
et rafraîchissez plusieurs fois : le compteur augmente ✅

> 💡 L'application joint Redis **par son nom** grâce au DNS du réseau personnalisé.

### Étape 11 — Prouver la persistance

```bash
# Valeur actuelle du compteur
docker exec redis redis-cli get visites

# Détruire le conteneur Redis...
docker rm -f redis

# ...et en recréer un NOUVEAU avec le même volume
docker run -d --name redis --network reseau-recap -v donnees-redis:/data redis:7-alpine redis-server --appendonly yes

docker exec redis redis-cli get visites
```

**Résultat attendu :** la même valeur qu'avant ✅ — contrairement à l'étape 4, les données ont survécu.

### Étape 12 — Nettoyer la Partie 3

```bash
docker rm -f compteur redis
docker network rm reseau-recap
docker volume rm donnees-redis
```

> 🤔 Cela fait beaucoup de commandes à retenir... C'est exactement ce que Compose simplifie.

---

## Partie 4 — Tout en un avec Docker Compose (module 05)

### Étape 13 — Lire le fichier Compose

Ouvrez `docker-compose.yml` et retrouvez tout ce que vous avez fait à la main :

| À la main (Partie 3) | Dans `docker-compose.yml` |
|----------------------|---------------------------|
| `docker build -t compteur:v1 app/` | `build: ./app` + `image: compteur:v1` |
| `docker network create reseau-recap` | `networks: reseau-recap` |
| `docker volume create donnees-redis` | `volumes: donnees-redis` |
| `-v donnees-redis:/data` | `volumes: - donnees-redis:/data` |
| `-p 8080:5000` | `ports: - "${APP_PORT:-8080}:5000"` |
| Lancer Redis **avant** l'app | `depends_on: condition: service_healthy` |

### Étape 14 — Lancer la stack

```bash
# --build : reconstruit l'image si besoin / --wait : attend que tout soit "healthy"
docker compose up -d --build --wait

docker compose ps
```

Ouvrez **http://localhost:8080** et rafraîchissez plusieurs fois ✅

```bash
# Les journaux de l'application
docker compose logs app
```

### Étape 15 — Personnaliser avec le fichier .env

Dans le fichier `.env`, modifiez :

```
APP_TITLE=Ma revision Docker
APP_COLOR=#c0392b
```

Vérifiez puis appliquez :

```bash
docker compose config
docker compose up -d --wait
```

Rafraîchissez la page : nouveau titre, nouvelle couleur… et le compteur **continue** ✅  
Compose n'a recréé que le conteneur `app` — Redis et son volume n'ont pas bougé.

### Étape 16 — down n'efface pas le volume

```bash
docker compose down
docker volume ls
```

**Résultat attendu :** le volume `recap_donnees-redis` existe toujours.

```bash
docker compose up -d --wait
```

Rafraîchissez : le compteur reprend là où il s'était arrêté ✅

```bash
# On arrête la stack Compose avant de passer à Swarm (sans -v : on garde le volume !)
docker compose down
```

---

## Partie 5 — Passer à l'échelle avec Docker Swarm (module 06)

### Étape 17 — Comparer les deux fichiers

Ouvrez `docker-stack.yml`. Il ressemble au fichier Compose, avec deux différences :

| `docker-compose.yml` | `docker-stack.yml` |
|----------------------|--------------------|
| `build: ./app` | ❌ Swarm ne construit pas d'image : on utilise `compteur:v1` déjà construite |
| `depends_on` | ❌ Non supporté par Swarm |
| — | ✅ `deploy:` : `replicas: 3`, `update_config`, `restart_policy` |
| réseau `bridge` | réseau `overlay` (peut s'étendre sur plusieurs machines) |

### Étape 18 — Initialiser Swarm et déployer

```bash
docker swarm init

docker stack deploy -c docker-stack.yml recap
```

Attendez une trentaine de secondes, puis :

```bash
docker stack services recap
```

**Résultat attendu :** `recap_app` en `3/3` et `recap_redis` en `1/1`.

Ouvrez **http://localhost:8080** : titre « (Swarm) » en orange… et le compteur **continue encore** !

> 💡 La stack s'appelle `recap`, comme le projet Compose : elle réutilise donc le même
> volume `recap_donnees-redis`.

### Étape 19 — Observer la répartition de charge

Envoyez plusieurs requêtes et regardez le nom du conteneur qui répond :

**Windows (PowerShell) :**
```powershell
1..6 | ForEach-Object { [regex]::Match((Invoke-WebRequest -UseBasicParsing http://localhost:8080).Content, '<code>[0-9a-f]+').Value }
```

**Mac / Linux :**
```bash
for i in 1 2 3 4 5 6; do curl -s http://localhost:8080 | grep -o '<code>[0-9a-f]*'; done
```

**Résultat attendu :** les 3 noms de conteneurs se succèdent — Swarm répartit les requêtes ✅

> 💡 Dans le navigateur, le nom change rarement : le navigateur réutilise la même connexion.

### Étape 20 — Auto-réparation

```bash
# Supprimer un conteneur de l'application (simuler une panne)
docker ps --filter name=recap_app
docker rm -f <ID_D_UN_CONTENEUR>

# Quelques secondes plus tard
docker stack ps recap
docker stack services recap
```

**Résultat attendu :** une tâche `Failed` ou `Shutdown`, une nouvelle tâche `Running`,
et `recap_app` revient à `3/3` ✅

### Étape 21 — Mise à jour sans interruption

```bash
docker service update --env-add APP_COLOR=#27ae60 recap_app
```

Swarm remplace les conteneurs **un par un** (`parallelism: 1`, `delay: 5s`).
Rafraîchissez la page pendant la mise à jour : elle reste disponible, puis passe au vert ✅

---

## Partie 6 — Grand nettoyage

```bash
# Supprimer la stack et quitter Swarm
docker stack rm recap
docker swarm leave --force

# Supprimer le volume (attendez quelques secondes que les conteneurs soient arrêtés)
docker volume rm recap_donnees-redis

# Supprimer l'image construite
docker image rm compteur:v1

# Voir l'espace disque utilisé par Docker
docker system df
```

> ⚠️ `docker system prune` supprime **tous** les conteneurs arrêtés, réseaux inutilisés et images
> sans tag de votre machine — pas seulement ceux de ce lab. À utiliser en connaissance de cause.

---

## 🧠 Défi final — Testez-vous

<details>
<summary>1. Pourquoi l'application affichait « Redis injoignable » à l'étape 8 ?</summary>

Le conteneur était seul, sur le réseau `bridge` par défaut : aucun conteneur nommé `redis`
n'était joignable, et le réseau par défaut ne fait pas de résolution par nom.
</details>

<details>
<summary>2. Quelle est la différence entre <code>docker compose down</code> et <code>docker compose down -v</code> ?</summary>

`down` supprime les conteneurs et les réseaux. `down -v` supprime **en plus** les volumes :
le compteur serait remis à zéro.
</details>

<details>
<summary>3. Pourquoi copie-t-on <code>requirements.txt</code> avant <code>app.py</code> dans le Dockerfile ?</summary>

Pour profiter du cache : tant que `requirements.txt` ne change pas, l'étape `pip install`
n'est pas refaite, même si `app.py` est modifié.
</details>

<details>
<summary>4. Pourquoi ne peut-on pas mettre 3 répliques de l'app avec Docker Compose sur le port 8080 ?</summary>

Avec Compose, chaque conteneur voudrait réserver le port 8080 de la machine : conflit.
Swarm, lui, publie le port **une seule fois** (routing mesh) et répartit les requêtes entre les répliques.
</details>

<details>
<summary>5. Quelles instructions de docker-compose.yml Swarm ignore-t-il ?</summary>

`build` (Swarm ne construit pas d'images) et `depends_on`. Il utilise en revanche la section `deploy`.
</details>

---

## ✅ Récapitulatif de la journée Docker

| Module | Commandes clés |
|--------|----------------|
| 01 – 02 | `docker run -d --name`, `docker ps`, `docker logs`, `docker exec -it`, `docker inspect`, `docker stats`, `docker rm -f` |
| 03 | `docker build -t`, `docker images`, `docker image history` |
| 04 | Multi-stage, `USER`, `HEALTHCHECK`, `.dockerignore`, `docker buildx build --check` |
| 05 | `docker network create`, `docker volume create`, `--network`, `-v`, `docker compose up -d --wait`, `docker compose down`, `.env` |
| 06 | `docker swarm init`, `docker stack deploy`, `docker stack services`, `docker service update`, `docker stack rm` |

---

➡️ **Suivant :** [Module 07 — Kubernetes](../../module-07/lab-basique/README.md)
