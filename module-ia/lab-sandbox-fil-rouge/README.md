# Module IA — Lab fil rouge S7 : l'agent améliore l'IT-Support Portal

> **Niveau :** Intermédiaire | **Durée estimée :** 60 minutes
> **Prérequis :** Labs S1 à S3, modules 02 à 05 (Dockerfile, multi-stage, Build Checks), Docker Desktop, accès à Claude Code
> **Fil rouge :** on reprend le portail **v1.0** du module 02 et on demande à un agent de le porter au niveau de la **v2.0** du module 03, **dans un sandbox**. Puis on **valide son travail**.

## 🎯 Objectifs

- Confier une tâche réelle à un agent dans un sandbox en mode **clone**
- Récupérer son travail par une branche Git (`git fetch`)
- **Valider** le résultat avec les outils des modules précédents : `docker buildx build --check`, build, test du conteneur, comparaison avec la correction du module 03

> **Règle (diapo 140) :** on conteneurise l'application, on met l'agent en sandbox. L'agent construit ses images avec **son propre** moteur Docker ; c'est vous qui validez avec le vôtre.

> ⚠️ Projet de formation uniquement : aucune donnée sensible.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Préparer le projet

Copiez le portail v1.0 hors du dépôt des labs et faites-en un dépôt Git. Depuis la racine du dépôt :

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse module-02\lab-fil-rouge C:\Labs\it-portal-agent
cd C:\Labs\it-portal-agent
```

**Mac / Linux**

```bash
cp -r module-02/lab-fil-rouge ~/labs/it-portal-agent
cd ~/labs/it-portal-agent
```

```bash
git init
git add .
git commit -m "IT-Support Portal v1.0"
```

Lisez le `Dockerfile` : une seule étape, pas d'utilisateur non-root, pas de `HEALTHCHECK`, `COPY . .` sans `.dockerignore`.

Mesurez l'état de départ :

```bash
docker buildx build --check .
docker build -t it-portal:avant .
docker images it-portal:avant
```

Notez les avertissements éventuels et la taille de l'image.

---

## Étape 2 — Lancer l'agent en mode clone

```bash
sbx run --clone --name lab-s7 claude .
```

Donnez-lui cette consigne :

```text
Crée une branche feat/dockerfile-v2. Améliore le Dockerfile de ce portail Flask :
1. build multi-stage (étape builder pour les dépendances, image finale légère),
2. utilisateur non-root,
3. HEALTHCHECK sur la route /health,
4. un fichier .dockerignore adapté,
5. serveur gunicorn au lieu du serveur de développement Flask (ajoute gunicorn à requirements.txt).
Construis l'image, lance un conteneur, vérifie que /health répond, puis fais un commit.
Ne modifie pas app.py ni les fichiers dans templates/ et static/.
```

Laissez-le travailler. Il peut exécuter `docker build` et `docker run` : c'est son moteur privé. **Ne quittez pas le sandbox** avant l'étape 3.

---

## Étape 3 — Récupérer le travail

Dans une **seconde fenêtre** sur l'hôte, dans `it-portal-agent` :

```bash
git status
```

**Résultat attendu :** `working tree clean` : l'agent n'a rien changé sur votre disque (mode clone).

```bash
git fetch sandbox-lab-s7
git log --oneline sandbox-lab-s7/feat/dockerfile-v2
git diff --stat HEAD..sandbox-lab-s7/feat/dockerfile-v2
```

**Question :** quels fichiers ont changé ? Y a-t-il des fichiers que vous n'aviez pas demandés ou une modification de `app.py` malgré la consigne ?

---

## Étape 4 — Valider, ne pas faire confiance

Lisez le diff complet :

```bash
git diff HEAD..sandbox-lab-s7/feat/dockerfile-v2
```

Puis extrayez la branche et testez avec **votre** moteur Docker :

```bash
git checkout -b feat/dockerfile-v2 sandbox-lab-s7/feat/dockerfile-v2
docker buildx build --check .
docker build -t it-portal:agent .
docker run --rm -d -p 5000:5000 --name it-portal-agent it-portal:agent
```

Ouvrez **http://localhost:5000** et **http://localhost:5000/health** ✅

```bash
docker ps
docker inspect --format "{{.State.Health.Status}}" it-portal-agent
docker exec it-portal-agent whoami
docker images it-portal:agent
```

Complétez la grille de validation :

| Critère | Attendu | Résultat |
|---|---|---|
| `docker buildx build --check` | Aucun avertissement | ........ |
| Build multi-stage | Au moins deux `FROM` | ........ |
| Utilisateur non-root | `whoami` ≠ `root` | ........ |
| Healthcheck | État `healthy` après quelques secondes | ........ |
| `.dockerignore` | Présent, exclut `.git`, `__pycache__`… | ........ |
| `app.py`, `templates/`, `static/` | Inchangés | ........ |
| Taille de l'image | Inférieure à `it-portal:avant` | ........ |

Nettoyez :

```bash
docker rm -f it-portal-agent
```

---

## Étape 5 — Comparer avec la correction du module 03

Comparez le Dockerfile de l'agent avec celui du module 03 :

**Windows (PowerShell)**

```powershell
git diff --no-index C:\chemin\vers\labs\module-03\lab-fil-rouge\Dockerfile Dockerfile
```

**Mac / Linux**

```bash
git diff --no-index ~/labs-depot/module-03/lab-fil-rouge/Dockerfile Dockerfile
```

(Adaptez le chemin vers votre copie du dépôt des labs.)

**Questions :**
- Quelles différences sont des **choix équivalents** ? Lesquelles sont des **oublis** ou des **erreurs** ?
- Y a-t-il une amélioration que l'agent a proposée et que la correction n'a pas ?
- Si vous aviez accepté le travail sans relecture, qu'est-ce qui aurait pu mal tourner ?

---

## Étape 6 — Pousser la branche, puis nettoyer

Si vous acceptez le résultat, la branche `feat/dockerfile-v2` est déjà dans votre dépôt local (étape 4). Avant de supprimer le sandbox, assurez-vous d'avoir tout récupéré :

```bash
git log --oneline -3
sbx rm lab-s7
sbx ls
```

`sbx rm` supprime aussi le remote `sandbox-lab-s7` de votre dépôt. La branche récupérée reste.

```bash
docker rmi it-portal:avant it-portal:agent
```

---

## ✅ Récapitulatif

| Étape | Outil |
|---|---|
| Donner la tâche en isolation | `sbx run --clone --name NOM claude .` |
| Récupérer le travail | `git fetch sandbox-NOM` |
| Relire | `git diff HEAD..sandbox-NOM/branche` |
| Valider | `docker buildx build --check`, `docker build`, `docker run`, `docker inspect` |
| Nettoyer | `sbx rm NOM` |

**À retenir :** l'agent accélère le travail, mais **vous** restez responsable du résultat. Les modules 03 et 04 vous donnent les critères de validation.

---

➡️ **Suivant :** Lab S8 — Deux agents, un même dépôt
