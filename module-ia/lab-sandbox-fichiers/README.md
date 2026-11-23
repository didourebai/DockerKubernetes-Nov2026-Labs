# Module IA — Lab basique S3 : Ce que l'agent peut atteindre (fichiers)

> **Niveau :** Débutant | **Durée estimée :** 30 minutes
> **Prérequis :** Labs S1 et S2 terminés, dossier `mon-projet` (dépôt Git propre)
> **Accès à un modèle :** **non requis** : on joue le rôle de l'agent avec un shell

## 🎯 Objectifs

Comparer les trois façons de donner des fichiers à un agent (diapo 142) :

| Mode | Ce que voit l'agent | Risque |
|---|---|---|
| **Sans accès** | Aucun dossier de l'hôte | Aucun pour vos fichiers |
| **Montage direct** | Votre dossier, en lecture-écriture | Aucune barrière entre l'agent et vos fichiers |
| **Clone** (`--clone`) | Une copie privée du dépôt Git dans la VM | Vos fichiers ne changent que si vous récupérez le travail |

> Dans ce lab, c'est **vous** qui faites ce qu'un agent pourrait faire (modifier, supprimer). Un agent, lui, agit sans que vous tapiez les commandes : d'où l'importance de choisir le bon mode avant de le lancer.

> **Note Windows / Mac :** une commande par ligne. Quand ce n'est pas possible, deux blocs : **Windows (PowerShell)** et **Mac / Linux**.

---

## Étape 1 — Préparer le projet

Ajoutez un fichier factice à `mon-projet`. Depuis la racine du dépôt des labs :

**Windows (PowerShell)**

```powershell
Copy-Item module-ia\lab-sandbox-fichiers\fichiers-a-copier\donnees-factices.txt C:\Labs\mon-projet\
cd C:\Labs\mon-projet
```

**Mac / Linux**

```bash
cp module-ia/lab-sandbox-fichiers/fichiers-a-copier/donnees-factices.txt ~/labs/mon-projet/
cd ~/labs/mon-projet
```

```bash
git add donnees-factices.txt
git commit -m "Ajout du fichier factice"
git status
```

**Résultat attendu :** `nothing to commit, working tree clean`.

---

## Étape 2 — Mode « sans accès aux fichiers de l'hôte »

Sans chemin de dossier, `sbx create` fabrique un sandbox **sans montage** (« mountless »). On l'attache ensuite par son nom :

```bash
sbx create --name lab-s3-vide shell
sbx run --name lab-s3-vide
```

Dans le sandbox :

```bash
pwd
ls -la
find / -name "donnees-factices.txt" 2>/dev/null
touch fichier-du-sandbox.txt
exit
```

**Résultat attendu :** le dossier de travail est `/home/agent/workspace` (propre au sandbox), le fichier factice est **introuvable**. Le fichier créé persiste dans le sandbox à travers les arrêts, mais disparaît à sa suppression.

> 💡 Pour échanger des fichiers avec un tel sandbox, on utilise `sbx cp` (étape 4). Les noms de sandbox doivent être **distincts** : relancer `sbx run` sur le même dossier se reconnecte au sandbox existant au lieu d'en créer un autre.

---

## Étape 3 — Mode « montage direct »

Retournez dans le projet :

**Windows (PowerShell)**

```powershell
cd C:\Labs\mon-projet
```

**Mac / Linux**

```bash
cd ~/labs/mon-projet
```

```bash
sbx run --name lab-s3-direct shell .
```

Dans le sandbox, jouez l'agent « maladroit » :

```bash
cat donnees-factices.txt
echo "MODIFIE PAR L'AGENT" >> donnees-factices.txt
rm .gitignore
ls -la
exit
```

Sur l'**hôte** :

```bash
git status
git diff
```

**Résultat attendu :** `donnees-factices.txt` est **modifié** et `.gitignore` est **supprimé**, sur votre disque, immédiatement. L'agent a pu **lire** le fichier « secret ».

Annulez les dégâts grâce à Git :

```bash
git restore .
git status
```

> 💡 Git est votre filet de sécurité : travaillez toujours dans un dépôt propre, avec les changements précédents commités.

---

## Étape 4 — Mode « clone »

```bash
sbx run --clone --name lab-s3-clone shell .
```

Dans le sandbox, créez une branche (le clone suit la branche extraite sur l'hôte : aucune branche n'est créée automatiquement), refaites les mêmes actions, puis versionnez-les dans la copie privée :

```bash
git switch -c feat/agent-essai
pwd
cat donnees-factices.txt
echo "MODIFIE PAR L'AGENT" >> donnees-factices.txt
rm .gitignore
git status
git commit -am "Travail de l'agent"
```

Votre dépôt d'origine est aussi visible **en lecture seule** :

```bash
ls /run/sandbox/source
touch /run/sandbox/source/test.txt
```

**Résultat attendu :** la lecture fonctionne, l'écriture est **refusée**.

> ⚠️ **Ne quittez pas le sandbox** : le récupérer demande qu'il soit en cours d'exécution (voir ci-dessous).

Sur l'**hôte**, dans une **seconde fenêtre** :

```bash
git status
git diff
```

**Résultat attendu :** `working tree clean` : **rien n'a changé** sur votre disque. Le travail de l'agent reste dans la copie privée tant que vous ne le récupérez pas.

### Récupérer le travail : `git fetch`

Votre dépôt hôte reçoit automatiquement un dépôt distant nommé `sandbox-NOM` (ici `sandbox-lab-s3-clone`). Les commits sont transférés par l'intermédiaire du démon, accessible à votre seul utilisateur :

```bash
git remote -v
git fetch sandbox-lab-s3-clone
git log --oneline sandbox-lab-s3-clone/feat/agent-essai
git diff HEAD..sandbox-lab-s3-clone/feat/agent-essai
```

**Observez :** vous relisez le travail de l'agent **avant** de l'accepter. Pour l'examiner dans votre dépôt :

```bash
git checkout -b feat/agent-essai sandbox-lab-s3-clone/feat/agent-essai
git status
git checkout -
```

Vous choisissez ce qui entre, et quand.

> 📖 Le remote est indisponible quand le sandbox est arrêté (`sbx stop`) : relancez-le avec `sbx run --name lab-s3-clone`, la configuration du remote est alors rafraîchie. `sbx rm` supprime le sandbox **et** son remote : **récupérez ce qui vous intéresse avant de supprimer**.

> 💡 Pour un fichier non commité, `sbx cp lab-s3-clone:/CHEMIN/ABSOLU/fichier ./` fonctionne aussi (chemin absolu côté sandbox).

Quittez maintenant le sandbox (`exit`).

---

## Étape 5 — Synthèse

Complétez avec vos observations :

| | Sans accès | Montage direct | Clone |
|---|---|---|---|
| L'agent peut lire `donnees-factices.txt` | ........ | ........ | ........ |
| Ses modifications apparaissent sur l'hôte | ........ | ........ | ........ |
| Une suppression par l'agent est irréversible sans Git | ........ | ........ | ........ |
| Récupérer son travail | — | Déjà là (`git diff`) | Explicite |
| Cas d'usage | Tâche autonome | Travail courant, dépôt propre | Plusieurs agents, essais risqués |

**Question :** dans le mode clone, l'agent peut-il quand même lire le « secret » ? (Oui : il est dans le dépôt copié. Ne versionnez pas de secrets.)

---

## Étape 6 — Nettoyer

```bash
sbx ls
sbx rm lab-s3-vide lab-s3-direct lab-s3-clone
sbx ls
```

`sbx rm` demande une confirmation pour chaque sandbox (`--force` pour l'ignorer). Supprimez aussi la branche locale `feat/agent-essai` (`git branch -D feat/agent-essai`) si vous l'avez créée.

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx run --name NOM AGENT .` | Montage direct du dossier courant |
| `sbx run --clone --name NOM AGENT .` | Copie privée du dépôt Git (dépôt requis) |
| `sbx create --name NOM AGENT` + `sbx run --name NOM` | Sandbox sans montage |
| `git fetch sandbox-NOM` | Récupérer les commits d'un sandbox en mode clone |
| `sbx cp NOM:/chemin/absolu hôte` | Copier un fichier entre sandbox et hôte |
| `git diff` / `git restore .` | Relire / annuler les changements |

**À retenir :** les fichiers partagés restent exposés aux actions de l'agent. Choisissez le mode **avant** de lancer l'agent.

---

➡️ **Suivant :** Lab S4 — Politiques réseau
