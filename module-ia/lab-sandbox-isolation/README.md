# Module IA — Lab basique S2 : Prouver l'isolation d'un sandbox

> **Niveau :** Débutant | **Durée estimée :** 30 minutes
> **Prérequis :** Lab S1 terminé (`sbx` installé, connecté, politique réseau initialisée), Docker Desktop ou Docker Engine sur le poste (pour la comparaison avec un conteneur classique), le dossier `mon-projet` du lab S1
> **Accès à un modèle :** **non requis** : on utilise un shell, pas d'agent IA

## 🎯 Objectifs

Vérifier par vous-même ce qu'annonce la présentation (diapos 139-140) :

- un sandbox a **son propre noyau**, son système de fichiers et son réseau
- il héberge un **moteur Docker privé** : ce que l'on y fait n'apparaît pas sur l'hôte
- seuls les dossiers **explicitement partagés** sont visibles des deux côtés

> **Règle à retenir :** on conteneurise l'application, on met l'agent en sandbox. Les deux se complètent.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.
> Quand ce n'est pas possible, deux blocs sont fournis.

> ⚠️ Le lab utilise le « agent » **Shell** de `sbx` : un terminal dans le sandbox, sans IA. Vérifiez qu'il est disponible avec `sbx run --help` (la liste des agents varie selon la version de `sbx`).

---

## Étape 1 — Point de référence : un conteneur classique

Depuis le dossier `mon-projet` :

```bash
docker run --rm alpine uname -r
docker run --rm alpine ls /
```

Notez la **version du noyau** affichée : un conteneur partage le noyau de son hôte (sous Windows et macOS, celui de la VM Linux de Docker Desktop).

---

## Étape 2 — Ouvrir un shell dans un sandbox

Toujours dans `mon-projet` :

```bash
sbx run --name lab-s2 shell
```

Vous obtenez un terminal **à l'intérieur** du sandbox. Les étapes 3 à 6 s'y exécutent, sauf mention contraire.

---

## Étape 3 — Un noyau et un système de fichiers à lui

Dans le sandbox :

```bash
uname -r
ls /
pwd
ls
```

**Observez :**
- la version du noyau (comparez avec l'étape 1)
- le répertoire courant : c'est votre projet, monté en **lecture-écriture**

Testons les frontières :

```bash
touch /tmp/fichier-prive.txt
touch fichier-partage.txt
```

Ouvrez **une seconde fenêtre de terminal sur l'hôte**, dans `mon-projet` :

**Windows (PowerShell)**

```powershell
dir
```

**Mac / Linux**

```bash
ls
```

**Résultat attendu :**
- `fichier-partage.txt` est **visible** sur l'hôte (dossier partagé)
- `fichier-prive.txt` est **introuvable** : il n'existe que dans le sandbox

Supprimez le fichier partagé depuis l'hôte :

**Windows (PowerShell)**

```powershell
del fichier-partage.txt
```

**Mac / Linux**

```bash
rm fichier-partage.txt
```

> 💡 Ce qui est partagé est exposé **dans les deux sens** : l'agent peut modifier ou supprimer vos fichiers du dossier monté. C'est la raison d'être du mode `--clone` (lab S3).

---

## Étape 4 — Un moteur Docker privé

De retour dans le sandbox :

```bash
docker run --rm hello-world
docker ps -a
docker images
```

Puis sur l'**hôte** (seconde fenêtre) :

```bash
docker images hello-world
docker ps -a
```

**Résultat attendu :** `hello-world` apparaît dans le sandbox, mais **pas** dans la liste des images de l'hôte. Le démon Docker de l'hôte n'est jamais sollicité.

**Question :** quel risque évite-t-on par rapport à un conteneur qui monterait le socket Docker de l'hôte ?

---

## Étape 5 — Droits et identité

Dans le sandbox :

```bash
id
whoami
```

Un agent peut disposer de privilèges élevés **dans** la microVM sans obtenir ceux de l'hôte. Notez ce que vous observez (utilisateur, groupes).

---

## Étape 6 — Réseau : une seule sortie

Dans le sandbox :

```bash
curl -sI https://registry.npmjs.org
curl -sI https://example.com
```

**Observez** quelles requêtes aboutissent et lesquelles sont refusées : le trafic sortant passe par un proxy qui applique la politique réseau. Notez les résultats : on les exploite dans le lab S4.

Quittez le shell du sandbox :

```bash
exit
```

---

## Étape 7 — Inspecter le sandbox depuis l'hôte

```bash
sbx ls
sbx inspect lab-s2
sbx df
```

**Résultat attendu :** le sandbox `lab-s2` est listé avec son espace de travail ; `inspect` affiche ses détails, `df` l'utilisation disque.

Exécuter une commande dans un sandbox **sans y entrer**, ou y ouvrir un shell :

```bash
sbx exec lab-s2 uname -r
sbx exec -it lab-s2 bash
```

(`exit` pour sortir du second.) Par défaut, la commande démarre dans le dossier de travail principal du sandbox.

---

## Étape 8 — Synthèse

Complétez ce tableau avec vos observations :

| | Conteneur (`docker run`) | Docker Sandbox |
|---|---|---|
| Frontière d'isolation | Espaces de noms et cgroups | Hyperviseur |
| Noyau | Partagé avec l'hôte | ........ (votre observation) |
| Docker à l'intérieur | Docker-in-Docker ou socket monté | ........ |
| Fichiers de l'hôte visibles | Seulement les montages | ........ |
| Fichier créé hors du dossier partagé | ........ | ........ |

---

## Étape 9 — Nettoyer

```bash
sbx stop lab-s2
sbx rm lab-s2
sbx ls
```

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx run --name NOM shell` | Terminal dans un nouveau sandbox |
| `sbx exec NOM commande` | Exécuter une commande dans un sandbox |
| `sbx exec -it NOM bash` | Ouvrir un shell dans un sandbox |
| `sbx inspect NOM` | Détails d'un sandbox |
| `sbx df` | Utilisation disque |
| `sbx stop` / `sbx rm` | Arrêter / supprimer |

**À retenir :**
- une microVM = un noyau, un système de fichiers et un réseau par sandbox
- le moteur Docker de l'agent est privé : l'hôte n'est pas touché
- les fichiers partagés et les sorties réseau autorisées restent exposés aux actions de l'agent

---

➡️ **Suivant :** Lab S3 — Ce que l'agent peut atteindre : fichiers
