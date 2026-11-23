# Module IA — Lab avancé S13b : Exécutions planifiées (cloud)

> **Niveau :** Avancé | **Durée estimée :** 35 minutes
> **Prérequis :** Lab S9 (Cloud Sandboxes), un compte avec l'**accès au cloud** et l'**accès aux planifications** (*scheduling*), `sbx --cloud schedule --help` disponible dans votre CLI, connexion **interactive** (`sbx login`, voir l'étape 1)
> **Accès à un modèle :** **non requis** : la tâche est une commande shell, pas un agent IA
> ⚠️ **Coût :** chaque exécution crée un sandbox cloud **facturé** à l'usage. Le lab garde la planification **en pause** et ne lance que des exécutions manuelles ; **supprimez la planification à la fin**. À faire en **démonstration par le formateur** si l'accès n'est pas disponible.

## 🎯 Objectifs

- Créer une planification (`schedule`) qui lance une tâche **à heure fixe** dans un sandbox cloud neuf
- La **tester** avant de l'activer, et lire l'état, le code de sortie et la durée d'une exécution
- Comprendre l'expression **cron** et le fuseau horaire
- Éviter le piège de la **mise à jour qui réinitialise** la configuration
- Comprendre pourquoi les **résultats doivent sortir du sandbox**

> **Idée :** une planification exécute des tâches sans surveillance, sans garder votre poste allumé. Chaque exécution **crée un sandbox cloud neuf** à partir d'un kit et d'une configuration sauvegardés, puis le **supprime** à la fin de la tâche ou à l'expiration de sa durée de vie, selon ce qui arrive en premier.

> **Note Windows / Mac :** une commande par ligne. Les expressions cron et les textes sont entre **guillemets simples** `'…'` ; elles fonctionnent à l'identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Vérifier l'accès et la connexion

```bash
sbx --cloud schedule --help
sbx login
```

**Résultat attendu :** l'aide de `schedule` s'affiche (sous-commandes `create`, `inspect`, `ls`, `rm`, `run`, `runs`, `update`).

> ⚠️ **Connexion interactive obligatoire.** Une connexion interactive (`sbx login`) enregistre un **identifiant de planification** (valable **90 jours**, à renouveler par une nouvelle connexion interactive). Une connexion par **jeton d'accès (PAT)**, comme au lab S13, n'enregistre **pas** cet identifiant : si vous vous étiez connecté ainsi, reconnectez-vous avec `sbx login`. Si la connexion affiche `schedule credential exchange failed`, résolvez-le avant d'aller plus loin.

---

## Étape 2 — Créer une planification en pause

Les planifications ne reçoivent **pas** de dossier de votre poste : chaque exécution démarre sans votre espace de travail. Notre tâche est donc une simple commande :

```bash
sbx --cloud schedule create claude --name lab-s13b --cron '0 9 * * 1' --timezone Etc/UTC --enabled=false --max-run-duration 1h --command 'echo "Bonjour depuis une tâche planifiée" && date'
```

Ce que signifie chaque option :

| Option | Rôle |
|---|---|
| `claude` | Le kit publié utilisé pour chaque exécution (un kit local ou `git+…` n'est pas accepté) |
| `--name` | Nom lisible (les commandes suivantes utilisent l'**identifiant**, pas le nom) |
| `--cron '0 9 * * 1'` | Tous les lundis à 09:00 |
| `--timezone Etc/UTC` | Fuseau IANA, à indiquer **explicitement** |
| `--enabled=false` | Planification **en pause** : seules les exécutions manuelles ont lieu |
| `--max-run-duration 1h` | Durée maximale d'une exécution (au moins `1h`, par défaut `1h`) |
| `--command '…'` | La tâche : **soit** `--command` (commande shell), **soit** `--prompt` (consigne pour un agent) |

La commande renvoie l'**identifiant** de la planification. **Notez-le** : on l'appelle `ID_PLANIF` ci-dessous.

> 💡 Ici, la tâche est une commande : aucun identifiant de modèle n'est nécessaire. Avec `--prompt`, il faudrait configurer les identifiants cloud de l'agent (`sbx --cloud secret set anthropic`).

---

## Étape 3 — Lister et inspecter

```bash
sbx --cloud schedule ls
sbx --cloud schedule inspect ID_PLANIF
```

**Observez :** le rythme (cron), l'état (en pause), le kit et la **prochaine exécution**.

---

## Étape 4 — Tester avant d'activer

Lancez une exécution **maintenant**, même si la planification est en pause :

```bash
sbx --cloud schedule run ID_PLANIF
sbx --cloud schedule runs ID_PLANIF
```

Repérez l'identifiant de l'exécution (`ID_EXEC`), attendez qu'elle se termine, puis :

```bash
sbx --cloud schedule runs inspect ID_PLANIF ID_EXEC
```

**Résultat attendu :** l'état, la raison d'un éventuel échec, le **code de sortie** (quand il est disponible) et les durées.

> ⚠️ **Mettre une exécution en file n'est pas une preuve de succès.** Attendez la fin et vérifiez le **résultat externe**. Notre commande n'écrit nulle part ailleurs que dans le sandbox : le code de sortie `0` est donc la seule trace dans ce lab.

**Exercice :** lancez `sbx --cloud schedule run ID_PLANIF` **deux fois de suite**, rapidement. Que devient la seconde exécution ? (Si une exécution est déjà active, le service annule la nouvelle comme **chevauchante** : attendez la fin de la première.)

---

## Étape 5 — Changer le rythme

Modifier seulement `--name`, `--description`, `--cron`, `--timezone` ou `--enabled` **préserve** la configuration de l'exécution. Passons à « chaque jour ouvrable à 8 h 30, heure de Toronto » :

```bash
sbx --cloud schedule update ID_PLANIF --cron '30 8 * * 1-5' --timezone America/Toronto
sbx --cloud schedule inspect ID_PLANIF
```

| Champ | Minute | Heure | Jour du mois | Mois | Jour de la semaine |
|---|---|---|---|---|---|
| `'30 8 * * 1-5'` | 30 | 8 | tous | tous | du lundi (1) au vendredi (5) |

**Exercice :** écrivez l'expression pour « le premier jour de chaque mois à minuit » (réponse : `'0 0 1 * *'`).

---

## Étape 6 — Le piège : remplacer la configuration

Si vous changez **un réglage d'exécution** (consigne, durée, variables, répertoire de travail) ou fournissez un kit, `schedule update` **remplace** toute la configuration enregistrée. Elle **n'est pas fusionnée** : ce que vous omettez est **réinitialisé** (règles réseau, durée, ressources, plateforme, variables d'environnement, répertoire de travail, serveurs MCP statiques).

Exemple correct : on change la durée **et** on répète la tâche :

```bash
sbx --cloud schedule update ID_PLANIF claude --max-run-duration 2h --command 'echo "Bonjour depuis une tâche planifiée" && date'
sbx --cloud schedule inspect ID_PLANIF
```

**Règle :** pour changer un seul paramètre d'exécution, copiez la commande `create` complète, remplacez `create claude` par `update ID_PLANIF claude`, et changez la valeur voulue. La CLI avertit des réinitialisations mais ne conserve pas ce qui est omis. **Mettez en pause avant de remplacer, puis testez avant de reprendre.**

**Question :** vous ajoutez un secret ou le kit change : la planification en tient-elle compte automatiquement ? (Non : il faut remplacer la configuration pour que les prochaines exécutions la prennent en compte.)

---

## Étape 7 — Activer, puis remettre en pause

```bash
sbx --cloud schedule update ID_PLANIF --enabled=true
sbx --cloud schedule inspect ID_PLANIF
sbx --cloud schedule update ID_PLANIF --enabled=false
```

> ⚠️ **Ne laissez pas la planification activée** : à l'heure du cron, une exécution facturée démarrerait. On l'active seulement pour observer l'état, puis on la remet en pause immédiatement.

---

## Étape 8 — Sortir les résultats du sandbox (à lire)

Le sandbox d'une exécution est **supprimé** à la fin. Une tâche utile doit donc **enregistrer son résultat dans un endroit externe** avant de se terminer (commentaire GitHub, fichier dans un dépôt, message…). Exemple de la documentation, à lire sans l'exécuter : un résumé hebdomadaire des tickets ouverts d'un dépôt, publié comme commentaire sur un ticket de suivi.

```bash
sbx --cloud secret set anthropic
sbx --cloud secret set github
sbx --cloud schedule create claude --name weekly-issue-summary --cron '0 9 * * 1' --timezone Etc/UTC --enabled=false --max-run-duration 1h --workdir /home/agent --env REPOSITORY=<PROPRIETAIRE>/<DEPOT> --env TRACKING_ISSUE=<NUMERO_TICKET> --allow-network api.github.com:443 --prompt 'Résume dix tickets ouverts au maximum de REPOSITORY avec l API REST de GitHub, sans les pull requests ni TRACKING_ISSUE. Publie leurs titres et liens en un seul commentaire sur TRACKING_ISSUE. Arrête-toi en cas d erreur de l API. Ne modifie ni le code ni les autres tickets, et ne demande rien.'
```

(La consigne est écrite sans apostrophe, pour ne pas casser les guillemets simples de la commande.)

Points à retenir de cet exemple :
- les **identifiants** (clé du modèle, jeton GitHub) sont dans le **coffre à secrets** cloud, jamais dans `--env`
- `--env` sert aux **paramètres** de la tâche
- `--allow-network` déclare les **destinations** nécessaires (la politique réseau locale ne se transfère pas)
- la planification est créée **en pause** (`--enabled=false`) jusqu'au test
- la consigne est précise : périmètre limité, **jamais d'entrée interactive**

---

## Étape 9 — Nettoyer

```bash
sbx --cloud schedule rm ID_PLANIF
sbx --cloud schedule ls
sbx --cloud ls
```

La suppression demande une confirmation (`--force` pour l'ignorer). Elle empêche les exécutions suivantes mais ne supprime pas immédiatement le sandbox d'une exécution **active**, qui peut rester jusqu'à son expiration. Si un sandbox de test reste dans `sbx --cloud ls`, supprimez-le (`sbx --cloud rm NOM`).

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx --cloud schedule create KIT --name N --cron '…' --timezone TZ --enabled=false --command '…'` | Créer (en pause) |
| `sbx --cloud schedule ls` / `inspect ID` | Lister / inspecter |
| `sbx --cloud schedule run ID` | Lancer maintenant |
| `sbx --cloud schedule runs ID` / `runs inspect ID ID_EXEC` | Voir les exécutions |
| `sbx --cloud schedule update ID --enabled=true\|false` | Activer / mettre en pause |
| `sbx --cloud schedule update ID --cron '…' --timezone TZ` | Changer le rythme (config préservée) |
| `sbx --cloud schedule update ID KIT …` | **Remplacer** la configuration (tout répéter) |
| `sbx --cloud schedule rm ID` | Supprimer |

**À retenir :** une planification = un sandbox cloud neuf à chaque exécution, supprimé ensuite. Testez avant d'activer, mettez en pause avant de remplacer, sortez les résultats du sandbox, et supprimez ce que vous n'utilisez pas : chaque exécution est facturée.

---

➡️ **Suivant :** les labs Docker AI : Gordon, Model Runner, Compose et modèles, MCP Toolkit.
