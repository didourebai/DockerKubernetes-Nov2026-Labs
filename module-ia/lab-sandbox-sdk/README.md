# Module IA — Lab avancé S12 : Piloter un sandbox par code (SDK TypeScript)

> **Niveau :** Avancé | **Durée estimée :** 45 minutes
> **Prérequis :** Lab S9 (Cloud Sandboxes), **Node.js 20 ou plus** et npm, un compte Docker avec un abonnement **Docker Agentic Platform** actif
> **Accès à un modèle :** **non requis** : ni agent IA, ni clé d'API de fournisseur de modèle
> ⚠️ **Coût :** le calcul cloud est **facturé** à votre abonnement (taille par défaut : *small*, 2 CPU et 4 Gio). Le programme supprime le sandbox à la fin ; **vérifiez-le** (étape 6). Ce lab peut être fait en **démonstration par le formateur**.

## 🎯 Objectifs

- Créer, utiliser et supprimer un Cloud Sandbox **depuis du code**, avec le SDK `@docker/sandboxes`
- Comprendre ce que fait chaque appel
- Vérifier le sandbox avec la CLI (`sbx --cloud ls`) pendant que le programme tourne
- Savoir quoi faire si le programme s'arrête avant la suppression

> **Idée :** la CLI `sbx` est faite pour vous ; le **SDK** (TypeScript/JavaScript) et l'**API REST** (n'importe quel langage) sont faits pour vos **applications et vos pipelines** : créer des sandboxes cloud, y exécuter des commandes, transférer des fichiers, gérer images, snapshots, volumes et secrets. Le SDK n'a pas besoin de la CLI Docker.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Créer le projet

```bash
mkdir sandboxes-sdk-lab
cd sandboxes-sdk-lab
npm init --yes
npm pkg set type=module
```

Installez le SDK et les outils TypeScript :

```bash
npm install @docker/sandboxes
npm install --save-dev tsx typescript @types/node
```

**Résultat attendu :** un dossier `node_modules` et un `package.json` contenant `"type": "module"`.

---

## Étape 2 — Récupérer le programme

Copiez `index.ts` (et `index-pause.ts`) dans le projet. Depuis le dossier `sandboxes-sdk-lab`, en adaptant le chemin vers votre copie du dépôt des labs :

**Windows (PowerShell)**

```powershell
Copy-Item C:\chemin\vers\labs\module-ia\lab-sandbox-sdk\projet-sdk\*.ts .
```

**Mac / Linux**

```bash
cp ~/chemin/vers/labs/module-ia/lab-sandbox-sdk/projet-sdk/*.ts .
```

Lisez `index.ts` : une vingtaine de lignes.

---

## Étape 3 — Comprendre le programme

| Ligne de code | Rôle |
|---|---|
| `new Sandboxes({ auth: oauth({ onVerification … }) })` | Crée le client ; l'authentification est interactive : le SDK affiche une adresse et un code à saisir dans le navigateur |
| `client.kits.launchAndWait('shell')` | Crée un sandbox à partir du **kit** `shell` et **attend** qu'il soit en cours d'exécution |
| `sandbox.processes.run({ args: [...] }, { timeoutMs })` | Exécute une commande dans le sandbox et collecte sa sortie |
| `sandbox.refresh()` | Relit l'état le plus récent du sandbox |
| `latest.delete({ force: true })` puis `waitUntilDeleted()` | Supprime (même s'il tourne) et attend la fin |
| `client.close()` (dans `finally`) | Libère les ressources locales. **Ne supprime pas** le sandbox |

> **Kit :** il fournit l'image et la configuration du sandbox pour un agent ou un outil. Le kit `shell` fournit un simple environnement shell : pas besoin d'agent IA.

**Question :** pourquoi le `client.close()` est-il dans un bloc `finally` ?

---

## Étape 4 — Exécuter

```bash
npx tsx index.ts
```

Le programme affiche une adresse et un code de vérification. Ouvrez l'adresse, connectez-vous avec le compte Docker qui a l'abonnement cloud. Le programme continue ensuite.

**Résultat attendu :**
1. `Sandbox : NOM_DU_SANDBOX`
2. `Bonjour depuis Docker Sandboxes`
3. `Supprimé : NOM_DU_SANDBOX`

---

## Étape 5 — Le voir avec la CLI

Lancez la variante qui laisse le sandbox vivant 60 secondes :

```bash
npx tsx index-pause.ts
```

Pendant la pause, dans **un second terminal** :

```bash
sbx --cloud ls
sbx --cloud inspect NOM_DU_SANDBOX
```

**Résultat attendu :** le sandbox créé par le code apparaît dans la liste cloud, avec ses ressources (2 CPU / 4 Gio par défaut). Après la pause, le programme le supprime ; `sbx --cloud ls` ne le montre plus.

**Question :** la CLI et le SDK parlent-ils au même service ?

---

## Étape 6 — Si le programme s'arrête avant la suppression

Si le programme s'interrompt après avoir affiché le nom du sandbox (erreur, `Ctrl+C`), **le sandbox existe encore et reste facturé**. La fermeture du client ne le supprime pas.

Vérifiez et nettoyez avec la CLI :

```bash
sbx --cloud ls
sbx --cloud rm NOM_DU_SANDBOX
sbx --cloud ls
```

(Dans le code, on le retrouverait avec `client.get(nom)` pour le supprimer.)

**Exercice :** provoquez l'arrêt avec `Ctrl+C` pendant la pause de `index-pause.ts`, puis nettoyez à la main.

---

## Étape 7 — Variantes

1. Dans `index.ts`, remplacez la commande par `['uname', '-a']`. Relancez.
2. Changez le message de l'`echo`. Relancez.
3. Notez le temps total d'exécution : combien de temps prend la création du sandbox ?

---

## Étape 8 — Pour aller plus loin (à lire)

- **Authentification d'un automate (CI) :** le SDK accepte un **jeton d'accès personnel** (PAT) à la place de la connexion interactive : voir la page *Authentication and authorization* de la doc.
- **Attendre la configuration d'un kit :** si vous utilisez un kit qui clone un dépôt ou installe des outils, attendez la fin de cette configuration avant d'utiliser ses résultats (page *API concepts*).
- **Recettes :** le *Cookbook* du SDK (processus, fichiers, stockage, réseau).
- **Erreurs et nouvelles tentatives :** lisez *Errors and retries* avant d'ajouter une logique de reprise.
- **Quotas et limites :** quotas de compte et limites de débit (page *Compute sizes and limits*).

| | CLI `sbx --cloud` | SDK TypeScript | API REST |
|---|---|---|---|
| Usage typique | Vous, au terminal | Application JS / TS | Tout langage ou outil HTTP |
| Authentification | `sbx login` | Navigateur ou PAT | Mêmes comptes et abonnement |
| Dépend de la CLI Docker | Oui | **Non** | Non |

---

## Étape 9 — Nettoyer

```bash
sbx --cloud ls
```

La liste doit être **vide** (aucun sandbox du lab). Supprimez ensuite le dossier du projet :

**Windows (PowerShell)**

```powershell
cd ..
Remove-Item -Recurse -Force sandboxes-sdk-lab
```

**Mac / Linux**

```bash
cd ..
rm -rf sandboxes-sdk-lab
```

---

## ✅ Récapitulatif

| Élément | Rôle |
|---|---|
| `npm install @docker/sandboxes` | Installer le SDK (Node.js 20+) |
| `oauth({ onVerification })` | Connexion interactive |
| `client.kits.launchAndWait('shell')` | Créer un sandbox et attendre qu'il tourne |
| `sandbox.processes.run(...)` | Exécuter une commande |
| `sandbox.refresh()` / `.delete({ force: true })` | Relire l'état / supprimer |
| `client.close()` | Libérer le client (ne supprime pas le sandbox) |

**À retenir :** piloter un sandbox par code revient à écrire le cycle **créer → utiliser → supprimer** avec un `finally` ou une vérification de nettoyage : un sandbox cloud oublié est un sandbox facturé.

---

➡️ **Suivant :** Lab S13 — CI, mode headless et exécutions planifiées
