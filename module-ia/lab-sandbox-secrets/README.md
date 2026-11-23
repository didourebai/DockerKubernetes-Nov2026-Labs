# Module IA — Lab basique S5 : Secrets et identifiants

> **Niveau :** Débutant | **Durée estimée :** 25 minutes
> **Prérequis :** Labs S1 à S4, `sbx` connecté. Facultatif : GitHub CLI (`gh`) connecté (`gh auth login`)
> **Accès à un modèle :** **non requis**

## 🎯 Objectifs

- Comprendre comment un sandbox reçoit des identifiants **sans** les mettre dans le projet
- Comparer avec la mauvaise pratique : une variable d'environnement dans un conteneur
- Gérer les secrets avec `sbx secret`

> ⚠️ **Ne remplacez pas vos vrais secrets.** Si vous avez déjà un secret `anthropic` ou `github` enregistré, ne le réécrasez pas : utilisez uniquement les commandes de lecture à l'étape 1 et la démonstration avec `gh` si le secret `github` n'existe pas.

> **Idée (diapo 143) :** les secrets gérés par le proxy peuvent être injectés dans les requêtes sans être remis directement à l'agent. D'autres identifiants (fichiers du projet, jetons déjà présents dans l'environnement) restent à protéger.

---

## Étape 1 — Voir les secrets déjà enregistrés

```bash
sbx secret ls
```

Notez ce qui existe. **Ne supprimez rien** pour l'instant.

---

## Étape 2 — La mauvaise pratique : un secret dans un conteneur classique

```bash
docker run --rm -e CLE_API=FAUX-SECRET-12345 alpine env
```

**Résultat attendu :** `CLE_API=FAUX-SECRET-12345` s'affiche en clair. Tout programme (donc tout agent) du conteneur peut le lire, l'afficher ou l'envoyer ailleurs.

---

### Même constat dans un sandbox

`sbx run -e` définit une variable dans le sandbox. Avec un shell :

```bash
sbx run -e CLE_API=FAUX-SECRET-12345 --name lab-s5-env shell
```

Dans le sandbox : `env | grep CLE_API`, puis `exit`. **Résultat attendu :** la valeur est lisible : la doc précise que les variables d'environnement sont lisibles par les processus du sandbox. Pour les clés d'API, on utilise donc `sbx secret`.

```bash
sbx rm lab-s5-env
```

---

## Étape 3 — Enregistrer un identifiant avec `sbx secret`

Si vous avez `gh` connecté et **pas** de secret `github` (étape 1) :

```bash
sbx secret set github --command 'gh auth token'
sbx secret ls
```

Le jeton est fourni par la commande `gh auth token` et géré par `sbx`, plutôt que copié dans votre projet. Il sert à permettre à l'agent d'ouvrir des pull requests. Le proxy de l'hôte injecte la vraie valeur dans les requêtes **sans l'exposer à l'agent**. (Pour un identifiant destiné à des hôtes précis, il existe aussi `sbx secret set-custom`, expérimental.)

> Pour une clé d'API de modèle, le principe est le même (par exemple `sbx secret set anthropic`, la valeur étant lue sur l'entrée standard). **Ne le faites pas ici avec une fausse clé** : cela remplacerait une vraie clé existante.

Sans `gh` : passez à l'étape 4 en lisant simplement la sortie de `sbx secret ls`.

---

## Étape 4 — Qu'est-ce que l'agent voit ?

```bash
sbx run --name lab-s5 shell
```

Dans le sandbox :

```bash
env | grep -i -E "token|key|secret|github|anthropic"
cat ~/.gitconfig
ls -la ~
```

**Observez :** retrouvez-vous la valeur du jeton ou de la clé en clair dans l'environnement ? Comparez avec l'étape 2.

Testez la barrière réseau (lien avec S4) :

```bash
curl -sI https://api.github.com
```

> Notez ce que vous observez, même si le résultat diffère de ce que vous attendiez : c'est le but du lab.

```bash
exit
```

---

## Étape 5 — Bonnes pratiques

| À faire | À éviter |
|---|---|
| Enregistrer les identifiants avec `sbx secret` | Mettre une clé dans le `Dockerfile`, un `.env` commité ou un YAML |
| Donner à l'agent des jetons à portée limitée (dépôt unique, durée courte) | Donner un jeton administrateur |
| Contrôler le réseau (S4) | Autoriser tous les domaines |
| Relire `git diff` avant de valider | Faire confiance au résultat d'un agent |

**Question :** si l'agent est trompé par une page web malveillante, qu'est-ce qui limite les dégâts : le secret géré par le proxy, la politique réseau, ou les deux ?

---

## Étape 6 — Nettoyer

```bash
sbx rm lab-s5
```

Pour retirer le secret créé à l'étape 3 (**uniquement si vous l'avez créé pour ce lab**) :

```bash
sbx secret rm github
sbx secret ls
```

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx secret ls` | Lister les secrets |
| `sbx secret set NOM --command 'CMD'` | Enregistrer un secret fourni par une commande |
| `sbx secret rm NOM` | Supprimer un secret |
| `sbx secret import` / `set-custom` | Importer / secret personnalisé (voir `--help`) |

**À retenir :** un secret passé par variable d'environnement est lisible par l'agent. Un secret géré par le proxy ne lui est pas remis directement, mais les fichiers partagés et les sorties réseau autorisées restent à protéger.

---

➡️ **Suivant :** Lab S6 — Attaque par injection de prompt
