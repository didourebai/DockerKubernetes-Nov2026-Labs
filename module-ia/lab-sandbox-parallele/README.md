# Module IA — Lab complémentaire S8 : Deux agents, un même dépôt

> **Niveau :** Intermédiaire | **Durée estimée :** 45 minutes
> **Prérequis :** Labs S3 et S7, accès à Claude Code
> **Projet :** le portail **v2.0** (module 03, `lab-fil-rouge`)

## 🎯 Objectifs

- Faire travailler **deux tâches en parallèle** sur le même dépôt sans qu'elles se marchent dessus
- Comprendre pourquoi **une branche seule n'isole pas** deux agents dans un même dossier de travail
- Récupérer, relire puis fusionner deux branches venues de sandboxes

> **Principe (doc Docker, *Git workflows*) :** en mode clone, le sandbox contient une copie du dépôt. Pour des tâches simultanées, on demande à l'agent de créer **un worktree par tâche** ; si les tâches ont besoin d'**environnements** indépendants, on utilise des sandboxes distincts, avec des noms distincts.

> ⚠️ Projet de formation uniquement : aucune donnée sensible.

---

## Étape 1 — Préparer le dépôt

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse module-03\lab-fil-rouge C:\Labs\it-portal-parallele
cd C:\Labs\it-portal-parallele
```

**Mac / Linux**

```bash
cp -r module-03/lab-fil-rouge ~/labs/it-portal-parallele
cd ~/labs/it-portal-parallele
```

```bash
git init
git add .
git commit -m "IT-Support Portal v2.0"
git branch
```

Notez le nom de votre branche principale (`main` ou `master`).

Deux tâches indépendantes :

| Tâche | Branche | Fichiers principaux |
|---|---|---|
| **A — Tests** | `feat/tests` | `tests/test_app.py`, `requirements-dev.txt` |
| **B — Version** | `feat/version` | `app.py` (nouvelle route `/api/version`) |

---

## Partie 1 — Un seul sandbox, un worktree par tâche

### Étape 2 — Lancer le sandbox

```bash
sbx run --clone --name lab-s8 claude .
```

Donnez cette consigne :

```text
Pour chaque tâche simultanée, crée un worktree Git séparé avec sa propre branche et fais tous les changements de cette tâche dans ce worktree.

Tâche A (branche feat/tests) : ajoute tests/test_app.py avec pytest, qui teste les routes /health et /api/status. Ajoute pytest dans requirements-dev.txt.

Tâche B (branche feat/version) : ajoute une route /api/version dans app.py qui renvoie {"version": ...} à partir de la variable d'environnement APP_VERSION.

Fais un commit par tâche. Ne touche pas à la branche principale.
```

Laissez-le travailler. **Ne quittez pas le sandbox.**

### Étape 3 — Récupérer les deux branches

Dans une **seconde fenêtre** sur l'hôte :

```bash
git status
git fetch sandbox-lab-s8
git branch -r
git log --oneline sandbox-lab-s8/feat/tests
git log --oneline sandbox-lab-s8/feat/version
```

**Résultat attendu :** deux branches distinctes, chacune avec ses commits, et un dépôt hôte resté propre.

```bash
git diff --stat HEAD..sandbox-lab-s8/feat/tests
git diff --stat HEAD..sandbox-lab-s8/feat/version
```

**Question :** chaque branche ne touche-t-elle que les fichiers de sa tâche ?

### Étape 4 — Fusionner

```bash
git merge sandbox-lab-s8/feat/tests
git merge sandbox-lab-s8/feat/version
git log --oneline --graph -8
```

En cas de conflit, ouvrez les fichiers, résolvez-les, puis `git add` et `git commit`.

Testez le résultat avec votre moteur Docker :

```bash
docker build -t it-portal:s8 .
docker run --rm -d -p 5000:5000 --name it-portal-s8 it-portal:s8
```

Ouvrez **http://localhost:5000/api/version** ✅

```bash
docker rm -f it-portal-s8
```

---

## Partie 2 — Deux sandboxes, deux environnements

Quand deux tâches ont besoin d'**environnements indépendants** (dépendances ou services différents), on lance deux sandboxes sur le même dépôt, avec des noms distincts.

```bash
sbx rm lab-s8
sbx run --clone --name lab-s8-a claude .
```

Dans une seconde fenêtre :

```bash
sbx run --clone --name lab-s8-b claude .
```

Donnez à chaque agent **une** tâche (A à l'un, B à l'autre), en commençant par « Crée une branche feat/… ».

Récupérez ensuite chaque branche :

```bash
git fetch sandbox-lab-s8-a
git fetch sandbox-lab-s8-b
git remote -v
```

**Observez :** chaque sandbox a son propre remote `sandbox-NOM`. `sbx rm NOM` supprime aussi le remote correspondant.

| | Un sandbox + worktrees | Deux sandboxes |
|---|---|---|
| Outils et services | Partagés | Indépendants |
| Mémoire / disque | Un seul environnement | Un environnement par tâche |
| Isolation des fichiers | Un worktree par tâche | Un clone par sandbox |
| Cas d'usage | Tâches légères et proches | Tâches aux dépendances différentes |

---

## Étape 5 — Nettoyer

```bash
sbx rm lab-s8-a lab-s8-b
sbx ls
docker rmi it-portal:s8
git remote -v
```

Supprimez les branches locales inutiles (`git branch -D …`) et les dossiers de travail.

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx run --clone --name NOM claude .` | Sandbox en mode clone |
| `git fetch sandbox-NOM` | Récupérer les branches du sandbox |
| `git log` / `git diff` | Relire |
| `git merge` | Fusionner |
| `sbx rm NOM` | Supprimer le sandbox (et son remote) |

**À retenir :**
- une branche seule n'isole pas deux tâches dans un même dossier de travail : il faut un worktree par tâche, ou un sandbox par tâche
- vous relisez et fusionnez : l'agent propose, vous décidez

---

➡️ **Suivant :** Lab S9 — Cloud Sandboxes (optionnel, facturé)
