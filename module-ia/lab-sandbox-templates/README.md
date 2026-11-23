# Module IA — Lab avancé S10 : Templates (et aperçu des Kits et skills)

> **Niveau :** Intermédiaire | **Durée estimée :** 40 minutes
> **Prérequis :** Labs S1 à S3 terminés
> **Accès à un modèle :** **non requis** (shell dans le sandbox)

## 🎯 Objectifs

- Figer l'état d'un sandbox (outils, fichiers) dans un **template** réutilisable
- Créer un nouveau sandbox à partir de ce template
- Exporter et importer un template pour le partager avec la classe
- Comprendre ce qu'un template **contient** (et surtout ce qu'il ne devrait jamais contenir)

> **Idée (diapo 144) :** les Kits sont des configurations réutilisables (outils, paramètres, autorisations). Un **template** est plus simple : une **image** du système de fichiers d'un sandbox. Le template apporte le contenu ; l'agent fournit toujours ses réglages d'exécution, comme les identifiants et les règles réseau.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Préparer un sandbox de base

On crée un sandbox **sans montage** (lab S3) : tout ce qu'on y met reste dans son système de fichiers, donc dans le futur template.

```bash
sbx create --name lab-s10-base shell
sbx run --name lab-s10-base
```

Dans le sandbox, fabriquez un petit « outil » maison :

```bash
mkdir -p ~/outils
printf '#!/bin/sh\necho "Bonjour depuis le template du lab S10"\n' > ~/outils/bonjour.sh
chmod +x ~/outils/bonjour.sh
~/outils/bonjour.sh
exit
```

**Résultat attendu :** le message s'affiche.

---

## Étape 2 — Sauvegarder un template

Arrêtez le sandbox puis sauvegardez-le sous un nom et une étiquette :

```bash
sbx stop lab-s10-base
sbx template save lab-s10-base lab-s10:v1
sbx template ls
```

**Résultat attendu :** `lab-s10:v1` apparaît dans la liste. L'image est stockée dans l'environnement d'exécution de `sbx`, **pas** dans le magasin d'images de votre Docker local.

> 💡 Un template n'est **pas** une sauvegarde complète : les montages (dossier de travail de l'hôte) et le magasin Docker `/var/lib/docker` n'y sont pas inclus.

---

## Étape 3 — Créer un sandbox à partir du template

```bash
sbx run -t lab-s10:v1 --name lab-s10-copie shell
```

Dans le sandbox :

```bash
~/outils/bonjour.sh
exit
```

**Résultat attendu :** l'outil est déjà là, sans réinstallation. Tous vos sandboxes issus de ce template démarrent avec le même environnement.

> Si le template a été préparé pour un autre agent que celui de `sbx run`, la CLI affiche un avertissement et suggère la bonne commande.

---

## Étape 4 — Exporter et importer

Pour partager un template ou le déplacer sur une autre machine :

```bash
sbx template save lab-s10-base lab-s10:v1 --output lab-s10.tar
```

Sur l'autre machine (ou après suppression du template local), on charge puis on utilise :

```bash
sbx template load lab-s10.tar
sbx run -t lab-s10:v1 --name lab-s10-importe shell
```

> 💡 Pour un template publié dans un registre, il faut l'adresse **complète** : `sbx run --template docker.io/mon-org/mon-template:v1 claude` (`sbx` n'ajoute pas `docker.io` tout seul). Pour un registre privé autre que Docker Hub, les identifiants se stockent avec `sbx secret set --registry`.

---

## Étape 5 — Ce qu'un template emporte avec lui

Reprenez le sandbox de base et ajoutez un **faux** secret dans son système de fichiers :

```bash
sbx run --name lab-s10-base
```

Dans le sandbox :

```bash
echo "FAUX-SECRET-POUR-LE-LAB-24680" > ~/.faux-secret
exit
```

Sauvegardez une nouvelle version, puis lancez un sandbox depuis celle-ci :

```bash
sbx stop lab-s10-base
sbx template save lab-s10-base lab-s10:v2
sbx run -t lab-s10:v2 --name lab-s10-fuite shell
```

Dans le sandbox :

```bash
cat ~/.faux-secret
exit
```

**Résultat attendu :** le faux secret est **dans le template**. Quiconque le reçoit le reçoit aussi.

> ⚠️ **Règle :** un template capture les fichiers du sandbox, y compris les clés ou jetons que vous y auriez écrits à la main. Pour garder les identifiants **hors** des templates, utilisez `sbx secret set` (lab S5) : le proxy les injecte à l'exécution sans les écrire dans le système de fichiers.

**Question :** que se passerait-il si ce template `v2` était publié sur Docker Hub ?

---

## Étape 6 — Limites à connaître

- Les fichiers de configuration **utilisateur de l'agent** (par exemple `~/.claude/settings.json`) sont recréés à chaque création de sandbox : vos modifications n'y persistent pas dans un template.
- L'agent installé dans le template garde sa version ; mettre à jour `sbx` ne met pas à jour les agents des sandboxes existants. Pour réutiliser un agent mis à jour, enregistrez un nouveau template après la mise à jour.

---

## Étape 7 — Nettoyer

```bash
sbx rm lab-s10-base lab-s10-copie lab-s10-importe lab-s10-fuite
sbx template rm lab-s10:v1
sbx template rm lab-s10:v2
sbx template ls
```

Supprimez aussi `lab-s10.tar`. Si une image n'apparaît pas dans la liste par défaut (elle n'a pas d'étiquette), utilisez `sbx template ls --all --digests`.

---

## Aperçu — Kits et skills (à venir)

La référence `sbx` propose deux autres mécanismes de réutilisation, signalés comme **expérimentaux** :

| Commande | Rôle |
|---|---|
| `sbx kit` (`pack`, `push`, `pull`, `sign`, `verify`…) | Paquets d'outils et de configuration réutilisables, signables et vérifiables |
| `sbx skills` (`add`, `import`, `ls`, `rm`, `update`) | Skills d'agents partagés avec les nouveaux sandboxes |

Ces fonctions ne sont pas pratiquées dans ce lab : elles varient selon la version de `sbx` (voir diapo 144).

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx template save NOM_SANDBOX nom:tag` | Sauvegarder un sandbox en template |
| `sbx template ls` | Lister les templates |
| `sbx run -t nom:tag --name N AGENT` | Créer un sandbox depuis un template |
| `sbx template save … --output f.tar` | Exporter |
| `sbx template load f.tar` | Importer |
| `sbx template rm nom:tag` | Supprimer |

**À retenir :** un template fige l'environnement, pas les identifiants. Ne le publiez jamais s'il a contenu un secret.

---

➡️ **Suivant :** Lab S11 — MCP dans un sandbox
