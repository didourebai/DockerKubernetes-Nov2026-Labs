# DockerKubernetes-Nov2026-Labs

> Ce guide vous accompagne pas à pas dans la découverte de Docker et Kubernetes, en partant des bases jusqu'à des déploiements complets.

---

## À propos de ces laboratoires

Chaque module contient **au moins deux laboratoires** :

| Type | Description |
|------|-------------|
| 🔧 **Lab basique** | Exercices indépendants pour maîtriser les commandes du module |
| 🏗️ **Lab fil rouge** | Construction progressive du **IT-Support Portal** — un portail web interne d'institution |
| ➕ **Labs complémentaires** | Modules 05 et 07 : réseaux, volumes, ConfigMap, stockage, déploiements |

### Le cas d'utilisation fil rouge : IT-Support Portal

Un portail web interne qui permet aux professeurs de consulter l'état de l'infrastructure IT (serveurs, VMs, services).
Il est composé d'un **site web HTML** servi par **Nginx** et d'une **API Python (Flask)** qui retourne des informations système, avec un historique des connexions stocké dans **SQLite**.

À chaque module, le portail évolue et gagne en robustesse, jusqu'à être déployé sur Kubernetes avec Helm.

---

## Structure du dépôt

```
labs/
├── app/                        ← Code source de base du IT-Support Portal (version module 02)
├── module-01/                  ← Concepts des conteneurs
│   ├── lab-basique/
│   └── lab-fil-rouge/
├── module-02/                  ← Docker : architecture et composants
├── module-03/                  ← Construire votre première image Docker
├── module-04/                  ← Optimisation des builds Docker
├── module-05/                  ← Réseau, volumes et Docker Compose
│   ├── lab-basique/            ← Réseaux + premier fichier Compose
│   ├── lab-reseau-compose/     ← Réseaux bridge, Compose multi-réseaux
│   ├── lab-volumes/            ← Volumes nommés, bind mounts, sauvegarde
│   └── lab-fil-rouge/
├── module-06/                  ← Docker Swarm
├── module-07/                  ← Kubernetes
│   ├── lab-basique/            ← Pod, Deployment, Service
│   ├── lab-configmap/          ← ConfigMap et Secret
│   ├── lab-stockage/           ← PersistentVolumeClaim
│   ├── lab-deploiement/        ← Rolling update, scaling, rollback
│   └── lab-fil-rouge/
└── module-08/                  ← Helm
```

Chaque lab contient un `README.md` avec les instructions étape par étape, et tous les fichiers nécessaires (code, Dockerfile, YAML…).

---

## Prérequis

- **Docker Desktop** récent (4.50 ou plus) installé — [Télécharger ici](https://www.docker.com/products/docker-desktop/)
- **Kubernetes activé** dans Docker Desktop pour les modules 07 et 08 (*Settings → Kubernetes → Enable Kubernetes*)
- **Helm** pour le module 08 (`winget install Helm.Helm` sur Windows, `brew install helm` sur Mac)
- Un terminal (PowerShell sur Windows, Terminal sur Mac)
- Aucune connaissance en développement requise

> Les commandes sont écrites pour fonctionner à l'identique sous Windows et Mac.
> Quand ce n'est pas possible, deux variantes sont fournies.

---

## Progression du IT-Support Portal

| Version | Image | Module | Technologie introduite |
|---------|-------|--------|----------------------|
| démo | — | 01 | Découverte (conteneur existant) |
| v1.0 | `it-portal:v1` | 02 | Premier Dockerfile Python/Flask |
| v2.0 | `it-portal:v2` | 03 | Multi-stage build, utilisateur non-root, healthcheck |
| v3.0 | `it-portal:v3` | 04 | BuildKit, cache optimisé, Build Checks, Docker Scout |
| v4.0 | (Compose) | 05 | Nginx + SQLite + Docker Compose |
| v5.0 | `it-portal:v5` | 06 | Docker Swarm, haute disponibilité |
| v6.0 | `it-portal:v6` | 07 | Kubernetes (Deployments, Services, ConfigMap, PVC) |
| v7.0 | `it-portal:v7` | 08 | Helm — déploiement géré et rollback |

---

## Comment utiliser ces labs

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/didourebai/DockerKubernetes-Nov2026-Labs.git labs
   cd labs
   ```
2. Naviguez dans le module correspondant au cours du jour
3. Lisez le `README.md` du lab et suivez les étapes

---

*Formation Novembre 2026 — Fondements des conteneurs Docker et Kubernetes*
