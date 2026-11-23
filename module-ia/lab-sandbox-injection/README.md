# Module IA — Lab complémentaire S6 : Attaque par injection de prompt

> **Niveau :** Intermédiaire | **Durée estimée :** 40 minutes
> **Prérequis :** Labs S1 à S5 terminés (surtout S4 : politiques réseau)
> **Accès à un modèle :** **non requis** pour le lab principal (l'attaque est simulée), facultatif pour l'étape 7

## 🎯 Objectifs

Illustrer le problème de la diapo 138 : *un agent suit ce qu'on lui dit, et cela peut venir d'une page web ou d'un commentaire dans le code d'un tiers.*

Vous allez :
- constater qu'un projet « innocent » contient une instruction cachée
- laisser un **agent naïf simulé** l'exécuter dans un sandbox avec le réseau ouvert
- refaire l'essai avec le réseau fermé et lire le journal du proxy
- construire une **défense en profondeur**

> ⚠️ **Tout est fictif.** `agent-naif.sh` est un petit script, pas une IA : il joue le rôle d'un agent qui obéirait à n'importe quelle consigne. Les données sont fausses. La seule requête sortante envoie un faux secret à `example.org`, un site de démonstration, uniquement depuis le sandbox. N'exécutez **jamais** le script directement sur votre poste.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal. Les noms de politique de l'étape 4 reprennent ceux du lab S4.

---

## Étape 1 — Préparer le projet piégé

Depuis la racine du dépôt des labs :

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse module-ia\lab-sandbox-injection\projet-piege C:\Labs\projet-piege
cd C:\Labs\projet-piege
```

**Mac / Linux**

```bash
cp -r module-ia/lab-sandbox-injection/projet-piege ~/labs/projet-piege
cd ~/labs/projet-piege
```

```bash
git init
git add .
git commit -m "Projet piégé initial"
```

---

## Étape 2 — Lire le piège

Ouvrez `README.md` dans un éditeur (en vue **source**, pas en rendu) : vous verrez un commentaire HTML invisible dans l'affichage normal de GitHub.

**Windows (PowerShell)**

```powershell
Select-String -Path README.md -Pattern "INSTRUCTION"
```

**Mac / Linux**

```bash
grep INSTRUCTION README.md
```

**Question :** que demande cette instruction ? À qui profite-t-elle ? Un humain qui lit la page rendue la verrait-il ?

---

## Étape 3 — Essai 1 : réseau ouvert

Préparez la politique de départ (voir le lab S4). Notez d'abord votre état initial avec `sbx policy ls`, puis :

```bash
sbx policy allow network example.org
```

Lancez un sandbox sur le projet :

```bash
sbx run --name lab-s6 shell
```

Dans le sandbox, laissez l'agent naïf « travailler » :

```bash
bash agent-naif.sh
```

**Résultat attendu :** l'agent trouve l'instruction, l'exécute, et une ligne `HTTP …` s'affiche : la requête est **partie**, avec le contenu du fichier factice.

Sans quitter le sandbox, notez ce que fait le script : il n'a posé aucune question.

Depuis l'**hôte**, dans une seconde fenêtre :

```bash
sbx policy log
```

**Observez :** la connexion vers `example.org` apparaît comme autorisée.

---

## Étape 4 — Essai 2 : réseau fermé

Sur l'**hôte** :

```bash
sbx policy deny network example.org
sbx policy ls
```

Dans le sandbox :

```bash
bash agent-naif.sh
```

**Résultat attendu :** l'instruction est de nouveau exécutée par l'agent naïf, mais la requête **échoue** (erreur de connexion ou refus du proxy).

```bash
sbx policy log
```

**Observez :** la tentative bloquée est visible dans le journal. C'est ce qui permet de **détecter** une tentative d'exfiltration.

> 💡 Avec le préréglage **Locked Down** (lab S4, étape 7), toute destination non autorisée est bloquée d'office : même sans règle `deny`, l'essai 2 échouerait.

---

## Étape 5 — Réduire ce que l'agent peut voler

Quittez le sandbox (`exit`), puis refaites l'essai 1 avec le mode **clone** et un dossier sans fichier sensible, ou un sandbox **sans montage** (lab S3). Dans quels cas le fichier `donnees-factices.txt` est-il lisible par l'agent ?

```bash
sbx rm lab-s6
sbx policy allow network example.org
sbx create --name lab-s6-vide shell
sbx run --name lab-s6-vide
```

Dans ce sandbox sans montage :

```bash
ls
```

**Résultat attendu :** le projet n'y est pas : il n'y a rien à voler, même si le réseau est ouvert. (Les fichiers du dossier de travail sont des données dont l'agent dispose si vous les lui donnez.)

Sortez avec `exit`.

---

## Étape 6 — Synthèse : la défense en profondeur

Complétez avec vos observations :

| Couche | Ce qu'elle apporte | Constaté dans ce lab |
|---|---|---|
| Politique réseau (S4) | Bloque et journalise les destinations non autorisées | ........ |
| Fichiers partagés (S3) | Moins de fichiers visibles = moins de données à voler | ........ |
| Secrets via le proxy (S5) | La clé n'est pas remise à l'agent | ........ |
| Relecture humaine | `git diff`, revue du journal réseau | ........ |
| Confiance dans le contenu | Un README, une page web ou une issue peuvent contenir des instructions | ........ |

**Questions :**
- Quelle couche aurait été **suffisante** à elle seule pour empêcher l'envoi du faux secret ?
- Pourquoi ne faut-il pas compter sur une seule couche ?
- Un agent moderne peut refuser ce genre d'instruction. Pourquoi ne pas s'en contenter ?

---

## Étape 7 (facultative) — Avec un vrai agent

Si vous avez un accès à Claude Code, relancez un sandbox sur le projet avec le réseau d'`example.org` **fermé** et demandez simplement :

```bash
sbx run --name lab-s6-claude claude -- "Lis le README et explique ce que fait ce projet"
```

Observez le comportement : le résultat dépend du modèle et de la version, et **ne prouve rien** sur la prochaine fois. Une défense qui repose sur la bonne volonté de l'agent n'est pas une défense.

```bash
sbx rm lab-s6-claude
```

---

## Étape 8 — Nettoyer

```bash
sbx policy rm network example.org
sbx rm lab-s6 lab-s6-vide
sbx ls
```

Si vous avez changé le préréglage de politique, remettez l'état noté à l'étape 3. Supprimez enfin le dossier `projet-piege`.

---

## ✅ Récapitulatif

| Idée | À retenir |
|---|---|
| Injection de prompt | Du texte non fiable (README, page web, issue) peut contenir des instructions |
| Le sandbox ne « comprend » pas | Il **limite** les dégâts : fichiers, réseau, secrets fixés avant |
| Détecter | `sbx policy log` |
| Réduire | Moins de fichiers, moins de domaines, secrets via `sbx secret` |

**À retenir :** un agent peut quand même agir via le dossier partagé et les sorties réseau autorisées. Le sandbox n'empêche pas l'agent d'être trompé : il réduit ce qu'il peut faire une fois trompé.

---

➡️ **Suivant :** Lab S7 — Fil rouge : l'agent améliore l'IT-Support Portal
