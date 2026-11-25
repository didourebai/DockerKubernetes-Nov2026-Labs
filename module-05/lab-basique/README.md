# Module 05 — Lab basique : Réseau Docker et Docker Compose

> **Niveau :** Débutant  
> **Durée estimée :** 35 minutes


> **Note Windows / Mac :** les commandes sont écrites pour fonctionner dans les deux
> environnements. Quand ce n'est pas possible, deux variantes sont données :
> **Windows (PowerShell)** et **Mac / Linux**.

---

## 🎯 Objectifs

- Créer un réseau Docker pour faire communiquer des conteneurs
- Écrire un fichier `docker-compose.yml`
- Lancer plusieurs services avec une seule commande
- Gérer les variables d'environnement avec un fichier `.env`

---

## Partie A — Réseau Docker

### Étape 1 — Créer un réseau bridge

```bash
# Créer un réseau isolé
docker network create --driver bridge reseau-institution

# Lister les réseaux
docker network ls
```

### Étape 2 — Lancer deux conteneurs sur le même réseau

```bash
# Lancer un serveur web
docker run -d --network reseau-institution --name serveur-web nginx:alpine

# Lancer un conteneur "client"
docker run -d --network reseau-institution --name client-test nginx:alpine sleep 3600
```

### Étape 3 — Tester la communication entre conteneurs

```bash
# Depuis le client, pinguer le serveur web par son NOM
docker exec client-test ping -c 3 serveur-web

# Faire une requête HTTP au serveur web
docker exec client-test wget -qO- http://serveur-web

# Afficher le réseau d'un conteneur
docker inspect client-test --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}'
```
> 💡 Les conteneurs sur le même réseau peuvent se joindre **par leur nom** — pas besoin d'adresse IP !

### Étape 4 — Nettoyer

```bash
docker stop serveur-web client-test
docker rm serveur-web client-test
docker network rm reseau-institution
```

---

## Partie B — Docker Compose

### Étape 5 — Votre premier fichier Compose

Placez-vous dans le dossier du lab, qui contient déjà tous les fichiers :

**Windows (PowerShell) :**
```powershell
cd labs\module-05\lab-basique
```

**Mac / Linux :**
```bash
cd labs/module-05/lab-basique
```

```
lab-basique/
├── docker-compose.yml   ← Description des services
├── .env                 ← Variables (port, nom, version)
└── html/
    └── index.html       ← Page servie par Nginx
```

Ouvrez `docker-compose.yml` :

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "${NGINX_PORT:-8080}:80"     # Port lu dans le fichier .env (8080 par défaut)
    volumes:
      - ./html:/usr/share/nginx/html:ro   # Le dossier html/ est monté dans Nginx
    networks:
      - reseau-app

networks:
  reseau-app:
    driver: bridge
```

> 💡 Depuis Compose v2, la ligne `version: "3.9"` en haut du fichier n'est plus utile :
> Docker affiche un avertissement si elle est présente.

### Étape 6 — Lancer tous les services

```bash
# Démarrer tous les services en arrière-plan
docker compose up -d

# Voir les services actifs
docker compose ps

# Voir les logs de tous les services
docker compose logs

# Voir les logs d'un service spécifique en temps réel (Ctrl+C pour quitter)
docker compose logs -f web
```

Testez dans votre navigateur : **http://localhost:8080** → votre page Nginx.

### Étape 7 — Variables d'environnement avec .env

Ouvrez le fichier `.env` :

```
APP_NAME=Formation-Docker
APP_VERSION=1.0.0
NGINX_PORT=8080
```

Compose lit **automatiquement** ce fichier. Changez `NGINX_PORT=8080` en `NGINX_PORT=8081`,
enregistrez, puis voyez la configuration finale calculée par Compose :

```bash
docker compose config
```

Relancez :
```bash
docker compose up -d
```

Le site est maintenant sur **http://localhost:8081**. Remettez ensuite `NGINX_PORT=8080`.

### Étape 8 — Commandes utiles Compose

```bash
# Arrêter sans supprimer
docker compose stop

# Redémarrer
docker compose start

# Voir les processus de chaque service
docker compose top

# Entrer dans un service
docker compose exec web sh
# (tapez exit pour sortir)

# Arrêter ET supprimer les conteneurs et réseaux
docker compose down

# Arrêter ET supprimer + les volumes
docker compose down -v
```

### Étape 9 — Nettoyer

```bash
docker compose down
```

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `docker compose up -d` | Démarrer tous les services |
| `docker compose down` | Arrêter et supprimer |
| `docker compose ps` | État des services |
| `docker compose logs -f` | Logs en temps réel |
| `docker compose config` | Voir la configuration finale |
| `docker compose stop/start` | Pause/reprise |
| `docker compose exec <service> sh` | Entrer dans un service |

---

➡️ **Suivant :** [Lab réseau — Réseaux bridge et Compose multi-réseaux](../lab-reseau-compose/README.md)
