# Module IA — Lab basique A1 : Gordon, l'assistant IA de Docker

> **Niveau :** Débutant | **Durée estimée :** 25 minutes
> **Prérequis :** Docker Desktop récent, connecté à votre compte Docker, **Gordon activé** (la CLI `docker ai` demande Docker Desktop 4.74 ou plus d'après la documentation ; la disponibilité dépend de votre version et de votre accès au service)
> **À savoir :** l'utilisation de Gordon est comptée dans les limites de votre plan

## 🎯 Objectifs

- Utiliser Gordon dans le terminal (`docker ai`) pour **diagnostiquer** un conteneur qui s'arrête aussitôt
- Lire et **approuver ou refuser** chaque action qu'il propose
- Lui demander d'améliorer un Dockerfile, puis **valider** sa réponse avec vos propres outils
- Reconnaître les demandes **dangereuses** (`prune`, `down -v`)

> **Rappel (diapo 130) :** Gordon aide à diagnostiquer des conteneurs, expliquer des commandes et améliorer des Dockerfiles, dans Docker Desktop ou avec `docker ai`. **Vérifiez les recommandations avant toute action**, notamment `prune` et `down -v`.

> ⚠️ Gordon peut lire le **dossier de travail** depuis lequel vous le lancez. Lancez-le uniquement dans le dossier du lab, jamais dans un dossier contenant des fichiers sensibles.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal. Les réponses de Gordon varient d'une fois à l'autre : le lab évalue votre **démarche de validation**, pas un texte exact.

---

## Étape 1 — Vérifier que Gordon est disponible

```bash
docker ai version
```

**Résultat attendu :** un numéro de version s'affiche (par exemple `v1.33.0`).

> ⚠️ Ce numéro s'affiche **même si Gordon est désactivé** : il prouve seulement que le plugin est installé. Vérifiez qu'il répond vraiment :
>
> ```bash
> docker ai "Bonjour"
> ```
>
> Si vous obtenez `The "Docker AI" feature needs to be enabled in Docker Desktop settings`, activez Gordon dans les paramètres de Docker Desktop (section *AI*), cliquez sur **Apply**, et vérifiez que vous êtes connecté à votre compte Docker.

Ouvrez l'interface interactive pour la découvrir, puis quittez-la :

```bash
docker ai
```

À la première utilisation, acceptez les conditions si elles sont demandées.

---

## Étape 2 — Provoquer une panne

Copiez le projet fourni et ouvrez-le. Depuis la racine du dépôt des labs :

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse module-ia\lab-gordon\projet-panne C:\Labs\projet-panne
cd C:\Labs\projet-panne
```

**Mac / Linux**

```bash
mkdir -p ~/labs
cp -r module-ia/lab-gordon/projet-panne ~/labs/projet-panne
cd ~/labs/projet-panne
```

Construisez l'image et démarrez un conteneur :

```bash
docker build -t lab-a1:panne .
docker run -d --name lab-a1 lab-a1:panne
docker ps -a --filter name=lab-a1
```

**Résultat attendu :** le conteneur est dans l'état **Exited**, avec un code de sortie différent de 0.

---

## Étape 3 — Votre diagnostic d'abord

Sans Gordon, notez votre hypothèse :

```bash
docker logs lab-a1
docker inspect --format "{{.State.ExitCode}}" lab-a1
```

**Résultat attendu :**
```
python: can't open file '/app/main.py': [Errno 2] No such file or directory
2
```

**Question :** que dit le message d'erreur ? Quelle est, selon vous, la cause et la correction ?

---

## Étape 4 — Demander à Gordon

Toujours dans `projet-panne` :

```bash
docker ai "pourquoi mon conteneur lab-a1 s'arrête immédiatement ?"
```

Gordon propose des actions (par exemple `docker ps`, `docker logs`) et attend votre **approbation** avant d'exécuter des commandes. Pour **chaque** action proposée :

1. lisez la commande exacte
2. demandez-vous : lit-elle seulement des informations, ou modifie-t-elle quelque chose ?
3. n'approuvez que ce que vous comprenez

Comparez sa conclusion avec la vôtre (étape 3).

---

## Étape 5 — Appliquer et valider la correction

Corrigez le `Dockerfile` : la commande de démarrage doit viser `app.py` (et non `main.py`). Vous pouvez le faire à la main, ou demander à Gordon de proposer la modification : **relisez le changement** avant de l'accepter.

```bash
docker build -t lab-a1:ok .
docker rm -f lab-a1
docker run -d --name lab-a1 -p 8000:8000 lab-a1:ok
docker ps --filter name=lab-a1
```

Ouvrez **http://localhost:8000** ✅

---

## Étape 6 — Demander une amélioration du Dockerfile

```bash
docker ai "rate my Dockerfile and suggest improvements"
```

(Gordon répond aussi en français si vous le lui demandez.) Notez ses suggestions. Pour **chacune**, décidez si vous l'appliquez, puis **validez** avec vos outils des modules 03 et 04 :

```bash
docker buildx build --check .
docker build -t lab-a1:v2 .
docker images lab-a1
```

| Suggestion de Gordon | Je l'applique ? | Vérification |
|---|---|---|
| ........ | ........ | `docker buildx build --check`, build, test du conteneur |

---

## Étape 7 — Garde-fous : reconnaître une demande dangereuse

Posez à Gordon une demande de nettoyage large :

```bash
docker ai "clean up all unused Docker resources"
```

Gordon va proposer des commandes de nettoyage. **Ne les approuvez pas** : lisez-les, puis **refusez**.

**Questions :**
- Quelles ressources la commande proposée supprimerait-elle ? (conteneurs arrêtés, réseaux, images sans étiquette, cache de build, parfois des **volumes**)
- Pourquoi `prune` et `docker compose down -v` sont-ils particulièrement risqués avec des volumes (lab du module 05) ?
- Que feriez-vous avant d'approuver : lister d'abord (`docker ps -a`, `docker volume ls`, `docker system df`) ?

---

## Étape 8 — Apprendre avec Gordon (facultatif)

```bash
docker ai "Explain multi-stage builds"
```

Comparez avec le Dockerfile multi-stage du module 03 (`module-03/lab-fil-rouge/Dockerfile`).

Pour que Gordon travaille sur un autre dossier : `docker ai -C ~/autre-projet`.

---

## Étape 9 — Nettoyer

```bash
docker rm -f lab-a1
docker rmi lab-a1:panne lab-a1:ok lab-a1:v2
```

(Supprimez seulement les images qui existent ; une erreur sur une image absente est normale.) L'image de base `python:3.12` pèse environ 1 Go : `docker rmi python:3.12` si vous ne l'utilisez plus. Supprimez le dossier `projet-panne`.

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `docker ai` | Ouvrir l'interface interactive de Gordon |
| `docker ai "question"` | Poser une question depuis le terminal |
| `docker ai version` | Version de Gordon |
| `docker ai -C DOSSIER` | Travailler sur un autre dossier |

**À retenir :**
- Gordon **propose** ; **vous** approuvez, action par action
- vérifiez toujours ses recommandations (build, tests, `--check`) : une réponse plausible n'est pas une réponse correcte
- refusez les nettoyages larges (`prune`, `down -v`) tant que vous n'avez pas listé ce qui serait supprimé

---

➡️ **Suivant :** Lab A2 — Docker Model Runner
