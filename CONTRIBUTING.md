# Guide pour les formateurs

## Structure d'un lab

Chaque lab suit le même modèle :
- `README.md` : instructions étape par étape en français
- Fichiers de code prêts à l'emploi (Dockerfile, YAML, etc.)
- Résultat attendu indiqué clairement à chaque étape

## Convention de nommage des images

| Module | Tag image | Commande build |
|--------|-----------|----------------|
| 02 | `it-portal:v1` | `docker build -t it-portal:v1 .` |
| 03 | `it-portal:v2` | `docker buildx build -t it-portal:v2 .` |
| 04 | `it-portal:v3` | `docker buildx build -t it-portal:v3 .` |
| 05 | Compose build (`it-portal` v4) | `docker compose build` |
| 06 | `it-portal:v5` | `docker build -t it-portal:v5 app/` |
| 07 | `it-portal:v6` | `docker build -t it-portal:v6 app/` |
| 08 | `it-portal:v7` | `docker build -t it-portal:v7 app/` |

## Environnement testé

Labs exécutés de bout en bout le 21 novembre 2026 avec :

- Docker Desktop (Windows 11), moteur Docker 29.9, Compose v5.7, Buildx 0.38
- Kubernetes 1.36 intégré à Docker Desktop (cluster **kind**, 1 nœud)
- Helm 3.16

> **Kubernetes dans Docker Desktop :** les images construites avec `docker build`
> sont directement visibles du cluster (`imagePullPolicy: IfNotPresent`), aucun
> `kind load` n'est nécessaire. La StorageClass par défaut est en
> `WaitForFirstConsumer` : un PVC reste `Pending` tant qu'aucun Pod ne l'utilise,
> et il ne peut pas être agrandi.

## Conventions

- Une commande = une ligne (pas de `\` en fin de ligne : incompatible PowerShell)
- Commandes identiques Windows / Mac quand c'est possible ; sinon deux blocs
  **Windows (PowerShell)** et **Mac / Linux**
- Ne pas créer de fichiers avec `echo ... >` dans PowerShell 5 (encodage UTF-16) :
  fournir le fichier dans le dépôt
- Pas d'images Bitnami (retirées de Docker Hub depuis septembre 2025)
