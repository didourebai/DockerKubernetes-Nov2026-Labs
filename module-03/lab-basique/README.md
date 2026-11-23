# Module 03 — Lab basique : Construire des images Docker

> **Niveau :** Débutant  
> **Durée estimée :** 30 minutes


> **Note Windows / Mac :** les commandes sont écrites pour fonctionner dans les deux
> environnements. Quand ce n'est pas possible, deux variantes sont données :
> **Windows (PowerShell)** et **Mac / Linux**.

---

## 🎯 Objectifs

- Écrire un Dockerfile complet
- Comprendre les instructions clés
- Utiliser le cache Docker intelligemment
- Publier une image sur Docker Hub

---

## Étape 1 — Votre premier Dockerfile from scratch

Placez-vous dans le dossier du lab, qui contient déjà `index.html` et `Dockerfile` :

**Windows (PowerShell) :**
```powershell
cd labs\module-03\lab-basique
```

**Mac / Linux :**
```bash
cd labs/module-03/lab-basique
```

Ouvrez `index.html` avec un éditeur de texte (Notepad, VS Code…) : c'est une page web simple.

Ouvrez le `Dockerfile` :

```dockerfile
FROM nginx:1.30-alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
```

Construisez et testez :

```bash
docker build -t mon-site-web:v1 .
docker run -d -p 8080:80 --name mon-site mon-site-web:v1
# Ouvrir http://localhost:8080
```

---

## Étape 2 — Observer le cache Docker

Modifiez le fichier `index.html` (changez un mot) et reconstruisez :

```bash
docker build -t mon-site-web:v2 .
```

Observez les lignes `CACHED` : Docker **réutilise** les couches non modifiées. C'est beaucoup plus rapide !

Maintenant, modifiez le Dockerfile lui-même (ajoutez un commentaire) et reconstruisez. Le cache est **invalidé** à partir de la ligne modifiée.

---

## Étape 3 — Utiliser les instructions ARG et ENV

Remplacez le contenu du `Dockerfile` par cette version plus élaborée :

```dockerfile
FROM nginx:1.30-alpine

# ARG : variable disponible seulement au moment du build
ARG VERSION=1.0.0
ARG BUILD_DATE

# ENV : variable disponible dans le conteneur à l'exécution
ENV APP_VERSION=$VERSION
ENV NGINX_PORT=80

# Ajouter des métadonnées à l'image
LABEL maintainer="technicien-it@institution.ca"
LABEL version="$VERSION"
LABEL build-date="$BUILD_DATE"

COPY index.html /usr/share/nginx/html/index.html
EXPOSE $NGINX_PORT
```

Construire avec des arguments :

**Windows (PowerShell) :**
```powershell
docker build --build-arg VERSION=2.0.0 --build-arg BUILD_DATE=$(Get-Date -Format "yyyy-MM-dd") -t mon-site-web:v2 .
```

**Mac / Linux :**
```bash
docker build --build-arg VERSION=2.0.0 --build-arg BUILD_DATE=$(date +%Y-%m-%d) -t mon-site-web:v2 .
```

Vérifier les métadonnées (les deux environnements) :
```bash
docker inspect --format "{{json .Config.Labels}}" mon-site-web:v2
```

---

## Étape 4 — Créer un fichier .dockerignore

Le `.dockerignore` dit à Docker quels fichiers **ne pas** copier dans l'image.

Créez un fichier nommé `.dockerignore` (avec le point au début) dans le dossier du lab,
avec votre éditeur de texte, et ce contenu :

```
*.md
*.log
.git
.DS_Store
node_modules
__pycache__
*.pyc
```

> **Windows :** dans Notepad, choisissez « Tous les fichiers (*.*) » au moment
> d'enregistrer, sinon le fichier s'appellera `.dockerignore.txt`.
> Évitez `echo ... > .dockerignore` dans PowerShell 5 : le fichier serait encodé
> en UTF-16 et Docker ne le lirait pas correctement.

> 💡 Sans `.dockerignore`, si votre dossier contient des gros fichiers inutiles (vidéos, archives), ils seraient copiés dans l'image et l'alourdir.

---

## Étape 5 — Comparer la taille des images

```bash
docker images mon-site-web
```

Comparez différentes images de base :

```bash
# Très petite
docker pull nginx:alpine
# Standard  
docker pull nginx:latest
# Ubuntu complète (beaucoup plus grosse)
docker pull ubuntu:24.04

docker images nginx
docker images ubuntu
```

> 💡 **Règle d'or :** Toujours préférer les images `alpine` ou `slim` en production — elles sont plus légères et ont moins de vulnérabilités.

---

## Étape 6 — Se connecter à Docker Hub et pousser une image

```bash
# Se connecter (créez un compte sur hub.docker.com si vous n'en avez pas)
docker login

# Renommer l'image avec votre nom d'utilisateur Docker Hub
docker tag mon-site-web:v1 VOTRE_NOM/mon-site-web:v1

# Pousser l'image
docker push VOTRE_NOM/mon-site-web:v1
```

> Remplacez `VOTRE_NOM` par votre nom d'utilisateur Docker Hub.

---

## 🧹 Nettoyage

```bash
docker stop mon-site
docker rm mon-site
docker rmi mon-site-web:v1 mon-site-web:v2
```

---

## ✅ Récapitulatif

| Instruction Dockerfile | Rôle |
|------------------------|------|
| `FROM` | Image de base |
| `WORKDIR` | Dossier de travail |
| `COPY` | Copier des fichiers |
| `RUN` | Exécuter une commande au build |
| `ENV` | Variable d'environnement (runtime) |
| `ARG` | Variable au moment du build |
| `EXPOSE` | Déclarer un port |
| `LABEL` | Métadonnées |
| `CMD` | Commande de démarrage |

---

➡️ **Suivant :** [Lab fil rouge — Optimisation du portail](../lab-fil-rouge/README.md)
