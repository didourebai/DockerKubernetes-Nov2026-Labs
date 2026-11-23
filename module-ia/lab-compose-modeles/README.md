# Module IA — Lab basique A3 : Docker Compose et les modèles d'IA

> **Niveau :** Débutant | **Durée estimée :** 30 minutes
> **Prérequis :** Lab A2 (Model Runner actif), **Docker Compose 2.38 ou plus** (`docker compose version`), Module 05 (Docker Compose)
> **Accès à un service externe :** **non requis** : le modèle tourne localement

## 🎯 Objectifs

- Déclarer un **modèle d'IA** dans un fichier Compose, à côté de l'application qui l'utilise
- Comprendre comment Compose **injecte l'adresse et le nom du modèle** dans le conteneur (`endpoint_var`, `model_var`)
- Vérifier qu'un service **n'accède qu'aux modèles qu'on lui accorde explicitement**

> **Rappel (diapo 132) :** la section `models` déclare les modèles à la racine de `compose.yaml` ; `endpoint_var` transmet au service l'adresse du modèle via une variable d'environnement ; le service doit déclarer le modèle dans sa propre section `models` pour pouvoir l'utiliser.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal. Les commandes se lancent depuis le dossier `module-ia/lab-compose-modeles` (fichiers `compose.yaml` et `app/` fournis).

---

## Étape 1 — Vérifier les prérequis

```bash
docker compose version
docker model status
```

**Résultat attendu :** Compose en version **2.38.0 ou plus**, et Model Runner en marche.

---

## Étape 2 — Lire le fichier Compose

Ouvrez `compose.yaml` :

```yaml
services:
  chat-app:
    build: ./app
    ports:
      - "8080:5000"
    models:
      llm:
        endpoint_var: MODEL_URL
        model_var: MODEL_NAME

models:
  llm:
    model: ai/smollm2
    context_size: 4096
```

**Repérez :**
- le bloc **`models:` à la racine** : déclare le modèle `llm` (`ai/smollm2`) et sa **taille de contexte**
- le bloc **`models:` dans le service** : **accorde** l'accès du service au modèle
- `endpoint_var` / `model_var` : les **noms des variables** qui recevront l'adresse et le nom du modèle

**Question :** pourquoi ne pas écrire l'adresse du modèle directement dans le code de l'application ? (Portabilité : le même fichier Compose peut fonctionner sur une autre infrastructure.)

Lisez aussi `app/app.py` : l'application lit `MODEL_URL` et `MODEL_NAME` et envoie une requête de type OpenAI (comme `appel.py` du lab A2).

---

## Étape 3 — Voir la configuration résolue

Depuis le dossier du lab :

```bash
docker compose config
```

**Observez :** Compose valide le fichier et affiche la configuration complète, y compris la section des modèles.

---

## Étape 4 — Démarrer l'application et le modèle

```bash
docker compose up -d --build
docker compose ps
docker model list
```

**À noter :** si le modèle n'est pas encore sur votre poste, son téléchargement peut prendre un peu de temps. Compose fournit le modèle à l'application, **sans que vous ayez à le lancer vous-même**.

**Résultat attendu :** le service `chat-app` est `running`, et `ai/smollm2` figure dans la liste des modèles.

---

## Étape 5 — Voir les variables injectées

```bash
docker compose exec chat-app sh -c "env | grep MODEL"
```

**Résultat attendu :**
```
MODEL_URL=http://model-runner.docker.internal/v1/
MODEL_NAME=ai/smollm2
```

Ces deux variables **ne figurent nulle part** dans le `Dockerfile` ni dans le code : elles ont été injectées par Compose. (L'adresse injectée se termine par `/v1/` : c'est la même API qu'au lab A2, sous une autre forme d'adresse.)

---

## Étape 6 — Utiliser l'application

Ouvrez **http://localhost:8080**, posez une question (par exemple « Qu'est-ce qu'un conteneur ? ») et lisez la réponse.

**Observez :** le nom du modèle affiché, le temps de réponse (le premier appel est le plus lent), la qualité de la réponse d'un petit modèle.

---

## Étape 7 — L'accès doit être accordé explicitement

Le fichier `compose-sans-acces.yaml` déclare le **même modèle** mais ne l'accorde **pas** au service. On lance cette variante dans un projet séparé, sur le port 8081 :

```bash
docker compose -p lab-a3-sans -f compose-sans-acces.yaml up -d --build
docker compose -p lab-a3-sans -f compose-sans-acces.yaml exec chat-app sh -c "env | grep MODEL"
```

**Résultat attendu :** aucune variable `MODEL_*` : la commande ne renvoie rien.

Ouvrez **http://localhost:8081**, posez une question : l'application affiche l'erreur « Variables MODEL_URL et MODEL_NAME absentes ».

**Question :** que se passerait-il, du point de vue de la sécurité, si tous les services avaient accès à tous les modèles ? (Moindre privilège : un service accède seulement à ce qui lui est accordé.)

---

## Étape 8 — Changer le modèle ou le contexte

Dans `compose.yaml`, remplacez `context_size: 4096` par `2048`, puis :

```bash
docker compose up -d
docker compose ps
```

**Observez :** Compose reconfigure le modèle (`llm Configured`) et laisse le conteneur `chat-app` tel quel (`Running`) : il ne touche qu'à ce qui a changé. La taille du contexte limite la quantité de texte que le modèle peut considérer à la fois, et influe sur la mémoire utilisée.

Pour utiliser un autre modèle, il suffit de changer la ligne `model:` (par exemple un autre modèle du catalogue `ai/…`) : le code de l'application ne change pas.

---

## Étape 9 — Nettoyer

```bash
docker compose down
docker compose -p lab-a3-sans -f compose-sans-acces.yaml down
```

Les modèles téléchargés ne sont **pas** supprimés par `down` ; pour libérer l'espace :

```bash
docker model rm ai/smollm2
docker rmi lab-compose-modeles-chat-app lab-a3-sans-chat-app
```

(Une erreur sur une image déjà supprimée est normale.)

---

## ✅ Récapitulatif

| Élément | Rôle |
|---|---|
| `models:` (racine) | Déclare les modèles : nom, `context_size`, options |
| `models:` (dans le service) | **Accorde** le modèle au service |
| `endpoint_var` | Variable qui reçoit l'adresse du modèle |
| `model_var` | Variable qui reçoit le nom du modèle |
| `docker compose up -d` | Démarre l'application **et** fournit le modèle |

**À retenir :**
- Compose traite un modèle comme une **dépendance** de l'application, comme une base de données
- l'application ne contient **ni adresse ni nom** de modèle en dur
- un service n'accède qu'aux modèles qui lui sont accordés

---

➡️ **Suivant :** Lab A4 — MCP Toolkit et MCP Gateway
