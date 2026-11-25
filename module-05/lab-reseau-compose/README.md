# Module 05 — Lab réseau : Réseaux bridge et Docker Compose multi-réseaux

> **Niveau :** Débutant  
> **Durée estimée :** 35 minutes  
> **Prérequis :** [Lab basique du module 05](../lab-basique/README.md) terminé


> **Note Windows / Mac :** les commandes sont écrites pour fonctionner dans les deux
> environnements. Quand ce n'est pas possible, deux variantes sont données :
> **Windows (PowerShell)** et **Mac / Linux**.

---

## 🎯 Objectifs

- Comprendre la différence entre le réseau `bridge` **par défaut** et un réseau bridge **personnalisé**
- Choisir la plage d'adresses (subnet) d'un réseau et l'adresse IP d'un conteneur
- Connecter / déconnecter un conteneur à chaud
- Isoler des services avec **plusieurs réseaux** dans Docker Compose
- Créer un réseau **interne** (sans accès Internet)
- Observer la répartition de charge DNS quand on scale un service

---

## Partie A — Le réseau bridge en détail

### Étape 1 — Le réseau bridge par défaut

Sans option `--network`, un conteneur rejoint le réseau `bridge` par défaut :

```bash
docker run -d --name alpha nginx:alpine
docker run -d --name beta nginx:alpine

# Alpha peut-il joindre Beta par son NOM ?
docker exec alpha ping -c 2 -W 2 beta
```

**Résultat attendu :** `ping: bad address 'beta'` ❌

```bash
# Récupérer l'adresse IP de beta sur le réseau bridge
docker inspect beta --format '{{.NetworkSettings.Networks.bridge.IPAddress}}'

# Pinguer cette IP (remplacez par l'adresse affichée, par ex. 172.17.0.3)
docker exec alpha ping -c 2 <IP_DE_BETA>
```

**Résultat attendu :** le ping par IP fonctionne ✅

> 💡 Le réseau `bridge` par défaut **n'a pas de DNS** entre conteneurs : il faut connaître les IP,
> qui changent à chaque redémarrage. C'est pourquoi on crée toujours ses propres réseaux.

### Étape 2 — Un réseau bridge personnalisé avec sa propre plage d'adresses

```bash
# Créer un réseau en choisissant le subnet et la passerelle
docker network create --driver bridge --subnet 10.20.0.0/24 --gateway 10.20.0.1 reseau-labo

# Voir sa configuration
docker network inspect reseau-labo --format '{{range .IPAM.Config}}{{.Subnet}} via {{.Gateway}}{{end}}'
```

### Étape 3 — Connecter des conteneurs à chaud

Pas besoin de recréer les conteneurs : on les branche sur le nouveau réseau.

```bash
docker network connect reseau-labo alpha

# On peut même imposer l'adresse IP (elle doit appartenir au subnet)
docker network connect --ip 10.20.0.50 reseau-labo beta

# Cette fois, le nom est résolu !
docker exec alpha ping -c 2 beta
```

**Résultat attendu :** `PING beta (10.20.0.50)` ✅

```bash
# Beta est maintenant sur DEUX réseaux, avec une IP sur chacun
docker inspect beta --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}={{$v.IPAddress}} {{end}}'
```

**Résultat attendu :** `bridge=172.17.0.x reseau-labo=10.20.0.50`

### Étape 4 — Déconnecter et isoler

```bash
# Débrancher beta du réseau personnalisé
docker network disconnect reseau-labo beta
docker exec alpha ping -c 2 -W 2 beta
```

**Résultat attendu :** `bad address 'beta'` — beta n'est plus joignable par son nom.

```bash
# Un conteneur sur un AUTRE réseau personnalisé est totalement isolé
docker network create reseau-isole
docker run -d --name gamma --network reseau-isole nginx:alpine

docker exec alpha ping -c 2 -W 2 gamma
```

**Résultat attendu :** `bad address 'gamma'` — deux réseaux différents ne se voient pas. 🔒

### Étape 5 — Publier un port seulement sur la machine locale

```bash
# 127.0.0.1:8090:80 → le port n'est accessible que depuis VOTRE machine,
# pas depuis les autres ordinateurs du réseau de l'institution
docker run -d --name delta -p 127.0.0.1:8090:80 nginx:alpine

docker port delta
```

**Résultat attendu :** `80/tcp -> 127.0.0.1:8090`. Ouvrez **http://localhost:8090** ✅

### Étape 6 — Nettoyer la partie A

```bash
docker rm -f alpha beta gamma delta
docker network rm reseau-labo reseau-isole
```

---

## Partie B — Docker Compose avec plusieurs réseaux

### Étape 7 — Découvrir l'architecture

Placez-vous dans le dossier du lab :

**Windows (PowerShell) :**
```powershell
cd labs\module-05\lab-reseau-compose
```

**Mac / Linux :**
```bash
cd labs/module-05/lab-reseau-compose
```

```
lab-reseau-compose/
├── docker-compose.yml   ← 4 services, 2 réseaux
├── .env                 ← Port publié par le proxy
└── nginx/
    └── nginx.conf       ← Le proxy transmet /api/ au service api
```

```
          Navigateur (http://localhost:8080)
                     │
   ┌─────────────────┼───────── réseau frontend ─────┐
   │              proxy (Nginx)                      │
   │                 │                               │
   │              api (whoami) ◄── alias backend-api │
   └─────────────────┼───────────────────────────────┘
   ┌─────────────────┼───────── réseau backend ──────┐
   │                 │         (internal: true)      │
   │   outils ──► cache (Redis)    10.50.0.0/24      │
   └─────────────────────────────────────────────────┘
```

| Service | Image | Réseaux | Port publié |
|---------|-------|---------|-------------|
| `proxy` | `nginx:alpine` | frontend | **8080** |
| `api` | `traefik/whoami` | frontend + backend | aucun |
| `cache` | `redis:7-alpine` | backend | aucun |
| `outils` | `busybox` | backend | aucun |

Points clés du `docker-compose.yml` :

```yaml
name: lab-reseau                # Préfixe des réseaux : lab-reseau_frontend, lab-reseau_backend

services:
  api:
    depends_on:
      cache:
        condition: service_healthy    # Attend que Redis soit "healthy"
    networks:
      frontend:
        aliases:
          - backend-api               # Second nom DNS sur le réseau frontend
      backend:

networks:
  backend:
    driver: bridge
    internal: true                    # Pas d'accès Internet
    ipam:
      config:
        - subnet: 10.50.0.0/24        # Plage d'adresses imposée
```

### Étape 8 — Lancer la stack

```bash
docker compose up -d
```

Observez l'ordre de démarrage dans la sortie : `cache` passe à **Healthy** avant que `api` démarre.

```bash
docker compose ps

# Les réseaux créés par Compose
docker network ls --filter name=lab-reseau
```

Testez dans votre navigateur :
- **http://localhost:8080** → `Proxy OK - essayez /api/`
- **http://localhost:8080/api/** → la réponse de `whoami` (nom du conteneur, ses IP…) ✅

> 💡 L'api affiche **deux IP** : une sur `frontend`, une sur `backend` (10.50.0.x).

### Étape 9 — Vérifier l'isolation

```bash
# 1. Le proxy joint l'api (même réseau frontend)
docker compose exec proxy wget -qO- http://api

# 2. ... aussi par son alias
docker compose exec proxy wget -qO- http://backend-api

# 3. Le proxy NE voit PAS le cache (réseau backend uniquement)
docker compose exec proxy ping -c 2 -W 2 cache
```

**Résultat attendu :** les deux premiers fonctionnent, le 3e affiche `bad address 'cache'` 🔒

```bash
# 4. Depuis le réseau backend, Redis répond
docker compose exec outils sh -c "echo PING | nc -w 2 cache 6379"
```

**Résultat attendu :** `+PONG` ✅

```bash
# 5. L'alias "backend-api" n'existe que sur frontend
docker compose exec outils ping -c 2 -W 2 backend-api
```

**Résultat attendu :** `bad address 'backend-api'` — un alias est **propre à un réseau**.

### Étape 10 — Le réseau interne n'a pas accès à Internet

```bash
docker compose exec outils wget -T 3 -qO- http://example.com

docker network inspect lab-reseau_backend --format "Interne: {{.Internal}} - Subnet: {{range .IPAM.Config}}{{.Subnet}}{{end}}"
```

**Résultat attendu :** `wget: bad address 'example.com'` puis `Interne: true - Subnet: 10.50.0.0/24`

> 💡 Idéal pour une base de données : elle n'a aucune raison de sortir sur Internet.

### Étape 11 — Scaler l'api : la répartition de charge par DNS

```bash
# Passer à 3 conteneurs api
docker compose up -d --scale api=3

# Le nom "api" renvoie maintenant 3 adresses IP
docker compose exec outils nslookup api
```

Attendez 5 secondes (le temps que Nginx rafraîchisse son cache DNS), puis :

```bash
docker compose exec proxy sh -c 'for i in 1 2 3 4 5 6 7 8 9 10; do wget -qO- http://127.0.0.1/api/ | grep Hostname; done'
```

**Résultat attendu :** plusieurs valeurs de `Hostname` différentes — Nginx répartit les requêtes
entre les 3 conteneurs. Vous pouvez aussi rafraîchir **http://localhost:8080/api/** dans le navigateur.

> 💡 La répartition n'est **pas parfaitement équitable** : un même conteneur peut répondre
> plusieurs fois de suite. Si vous ne voyez que 1 ou 2 `Hostname` différents, relancez la commande.

> ⚠️ On ne peut scaler que les services **sans port publié** : deux conteneurs ne peuvent pas
> écouter sur le même port 8080 de l'hôte. C'est pour cela que seul le proxy publie un port.

### Étape 12 — Nettoyer

```bash
docker compose down

# Vérifier que les réseaux ont bien été supprimés
docker network ls --filter name=lab-reseau
```

---

## ✅ Récapitulatif

| Commande / clé | Action |
|----------------|--------|
| `docker network create --subnet ... --gateway ...` | Réseau avec plage d'adresses choisie |
| `docker network connect [--ip ...] <réseau> <conteneur>` | Brancher un conteneur à chaud |
| `docker network disconnect <réseau> <conteneur>` | Débrancher un conteneur |
| `-p 127.0.0.1:8090:80` | Publier un port uniquement en local |
| `networks:` (plusieurs) dans un service | Un service sur plusieurs réseaux |
| `aliases:` | Nom DNS supplémentaire sur un réseau |
| `internal: true` | Réseau sans accès Internet |
| `ipam.config.subnet` | Choisir la plage d'adresses dans Compose |
| `depends_on.condition: service_healthy` | Attendre qu'un service soit prêt |
| `docker compose up -d --scale <service>=N` | Lancer N conteneurs d'un service |

| Réseau `bridge` par défaut | Réseau bridge personnalisé |
|----------------------------|----------------------------|
| ❌ Pas de résolution par nom | ✅ DNS intégré (nom du conteneur / service) |
| Tous les conteneurs sans `--network` s'y retrouvent | Isolation : seuls les conteneurs ajoutés se voient |
| Subnet fixé par Docker | Subnet configurable |

---

➡️ **Suivant :** [Lab volumes — Persistance des données](../lab-volumes/README.md)
