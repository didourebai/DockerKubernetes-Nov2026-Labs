# Module IA — Lab de synthèse A8 : La boucle complète, de l'assistant IA à l'agent en sandbox

> **Niveau :** Avancé | **Durée estimée :** 75 minutes
> **Prérequis :** Lab A5 (assistant IA, stack Compose fonctionnelle), Lab S7 (agent en mode clone), `sbx` installé et connecté, accès à Claude Code
> **Accès à un service externe :** **oui** (Claude Code pour l'agent ; DuckDuckGo pour l'assistant)

## 🎯 Objectifs

- Faire **évoluer** l'assistant IA du lab A5 en confiant la tâche à un **agent dans un sandbox**
- **Valider** le travail de l'agent avec **votre** moteur Docker : build, Compose, tests, relecture du diff
- Utiliser le **modèle local** (Model Runner) comme **second regard** sur le diff, et mesurer ses limites
- Relier les deux modules : **Docker AI** (modèle, outils, Compose) et **Docker Sandboxes** (agent isolé)

> **Règle (diapo 140) :** on conteneurise l'application, on met l'agent en sandbox. L'agent construit avec **son** moteur Docker ; vous validez avec le vôtre.

```
              ┌──────────── sandbox (microVM) ────────────┐
 vous ──────► │ agent Claude Code : modifie le code,      │
 (consigne)   │ construit l'image avec SON moteur Docker  │
              └──────────────────┬────────────────────────┘
                                 │ git fetch (branche)
                                 ▼
 vous : relecture + validation avec VOTRE Docker
        docker compose up  ──►  assistant ──► Model Runner
                                    └──────► MCP Gateway ──► DuckDuckGo
```

> ⚠️ Projet de formation uniquement : aucune donnée sensible.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Vérifier que l'assistant de départ fonctionne

Depuis `module-ia/lab-assistant-it` (lab A5) :

```bash
docker compose up -d --build
docker compose ps
```

Ouvrez **http://localhost:8090** et posez la question courte :

```text
Explique en deux phrases ce qu'est un conteneur.
```

> ⏱️ Sur un poste sans carte graphique, la réponse prend environ **1 minute**.

**Résultat attendu :** une réponse et « Aucun outil appelé ». Puis arrêtez la stack :

```bash
docker compose down
```

---

## Étape 2 — Mesurer le point faible actuel

On va chercher un défaut réel de l'assistant. **Sans** la passerelle MCP, l'application échoue lorsqu'elle essaie de s'y connecter. Lancez uniquement l'assistant :

```bash
docker compose up -d --build assistant
```

`depends_on` démarre aussi la passerelle : arrêtez-la pour simuler une panne.

```bash
docker compose stop mcp-gateway
```

Ouvrez **http://localhost:8090** et posez n'importe quelle question.

**Observez :** le message d'erreur affiché à l'utilisateur. Est-il lisible pour quelqu'un du support ? Notez-le tel quel : c'est le point de départ.

Il manque aussi une route de **santé** (`/health`) et un `HEALTHCHECK` dans l'image, comme le portail du lab S7.

```bash
docker compose down
```

---

## Étape 3 — Préparer le projet pour l'agent

Copiez l'assistant hors du dépôt des labs, et faites-en un dépôt Git. Depuis la racine du dépôt :

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse module-ia\lab-assistant-it C:\Labs\assistant-agent
cd C:\Labs\assistant-agent
```

**Mac / Linux**

```bash
cp -r module-ia/lab-assistant-it ~/labs/assistant-agent
cd ~/labs/assistant-agent
```

```bash
git init
git add .
git commit -m "Assistant IT-Support v1"
```

---

## Étape 4 — Confier la tâche à l'agent

```bash
sbx run --clone --name lab-a8 claude .
```

Donnez-lui cette consigne :

```text
Crée une branche feat/robustesse. Améliore l'assistant IT-Support (dossier app/) :
1. ajoute une route GET /health qui renvoie du JSON : status, model (variable MODEL_NAME) et gateway_configured (true si MCP_GATEWAY_URL est définie),
2. ajoute un HEALTHCHECK dans app/Dockerfile qui interroge /health, sans installer curl,
3. quand la passerelle MCP est injoignable, affiche un message clair en français ("Les outils de recherche sont indisponibles") au lieu de l'erreur technique, puis réponds quand même avec le modèle seul, sans outils,
4. ne modifie ni compose.yaml ni compose-sans-outils.yaml.
Construis l'image de l'application (app/), lance-la seule, vérifie que /health répond, puis fais un commit.
```

**À noter :** l'agent ne peut **pas** démarrer la stack complète dans son sandbox (le modèle est fourni par **votre** Model Runner). Il construit et teste l'image seule : c'est volontaire, et c'est à vous de valider le reste.

Laissez-le travailler. **Ne quittez pas le sandbox** avant l'étape 5.

---

## Étape 5 — Récupérer et relire le travail

Dans une **seconde fenêtre**, dans le dossier `assistant-agent` :

```bash
git status
git fetch sandbox-lab-a8
git log --oneline sandbox-lab-a8/feat/robustesse
git diff --stat HEAD..sandbox-lab-a8/feat/robustesse
```

**Résultat attendu :** `working tree clean`, puis la liste des fichiers modifiés.

**Questions :**
- L'agent a-t-il modifié des fichiers interdits (`compose.yaml`) ?
- A-t-il ajouté des dépendances ou des fichiers non demandés ?

Lisez le diff complet :

```bash
git diff HEAD..sandbox-lab-a8/feat/robustesse
```

---

## Étape 6 — Valider avec votre moteur Docker

Extrayez la branche et lancez la stack complète :

```bash
git checkout -b feat/robustesse sandbox-lab-a8/feat/robustesse
docker compose up -d --build
docker compose ps
```

Attendez quelques secondes, puis :

```bash
docker inspect --format "{{.State.Health.Status}}" assistant-agent-assistant-1
```

> Le nom du conteneur dépend du nom du dossier : relevez-le avec `docker compose ps` et adaptez la commande.

Ouvrez **http://localhost:8090/health** : vous devez voir un JSON avec le nom du modèle et `gateway_configured`.

**Test de la panne (l'étape 2, rejouée) :**

```bash
docker compose stop mcp-gateway
```

Ouvrez **http://localhost:8090** et posez : « Explique en deux phrases ce qu'est un conteneur. »

**Résultat attendu :** un message clair en français indiquant que les outils sont indisponibles, **suivi d'une réponse du modèle** (plus lente : environ 1 minute sur processeur).

Redémarrez la passerelle et testez la question qui demande un outil :

```bash
docker compose start mcp-gateway
```

Posez : « Quelle est la dernière version stable de Docker Desktop ? » (2 à 3 minutes sur processeur).

**Résultat attendu :** « Outils appelés » affiche `search`. La réponse peut être **fausse** : c'est le modèle, pas l'agent, qui l'a rédigée.

Complétez la grille de validation :

| Critère | Attendu | Résultat |
|---|---|---|
| `/health` | JSON avec `status`, `model`, `gateway_configured` | ........ |
| `HEALTHCHECK` | État `healthy` après quelques secondes | ........ |
| Panne de la passerelle | Message clair **et** réponse du modèle | ........ |
| Fonctionnement normal | Appel de l'outil `search` conservé | ........ |
| `compose.yaml` | Inchangé | ........ |
| Dépendances (`requirements.txt`) | Inchangées (ou justifiées) | ........ |

---

## Étape 7 — Second regard : le modèle local relit le diff (optionnel)

Le code ne quitte pas votre poste : on demande au modèle **local** de résumer les changements. Enregistrez le diff :

```bash
git diff HEAD~1..HEAD -- app > diff.txt
```

**Mac / Linux**

```bash
docker model run ai/qwen3:1.7b "Résume en trois points ce diff et signale les risques : $(cat diff.txt)"
```

**Windows (PowerShell)**

```powershell
$d = Get-Content diff.txt -Raw
docker model run ai/qwen3:1.7b "Résume en trois points ce diff et signale les risques : $d"
```

**Questions :**
- Le résumé est-il fidèle au diff que **vous** avez lu à l'étape 5 ?
- Signale-t-il un risque que vous aviez manqué, ou invente-t-il un problème ?
- Peut-on remplacer la relecture humaine par ce second regard ? (Non : un petit modèle local aide à **survoler**, il ne **valide** pas.)

---

## Étape 8 — Conclure et nettoyer

Si vous acceptez le travail, la branche `feat/robustesse` est déjà dans votre dépôt local. Nettoyez :

```bash
docker compose down
sbx rm lab-a8
sbx ls
```

Libérez l'espace (images et modèle) :

```bash
docker rmi assistant-agent-assistant docker/mcp-gateway:v0.44.3
docker model rm ai/qwen3:1.7b
```

(Une erreur sur une image déjà supprimée est normale ; adaptez le nom de l'image au nom de votre dossier.)

---

## 🧭 Bilan : le parcours complet

| Module | Ce qu'on a utilisé dans ce lab |
|---|---|
| Docker AI | Model Runner (modèle local), Compose `models:`, MCP Gateway et serveur DuckDuckGo |
| Docker Sandboxes | `sbx run --clone`, microVM, moteur Docker privé de l'agent, `git fetch` |
| Docker de base | `docker compose`, `HEALTHCHECK`, `docker inspect`, nettoyage |

**À retenir :**
- l'agent **accélère**, la validation reste **humaine**, avec des critères vérifiables
- ce que l'agent ne peut pas tester (ici le modèle) se teste **chez vous**
- un modèle, local ou non, peut se tromper : les outils et les relectures réduisent le risque sans le supprimer
- isolation de l'agent, moindre privilège des services et contrôle des sorties sont les mêmes principes d'un bout à l'autre

---

➡️ **Fin du parcours IA.** Retour au [sommaire du module IA](../README.md) s'il existe, sinon aux labs S1 à S13 et A1 à A7.
