# Module IA — Lab avancé S13 : CI et mode headless

> **Niveau :** Avancé | **Durée estimée :** 40 minutes
> **Prérequis :** Labs S1, S3 et S5 terminés ; `sbx` version **0.48.0 ou plus** ; un compte Docker avec la possibilité de créer un **jeton d'accès personnel** (PAT) ; le dossier `mon-projet` (dépôt Git propre) ; `jq` (facultatif, pour l'étape 6)
> **Accès à un modèle :** **non requis** (on utilise le shell, pas d'agent IA)

## 🎯 Objectifs

- Se connecter à `sbx` **sans navigateur**, avec un jeton d'accès personnel
- Exécuter une tâche dans un sandbox **sans terminal interactif** : créer → exécuter → récupérer → supprimer
- Lire les **codes de sortie** et éviter les confirmations qui bloquent un script
- Lire la sortie des commandes en **JSON**

> **Contexte :** en CI, aucun navigateur et aucun terminal interactif. Tout doit être explicite : jeton, noms, `--force`, codes de sortie. Cette page décrit les sandboxes **locaux** en CI ; pour du calcul cloud sans virtualisation locale, voir le lab S9 (`sbx --cloud run --detach`).

> **Note Windows / Mac :** les scripts sont fournis en Bash (`ci-job.sh`) et en PowerShell (`ci-job.ps1`).

---

## Étape 1 — Créer un jeton d'accès personnel (PAT)

Dans les paramètres de votre compte Docker (**Personal access tokens**), générez un jeton avec au moins la portée **Read**. Gardez-le pour la durée du lab.

> ⚠️ Un jeton est un **secret** : ne le collez jamais dans un fichier du dépôt, une capture d'écran ou un historique partagé. Révoquez-le à la fin du lab.

---

## Étape 2 — Se connecter sans navigateur

Remplacez `VOTRE_IDENTIFIANT` par votre identifiant Docker.

**Mac / Linux**

```bash
read -rs DOCKER_PAT
echo "$DOCKER_PAT" | sbx login --username VOTRE_IDENTIFIANT --password-stdin
```

(collez le jeton à l'invite, puis Entrée)

**Windows (PowerShell)**

```powershell
$env:DOCKER_PAT = Read-Host "Jeton" -MaskInput
$env:DOCKER_PAT | sbx login --username VOTRE_IDENTIFIANT --password-stdin
```

**Résultat attendu :** la connexion réussit sans ouvrir de navigateur.

> Dans un vrai pipeline, le jeton vient du **coffre à secrets** du fournisseur de CI (par exemple `${{ secrets.DOCKER_PAT }}` dans GitHub Actions), jamais du dépôt.

---

## Étape 3 — Une tâche CI complète

Le script crée un sandbox **en mode clone** (lab S3), y exécute une commande qui crée une branche et un commit, récupère le travail avec `git fetch` et supprime le sandbox. Il se lance **depuis le dépôt de test** :

**Mac / Linux**

```bash
cd ~/labs/mon-projet
git status
bash ~/chemin/vers/labs/module-ia/lab-sandbox-ci/scripts/ci-job.sh
```

**Windows (PowerShell)**

```powershell
cd C:\Labs\mon-projet
git status
C:\chemin\vers\labs\module-ia\lab-sandbox-ci\scripts\ci-job.ps1
```

(Adaptez le chemin vers votre copie du dépôt des labs.)

**Résultat attendu :**
- le sandbox est créé en arrière-plan
- la commande s'exécute et le code de sortie affiché est `0`
- `git log` montre le commit « Rapport CI » sur `sandbox-ci-task/ci/rapport`
- le sandbox est supprimé (`sbx ls` ne le montre plus)

Lisez ensuite le script : repérez les points qui le rendent **non interactif** (`--force`, noms explicites, pas de saisie).

> 💡 Dans la doc, un workflow typique utilise un agent à la place de la commande : `sbx exec ci-task -- claude … -p "Relis le code et valide tes modifications"`. Le principe est identique : **la tâche est une commande**.

---

## Étape 4 — Les codes de sortie

`sbx exec` renvoie le code de sortie de la commande qu'il exécute. Créez un sandbox jetable :

```bash
sbx create --name lab-s13-codes shell
```

Puis testez (lisez `$?` sous Bash ou `$LASTEXITCODE` sous PowerShell après chaque commande) :

```bash
sbx exec lab-s13-codes -- sh -c "exit 3"
sbx exec lab-s13-codes -- commande-inexistante
sbx exec sandbox-qui-n-existe-pas -- true
```

**Résultat attendu :**

| Commande | Code |
|---|---|
| Une commande qui retourne 3 | **3** |
| Un exécutable absent dans le sandbox local | **127** |
| Un sandbox inexistant (échec pour lancer la commande) | **125** |

**Question :** dans un pipeline, comment distinguer « ma tâche a échoué » (code propre à la tâche) de « le sandbox n'existe pas » (125) ?

---

## Étape 5 — Les confirmations bloquent les scripts

```bash
echo y | sbx rm lab-s13-codes
```

**Résultat attendu :** la commande **échoue** (code 1) : les confirmations exigent un vrai terminal, et envoyer `y` dans l'entrée standard ne les confirme pas. Dans un script, on utilise **`--force`** :

```bash
sbx rm --force lab-s13-codes
```

> 💡 Pour des nettoyages répétables, vérifiez d'abord que la ressource existe : `sbx mcp rm` échoue pour un serveur non enregistré, même avec `--force`, et `sbx secret rm` échoue si aucun secret ne correspond (testez avec `sbx mcp ls` / `sbx secret ls`).

---

## Étape 6 — Lire la sortie en JSON

Les tableaux lisibles peuvent changer d'une version à l'autre : en script, demandez une sortie structurée. Les résultats vont sur la sortie standard ; erreurs, avertissements et progression vont sur la sortie d'erreur.

```bash
sbx create --name lab-s13-json shell
sbx ls --json
```

**Mac / Linux (avec `jq`)**

```bash
sbx ls --json | jq -r '.[].name'
```

**Windows (PowerShell)**

```powershell
sbx ls --json | ConvertFrom-Json | ForEach-Object { $_.name }
```

**Résultat attendu :** la liste des noms de sandboxes. Depuis `sbx` 0.48.0, `sbx ls --json` renvoie **directement un tableau** (et non plus un objet `{sandboxes: [...]}`). Les champs sont en `snake_case`.

Autres options utiles :

```bash
sbx diagnose --format json
sbx policy ls -q
```

- `--json` est un alias de `--format json` ; `--format`, `--json` et `--quiet` (`-q`) sont **mutuellement exclusifs**
- pour `sbx diagnose`, identifiez un contrôle par son **`id`** (stable), pas par son `name` (texte d'affichage)

Nettoyez :

```bash
sbx rm --force lab-s13-json
```

---

## Étape 7 — Secrets en CI

Les clés d'agent (clé d'API de modèle, jeton GitHub) peuvent être préconfigurées comme **secrets globaux** pour tout sandbox créé par l'exécuteur. À **lire** (ne pas exécuter dans ce lab) :

```bash
sbx secret import --all
sbx secret set anthropic --force -t "${{ secrets.ANTHROPIC_API_KEY }}"
```

- `sbx secret import --all` importe d'un coup les variables d'environnement déjà définies dans l'environnement de CI
- `--force` écrase une entrée existante ; `-t` transmet la valeur depuis le coffre du fournisseur de CI

Lisez `scripts/ci-exemple.yml` : un exemple de workflow GitHub Actions (à adapter, volontairement non placé dans `.github/workflows`).

> ⚠️ Les exécuteurs de CI hébergés ne permettent pas toujours la virtualisation (Ubuntu 24.04+ avec KVM requis, virtualisation imbriquée dans une VM : diapo 145). Vérifiez votre exécuteur avant de planifier une tâche `sbx` locale ; sinon, utilisez le **cloud** (lab S9).

---

## Étape 8 — Migration des scripts vers la version 0.48.0

Si vous reprenez un ancien script, ces options ont changé :

| Commande | Ancienne option | Remplacement |
|---|---|---|
| `sbx run` | `--detached` | `--detach` ou `-d` |
| `sbx env create` / `env run` | `--auto-approve`, `-y` | `--force` ou `-f` |
| `sbx create` | `--quiet`, `-q` | `--no-progress` |
| `sbx template save` | `-d` (description) | `--description` |
| `sbx diagnose` | `--output`, `-o` | `--format table`, `json`, `yaml` ou `github-issue` |
| `sbx mcp add` | `--skip_auth` | `--skip-auth` |

---

## Étape 9 — Nettoyer

```bash
sbx ls
git branch -a
```

Supprimez les sandboxes restants (`sbx rm --force NOM`), la branche récupérée si vous n'en voulez plus (`git branch -D …`), et **révoquez le jeton** dans les paramètres Docker. Pour oublier la session : `sbx logout` (demande une confirmation ; en script : `sbx logout --yes`).

---

## Pour aller plus loin : exécutions planifiées (cloud)

Pour des tâches **récurrentes** sans garder votre poste allumé, la commande **`sbx --cloud schedule`** lance un sandbox cloud neuf selon une expression cron. Elle fait l'objet du lab **S13b**. Attention : une connexion par **PAT** (étape 2 de ce lab) n'enregistre **pas** l'identifiant de planification ; il faut une connexion **interactive** (`sbx login`).

---

## ✅ Récapitulatif

| Besoin | Outil |
|---|---|
| Connexion sans navigateur | `echo "$PAT" \| sbx login --username ID --password-stdin` |
| Sandbox en arrière-plan | `sbx create --name N --clone AGENT .` |
| Exécuter une tâche | `sbx exec N -- commande` (code de sortie = celui de la commande) |
| Récupérer le travail | `git fetch sandbox-N` |
| Nettoyer sans confirmation | `sbx rm --force N` |
| Sortie pour un script | `--json` / `--format json` |
| Secrets en CI | `sbx secret import --all` ou `sbx secret set … -t` |

**À retenir :** en CI, tout est explicite : identité (PAT), noms, `--force`, codes de sortie. Aucun secret dans le dépôt.

---

➡️ **Suivant :** Lab S13b — Exécutions planifiées (cloud)
