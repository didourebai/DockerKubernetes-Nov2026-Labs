# Module IA — Lab basique S4 : Politiques réseau

> **Niveau :** Débutant | **Durée estimée :** 35 minutes
> **Prérequis :** Labs S1 à S3 terminés, `sbx` connecté
> **Accès à un modèle :** **non requis** (shell dans le sandbox)

## 🎯 Objectifs

- Lire la politique réseau en vigueur
- Observer une requête **autorisée** puis **bloquée**
- Autoriser ou refuser un domaine, et consulter le journal
- Comparer les préréglages **Balanced** et **Locked Down**

> **Pourquoi c'est important :** un agent suit des instructions qui peuvent venir d'une page web ou d'un commentaire dans du code tiers (diapo 138). Le trafic sortant passe par un proxy qui applique vos règles : c'est la barrière qui limite ce qu'un agent trompé peut envoyer à l'extérieur.

> **Important :** les règles `sbx policy` sont **globales** (elles s'appliquent à vos sandboxes locaux, pas à un seul). Notez l'état de départ de l'étape 1 pour pouvoir le restaurer.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Lire la politique actuelle

```bash
sbx policy ls
sbx policy inspect
```

Notez (capture d'écran ou copie) les règles affichées : c'est votre **état de départ**.

Si la politique n'est pas encore initialisée :

```bash
sbx policy init balanced
```

> Balanced autorise les services de développement courants. Locked Down exige une règle d'autorisation explicite pour tout.

---

## Étape 2 — Observer une requête depuis le sandbox

Depuis `mon-projet` :

```bash
sbx run --name lab-s4 shell
```

Dans le sandbox :

```bash
curl -sI https://registry.npmjs.org
curl -sI https://example.org
```

Notez pour chaque adresse : **réponse HTTP** ou **échec/refus**. Gardez ce sandbox ouvert, ou rattachez-le avec `sbx run --name lab-s4` si vous quittez.

---

## Étape 3 — Interroger la politique

Dans une **seconde fenêtre sur l'hôte** :

```bash
sbx policy check example.org
sbx policy check registry.npmjs.org
```

**Question :** la réponse de `check` correspond-elle à ce que vous avez observé à l'étape 2 ?

---

## Étape 4 — Autoriser un domaine

Si `example.org` était refusé, autorisez-le :

```bash
sbx policy allow network example.org
sbx policy ls
```

Dans le sandbox, relancez :

```bash
curl -sI https://example.org
```

**Résultat attendu :** la requête aboutit maintenant.

---

## Étape 5 — Refuser un domaine

Sur l'hôte :

```bash
sbx policy deny network example.org
sbx policy ls
```

Dans le sandbox :

```bash
curl -sI https://example.org
```

**Résultat attendu :** la requête est de nouveau bloquée.

---

## Étape 6 — Consulter le journal

Sur l'hôte :

```bash
sbx policy log
```

**Observez :** les connexions autorisées et refusées par le proxy, avec le domaine concerné.

> 💡 Le tableau de bord interactif (`sbx`, sans argument) contient aussi un **panneau réseau** (touche `tab`) : journal des connexions, autorisation ou blocage d'un hôte, règles personnalisées.

**Question :** si un agent tentait d'envoyer vos fichiers vers un site inconnu, que verriez-vous ici ?

---

## Étape 7 (optionnelle) — Locked Down

> ⚠️ Cette étape modifie votre politique globale. Vérifiez le nom exact des préréglages avec `sbx policy init --help` avant de continuer.

Sur l'hôte :

```bash
sbx policy reset
sbx policy init locked-down
sbx policy ls
```

Dans le sandbox, retestez `registry.npmjs.org` : sans règle explicite, la requête est refusée. Autorisez-la :

```bash
sbx policy allow network registry.npmjs.org
```

**À retenir :** Locked Down = tout est interdit sauf ce que vous autorisez (adapté aux usages sensibles).

Pour revenir à l'état normal :

```bash
sbx policy reset
sbx policy init balanced
```

---

## Étape 8 — Nettoyer

```bash
sbx policy rm network example.org
sbx rm lab-s4
sbx ls
```

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx policy init balanced` | Initialiser la politique (préréglage) |
| `sbx policy ls` / `inspect` | Voir les règles |
| `sbx policy check DOMAINE` | Tester un domaine |
| `sbx policy allow network DOMAINE` | Autoriser |
| `sbx policy deny network DOMAINE` | Refuser |
| `sbx policy rm network DOMAINE` | Supprimer une règle |
| `sbx policy log` | Journal des connexions |
| `sbx policy reset` | Réinitialiser |

**À retenir :** les limites (fichiers, réseau, secrets) sont fixées **avant** le démarrage de l'agent, pas par l'agent. Mais un agent peut agir via les sorties réseau que vous autorisez.

---

➡️ **Suivant :** Lab S5 — Secrets et identifiants
