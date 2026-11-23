# Module IA — Lab intermédiaire A6 : Applications agentiques avec un Labspace Docker

> **Niveau :** Intermédiaire | **Durée estimée :** 60 minutes (la page officielle ne donne pas de durée)
> **Prérequis :** Labs A2 à A5 (Model Runner, Compose et modèles, MCP Toolkit, assistant IT-Support), Docker Compose avec prise en charge des fichiers Compose OCI
> **Accès à un service externe :** **oui** (téléchargement du Labspace et d'un modèle depuis Docker Hub)

## 🎯 Objectifs

- Lancer un **Labspace** : un laboratoire interactif qui s'exécute lui-même dans des conteneurs
- Suivre le parcours officiel « Building Agentic Apps with Docker » (Compose + Model Runner + MCP Gateway)
- Relier chaque module du Labspace aux labs déjà réalisés (A2 à A5)
- Réaliser un **carnet de bord** : ce que l'on a compris, ce qui reste flou

> **Rappel (diapo 132 à 134) :** une application agentique combine un **modèle** (Model Runner), des **outils** (serveurs MCP derrière la MCP Gateway) et un fichier **Compose** qui déclare le tout.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal. Ce lab est **autonome** : il n'a pas de fichier à copier, le contenu est dans le Labspace.

---

## Qu'est-ce qu'un Labspace ?

Un Labspace est un laboratoire Docker publié comme **fichier Compose** (artefact OCI) sur Docker Hub. Un seul `docker compose up` démarre :
- une **interface web** (http://localhost:3030) qui affiche les instructions et les boutons d'exécution
- un **environnement de travail** (éditeur) dans un conteneur
- un accès Docker **filtré** pour que le lab ne manipule que ses propres ressources

---

## Étape 1 — Vérifier les prérequis

```bash
docker compose version
docker model status
```

**Résultat attendu :** Compose récent, Model Runner en marche. Vérifiez que le port **3030** est libre.

---

## Étape 2 — Lancer le Labspace

```bash
docker compose -p labspace -f oci://dockersamples/labspace-agentic-apps-with-docker up -d
```

**À noter :** le lancement dure environ **2 minutes** avec une bonne connexion : le Labspace télécharge 7 images et le modèle `ai/llama3.2:3B-Q4_K_M` (1,9 Go).

```bash
docker compose -p labspace ps
docker model list
```

**Résultat attendu :** six services `running` (`host-republisher`, `interface`, `socket-proxy`, `visual-chatbot`, `workspace`, `workspace-cleaner`) et le modèle `llama3.2:3B-Q4_K_M` dans `docker model list`. (Le service `configurator` prépare le lab puis s'arrête : c'est normal.)

---

## Étape 3 — Observer l'architecture du Labspace

Avant d'ouvrir l'interface, regardez ce qui tourne :

```bash
docker ps
docker compose -p labspace config
```

**Questions :**
- Combien de conteneurs ? Quels sont leurs rôles (interface, éditeur, proxy du socket Docker, etc.) ?
- Pourquoi un **proxy** filtre-t-il l'accès au socket Docker ? (Le lab doit pouvoir lancer des conteneurs sans toucher à vos autres ressources : même principe de moindre privilège que dans les labs A3 et A5.)

---

## Étape 4 — Suivre le parcours

Ouvrez **http://localhost:3030** et suivez les modules dans l'ordre. Complétez le carnet de bord (fin du lab) au fur et à mesure.

| # | Module du Labspace | Lab correspondant | À observer |
|---|---|---|---|
| 1 | Introduction | — | Les trois briques d'une application agentique |
| 2 | Comprendre les interactions avec un modèle | A2 | Format des requêtes et réponses |
| 3 | Docker Model Runner | A2, A3 | Configuration dans Compose |
| 4 | Outils et MCP | A4 | Appel d'outils, protocole MCP |
| 5 | MCP Gateway | A4, A5 | Démarrer et configurer la passerelle |
| 6 | Tout assembler | A5 | Application agentique complète |
| 7 | Conclusion | — | Résumé et suites possibles |

> Faites une pause après les modules 3 et 5 : à chaque fois, **réexpliquez à voix haute** ce qui vient d'être fait avec vos mots, sans regarder l'écran.

---

## Étape 5 — Comparer avec votre assistant (lab A5)

Une fois le module 6 terminé, comparez avec `lab-assistant-it` :

| Question | Votre réponse |
|---|---|
| Comment l'application trouve-t-elle l'adresse du modèle ? | |
| Comment l'application trouve-t-elle les outils ? | |
| Qui lance le serveur MCP ? | |
| Quel modèle est utilisé et gère-t-il l'appel d'outils ? | |
| Quel est le point le plus fragile du montage (réseau, jeton, socket Docker) ? | |

---

## Étape 6 — Nettoyer

Arrêtez le Labspace **et supprimez ses volumes** (`-v`) : sans cette option, cinq volumes (`labspace-content`, `labspace-socket-proxy`…) restent sur le poste.

```bash
docker compose -p labspace down -v
```

Vérifiez qu'il ne reste rien :

```bash
docker ps
docker volume ls
```

S'il reste des volumes `labspace…`, supprimez-les avec `docker volume rm NOM`.

Le modèle téléchargé n'est pas supprimé par `down`. Pour libérer l'espace :

```bash
docker model rm ai/llama3.2:3B-Q4_K_M
```

Les images du Labspace (`dockersamples/labspace-…`, `mikesir87/…`) restent aussi : `docker images` pour les repérer, `docker rmi` pour les supprimer.

---

## 📓 Carnet de bord

À remplir avant de partir :

1. Trois choses que j'ai comprises :
2. Une chose que je ne saurais pas encore refaire seul :
3. Une idée d'assistant IA pour mon travail (modèle + outils) :
4. Un risque de sécurité que je surveillerais :

---

## ✅ Récapitulatif

| Élément | Rôle |
|---|---|
| **Labspace** | Laboratoire interactif publié comme fichier Compose OCI |
| `docker compose -p labspace -f oci://… up -d` | Lancer un Labspace |
| http://localhost:3030 | Interface du Labspace |
| `docker compose -p labspace down` | L'arrêter |

**À retenir :**
- une application agentique = **modèle + outils + Compose**
- un Labspace est lui-même une application Compose : on peut l'inspecter comme les autres
- l'accès au socket Docker doit toujours être **limité** à ce dont le lab a besoin

---

➡️ **Suivant :** [Lab A7 — Docker Agent](../lab-docker-agent/README.md)
