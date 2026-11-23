# Module IA — Lab basique S1 : Premier Docker Sandbox

> **Niveau :** Débutant | **Durée estimée :** 30 minutes
> **Prérequis :** Git, un compte Docker, un accès à Claude Code (abonnement Max / Team / Enterprise **ou** clé API Anthropic)

## 🎯 Objectifs

- Installer et vérifier la CLI `sbx`, puis se connecter
- Lancer un agent de codage (Claude Code) dans un sandbox
- Observer ce que l'agent a modifié, et le relire avec `git diff`
- Arrêter puis supprimer le sandbox

> ⚠️ **Sécurité :** n'exécutez ce lab que sur le petit projet de test fourni. Jamais sur des données sensibles.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.
> Quand ce n'est pas possible, deux blocs sont fournis : **Windows (PowerShell)** et **Mac / Linux**.

> **À savoir :** Docker Desktop n'est **pas** requis pour `sbx`. Le premier lancement est plus long
> (téléchargement de l'image de l'agent) ; les suivants démarrent en quelques secondes.

---

## Prérequis matériels

| Système | Exigence |
|---|---|
| macOS | 14 ou plus, Apple silicon |
| Windows | 11 avec *Windows Hypervisor Platform* activée |
| Linux | Ubuntu 24.04 ou plus, avec KVM |

En machine virtuelle, la virtualisation imbriquée est nécessaire.

---

## Étape 1 — Installer et vérifier `sbx`

**Windows (PowerShell)**

```powershell
winget install -h Docker.sbx
```

**Mac**

```bash
brew install docker/tap/sbx
```

Rouvrez le terminal, puis :

```bash
sbx --version
```

**Résultat attendu :** un numéro de version s'affiche.

---

## Étape 2 — Se connecter

```bash
sbx login
```

Suivez la connexion dans le navigateur avec votre compte Docker.

---

## Étape 3 — Initialiser la politique réseau

La politique réseau décide où l'agent a le droit de se connecter. On choisit le préréglage **Balanced** (services de développement courants autorisés).

```bash
sbx policy init balanced
sbx policy ls
```

**Résultat attendu :** la liste des règles réseau actives.

> 💡 Si vous sautez cette étape, `sbx run` vous la proposera au premier lancement en terminal interactif : choisissez **Balanced**.

---

## Étape 4 — Préparer le projet de test

On copie le projet fourni en dehors du dépôt des labs et on en fait un dépôt Git. Depuis la racine du dépôt des labs :

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse module-ia\lab-sandbox-premier\projet-test C:\Labs\mon-projet
cd C:\Labs\mon-projet
```

**Mac / Linux**

```bash
mkdir -p ~/labs && cp -r module-ia/lab-sandbox-premier/projet-test ~/labs/mon-projet
cd ~/labs/mon-projet
```

```bash
git init
git add .
git commit -m "Projet de test initial"
git status
```

**Résultat attendu :** `nothing to commit, working tree clean`.

> Si Git demande votre identité : `git config user.name "Votre Nom"` et `git config user.email "vous@exemple.com"`, puis refaites le `commit`.

Jetez un œil au `Dockerfile` : il fonctionne, mais il est volontairement perfectible (image lourde, pas de cache, utilisateur root).

---

## Étape 5 — Lancer un agent dans un sandbox

Depuis `mon-projet` :

```bash
sbx run --name lab-s1 claude
```

Le sandbox est créé, le dossier courant y est monté en **lecture-écriture**, et Claude Code démarre dedans.

> 💡 Le dossier courant est monté parce qu'aucun chemin n'est donné. `sbx run claude .` (écriture de la présentation) et `sbx run claude` sont équivalents. Pour donner une consigne dès le départ : `sbx run claude -- "explique ce projet"` (tout ce qui suit `--` est transmis à l'agent).

> Si Claude Code demande une connexion et que vous avez un abonnement, tapez `/login` dans le sandbox (le jeton reste sur votre poste). Avec une clé API, voir le lab S5 (secrets).

Donnez cette consigne à l'agent :

```text
Améliore le Dockerfile de ce projet : image plus légère, meilleur usage du cache, utilisateur non-root. Puis construis l'image et vérifie que l'application démarre.
```

Laissez-le travailler (il peut lancer `docker build` : il dispose de son **propre** moteur Docker dans la microVM).

---

## Étape 6 — Observer depuis l'extérieur

Pendant que l'agent travaille, ouvrez **une seconde fenêtre de terminal** :

```bash
sbx ls
docker ps
```

**Résultat attendu :**
- `sbx ls` affiche le sandbox `lab-s1` (colonnes SANDBOX, AGENT, STATUS, PORTS, WORKSPACE, CREATED)
- `docker ps` ne montre **pas** les conteneurs lancés par l'agent : ils tournent dans le moteur privé du sandbox

**Question :** pourquoi l'agent peut-il faire `docker build` sans toucher au démon de votre poste ?

Quittez l'agent quand il a terminé (`/exit` ou `Ctrl+C` selon l'interface).

---

## Étape 7 — Examiner les modifications

Le dossier étant partagé, les changements sont **déjà sur votre poste**. Relisez-les avant de les accepter :

```bash
git status
git diff
```

Vérifiez :
- quels fichiers ont changé ?
- le `Dockerfile` est-il réellement meilleur ? (base plus légère, `requirements.txt` copié avant le code, `USER` non-root)
- y a-t-il des fichiers que vous n'aviez pas demandés ?

Validez le résultat vous-même :

```bash
docker build -t lab-s1:test .
docker run --rm -d -p 5000:5000 --name lab-s1-test lab-s1:test
```

Ouvrez **http://localhost:5000** ✅, puis :

```bash
docker rm -f lab-s1-test
```

> 💡 Ne faites jamais confiance aveuglément au résultat d'un agent : relisez, construisez, testez.

---

## Étape 8 — Arrêter, reprendre, puis supprimer

```bash
sbx stop lab-s1
sbx ls
```

`stop` conserve les paquets, images et configuration du sandbox pour une réutilisation. Un sandbox **persiste** : on peut le reprendre depuis n'importe quel dossier avec son nom.

```bash
sbx run --name lab-s1
```

(Relancer `sbx run claude` dans le même dossier se reconnecte aussi au même sandbox au lieu d'en créer un autre.) Quittez l'agent, puis supprimez :

```bash
sbx rm lab-s1
sbx ls
```

`rm` demande une confirmation (`--force` pour l'ignorer) et supprime tout le contenu du sandbox. Les fichiers de votre dossier de travail **ne sont pas touchés** : le `git diff` de l'étape 7 reste valable.

> 💡 Pour une session jetable : `sbx run --rm claude` supprime le sandbox dès que l'agent se termine.

---

## Variante — Mode clone

Avec `--clone`, l'agent travaille sur une **copie privée** du dépôt dans la VM : vos fichiers ne changent pas tant que vous ne récupérez pas explicitement les modifications. (Dépôt Git requis.) Annulez d'abord les changements de l'étape 7 si vous voulez repartir de zéro : `git restore .`

```bash
sbx run --clone --name lab-s1-clone claude
```

Le clone suit la branche actuellement extraite sur l'hôte (aucune branche n'est créée automatiquement). Récupérez les changements utiles **avant** de supprimer le sandbox (voir le lab S3), puis :

```bash
sbx rm lab-s1-clone
```

Ce mode est approfondi dans le lab S3.

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx --version` | Vérifier l'installation |
| `sbx login` | Se connecter à Docker |
| `sbx policy init balanced` | Initialiser la politique réseau |
| `sbx policy ls` | Voir les règles réseau |
| `sbx run --name NOM claude` | Créer le sandbox et lancer l'agent |
| `sbx ls` | Lister les sandboxes |
| `sbx stop NOM` | Arrêter (conserve l'état) |
| `sbx rm NOM` | Supprimer le sandbox |
| `sbx` | Ouvrir le tableau de bord interactif |

**À retenir :** on conteneurise l'application, on met l'agent en sandbox. La microVM isole l'agent, mais les fichiers explicitement partagés restent accessibles à ses actions.

---

➡️ **Suivant :** Lab S2 — Prouver l'isolation
