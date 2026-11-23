# Module IA — Lab complémentaire S9 : Cloud Sandboxes (optionnel, facturé)

> **Niveau :** Intermédiaire | **Durée estimée :** 30 minutes
> **Prérequis :** Labs S1 et S4, `sbx login`, un **accès au calcul cloud** de Docker Sandboxes (abonnement pay-as-you-go)
> **Accès à un modèle :** **non requis** : on n'ouvre jamais de session d'agent
> ⚠️ **Coût :** le calcul cloud est **facturé à l'usage**, tant que le sandbox tourne. Un sandbox arrêté n'est pas facturé pour le calcul. **Supprimez toujours le sandbox à la fin.** Ce lab peut aussi être fait en **démonstration par le formateur**.

## 🎯 Objectifs

- Créer un sandbox sur l'infrastructure gérée par Docker, avec `--cloud`
- Choisir ses ressources et sa **durée de vie** (TTL), et prévoir une suppression automatique
- Exécuter des commandes, transférer des fichiers, exposer un port public
- Arrêter, reprendre, supprimer
- Comparer local et cloud

> **Idée :** la même CLI `sbx` pilote les deux mondes ; l'option globale `--cloud` envoie la commande à l'API Docker Cloud Sandboxes au lieu du démon local. Les identifiants, politiques réseau et cycles de vie du cloud sont **séparés** du local.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Vérifier l'accès cloud

```bash
sbx login
sbx --cloud diagnose
```

**Résultat attendu :** les contrôles (CLI, connexion Docker, API cloud, compte) sont au vert. Si l'accès cloud n'est pas activé sur votre compte, arrêtez-vous ici et suivez la démonstration du formateur.

---

## Étape 2 — Créer un sandbox avec une suppression automatique

Un sandbox cloud expire par défaut après **1 heure**. On choisit explicitement la durée et l'action à l'expiration, pour qu'un oubli ne coûte rien de plus :

```bash
sbx --cloud create --name cloud-lab --cpus 2 --memory 4g --ttl 1h --on-timeout delete claude
```

La commande affiche l'**ID** du sandbox (préfixe `sbx_`).

À savoir :
- le nom doit compter 2 à 63 caractères (lettres, chiffres, tirets), sans point
- un chemin de workspace est **refusé** dans le cloud (`sbx --cloud run claude .` échoue) : les fichiers se transfèrent avec `cp`
- tailles disponibles : micro (1 CPU / 2 Gio), small (2 / 4), medium (4 / 8), large (8 / 16), xl (16 / 32)

> On utilise l'agent `claude` pour créer le sandbox, mais on n'ouvre **pas** de session d'agent : aucun identifiant de modèle n'est nécessaire. (Les identifiants enregistrés pour les sandboxes locaux ne sont pas disponibles dans le cloud.)

---

## Étape 3 — Lister et inspecter

```bash
sbx --cloud ls
sbx --cloud inspect cloud-lab
sbx --cloud ttl cloud-lab
```

**Observez :** l'état, les ressources, le délai avant expiration. **Les sandboxes cloud et locaux sont listés séparément** : comparez avec `sbx ls`.

---

## Étape 4 — Exécuter des commandes

```bash
sbx --cloud exec cloud-lab pwd
sbx --cloud exec cloud-lab uname -r
sbx --cloud exec cloud-lab nproc
sbx --cloud exec cloud-lab free -h
```

**Résultat attendu :** 2 CPU et environ 4 Gio de mémoire, conformément à la taille demandée.

---

## Étape 5 — Transférer des fichiers

Depuis la racine du dépôt des labs, envoyez la page d'exemple. Les chemins côté sandbox doivent être **absolus** :

```bash
sbx --cloud cp module-ia/lab-sandbox-cloud/site cloud-lab:/home/agent/workspace/site
sbx --cloud exec cloud-lab ls -la /home/agent/workspace/site
```

(Sous Windows PowerShell, utilisez `module-ia\\lab-sandbox-cloud\\site` pour le chemin local.)

> 💡 Une copie est un transfert **ponctuel** : rien n'est monté ni synchronisé. Les permissions et les horodatages ne sont pas conservés.

---

## Étape 6 — Exposer un port

Démarrez un petit serveur web dans le sandbox, en arrière-plan :

```bash
sbx --cloud exec cloud-lab bash -c "nohup python3 -m http.server 8080 --directory /home/agent/workspace/site > /tmp/web.log 2>&1 &"
```

Exposez le port :

```bash
sbx --cloud port publish cloud-lab 8080
sbx --cloud port ls cloud-lab
```

La commande renvoie une **URL HTTPS publique**. Ouvrez-la dans le navigateur ✅

> ⚠️ Une URL exposée est un **point d'accès public** : n'importe qui qui l'a peut l'ouvrir. Ne publiez rien de sensible, et retirez l'exposition dès que possible.

```bash
sbx --cloud port unpublish cloud-lab 8080
```

Rechargez l'URL : elle n'est plus accessible.

---

## Étape 7 — Prolonger la durée de vie

```bash
sbx --cloud ttl cloud-lab
sbx --cloud ttl +30m cloud-lab
sbx --cloud ttl cloud-lab
```

**Observez :** l'expiration est repoussée. Une prolongation ne peut pas dépasser **24 heures** après la création.

---

## Étape 8 — Arrêter, reprendre

```bash
sbx --cloud stop cloud-lab
sbx --cloud ls
```

Le calcul n'est **pas facturé** pendant l'arrêt. L'arrêt est confirmé quand `ls` indique l'état arrêté. Pour reprendre sans ouvrir d'agent :

```bash
sbx --cloud run --detach claude --name cloud-lab
sbx --cloud ls
sbx --cloud ttl cloud-lab
```

**Observez :** l'ID est conservé, et un **nouveau** délai de vie démarre.

---

## Étape 9 — Local ou cloud ?

Complétez avec vos observations :

| | Local | Cloud |
|---|---|---|
| Calcul | Votre machine (gratuit) | Infrastructure Docker, **facturé à l'usage** |
| Fichiers du projet | Montage ou `--clone` | Aucun chemin accepté : `cp` ou clone depuis le sandbox |
| Identifiants | `sbx secret` (local) | Identifiants **cloud** séparés |
| Réseau | `sbx policy` local | Politique réseau cloud (`--allow-network` à la création) |
| Durée de vie | Jusqu'à `sbx rm` | **TTL** (1 h par défaut, 24 h au plus) |
| Ports | Publiés sur `localhost` | URL **HTTPS publique** |
| Liste | `sbx ls` | `sbx --cloud ls` |

**Question :** pour quel type de tâche choisiriez-vous le cloud ? (ressources importantes, tâche longue, poste sans virtualisation…)

---

## Étape 10 — Nettoyer (obligatoire)

```bash
sbx --cloud rm cloud-lab
sbx --cloud ls
```

La suppression demande une confirmation, détruit le sandbox et ne peut pas être annulée (`--force` pour les scripts). Vérifiez que **la liste est vide** : plus aucun calcul n'est facturé.

---

## Pour aller plus loin (démonstration du formateur)

**Autoriser un domaine dès la création** :

```bash
sbx --cloud create --name cloud-net --allow-network github.com claude
```

**Session jetable** (supprimée quand l'agent se termine) : `sbx --cloud run --rm claude`.

**Déplacer un sandbox local vers le cloud** : `sbx move NOM_LOCAL --to cloud --ttl 2h --on-timeout stop`. Ce qui est transféré : le système de fichiers du sandbox. Ce qui ne l'est **pas** : processus, mémoire, montages du dossier de travail, secrets gérés, règles réseau locales. Les identifiants écrits dans le sandbox par une connexion interactive d'un agent **sont** inclus dans l'instantané : les retirer avant de déplacer. Ce n'est pas une migration à chaud (diapo 144). Le sandbox source n'est pas supprimé : vérifiez la destination avant de le retirer.

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx --cloud diagnose` | Vérifier l'accès cloud |
| `sbx --cloud create --name N --cpus 2 --memory 4g --ttl 1h --on-timeout delete claude` | Créer |
| `sbx --cloud ls` / `inspect N` | Lister / inspecter |
| `sbx --cloud exec N commande` | Exécuter une commande |
| `sbx --cloud cp ./local N:/chemin/absolu` | Transférer des fichiers |
| `sbx --cloud port publish N 8080` | Exposer un port (URL publique) |
| `sbx --cloud ttl [+30m] N` | Voir / prolonger la durée de vie |
| `sbx --cloud stop N` | Arrêter (calcul non facturé) |
| `sbx --cloud rm N` | Supprimer |

**À retenir :** un sandbox cloud est facturé tant qu'il tourne : fixez un TTL avec `--on-timeout delete`, supprimez après usage, et traitez toute URL exposée comme publique.

---

➡️ **Suivant :** Lab S10 — Templates, Kits et skills
