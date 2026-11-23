# Module IA — Lab intermédiaire A7 : Docker Agent

> **Niveau :** Intermédiaire | **Durée estimée :** 50 minutes
> **Prérequis :** Labs A2 (Model Runner) et A4 (MCP Toolkit), **Docker Desktop 4.63 ou plus** (Docker Agent est inclus ; dans les versions 4.49 à 4.62, la fonctionnalité s'appelait `cagent`)
> **Accès à un service externe :** **oui**, uniquement pour l'étape 5 (recherche web). Les autres étapes utilisent un modèle **local**, sans clé d'API.

## 🎯 Objectifs

- Définir un **agent** dans un fichier YAML, sans écrire de code
- Lui donner des **outils** (réflexion, fichiers, recherche web via un serveur MCP)
- Faire collaborer plusieurs agents dans une **équipe**
- Comprendre pourquoi un agent qui agit doit être **encadré** (lien avec Docker Sandboxes)

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal. Les commandes se lancent depuis `module-ia/lab-docker-agent` (fichiers `*.yaml` et dossier `donnees/` fournis).

---

## Étape 1 — Vérifier les prérequis

```bash
docker agent --help
docker model status
docker model pull ai/qwen3:1.7b
```

**Résultat attendu :** l'aide de `docker agent` s'affiche et Model Runner est en marche. Le modèle `ai/qwen3:1.7b` (environ 1,1 Go) est téléchargé : le modèle sans étiquette `ai/qwen3` pèse environ 5 Go.

> Si `docker agent` n'existe pas, votre Docker Desktop est plus ancien : essayez `cagent --help` (ancien nom) ou mettez Docker Desktop à jour.

---

## Étape 2 — Lire la configuration d'un agent

Ouvrez `agent-simple.yaml` :

```yaml
agents:
  root:
    model: dmr/ai/qwen3:1.7b
    description: Assistant du support informatique
    instruction: |
      Tu es un assistant du support informatique.
      Réponds en français, de façon courte et claire.
    toolsets:
      - type: think
```

**Repérez :**
- `agents` / `root` : l'agent principal
- `model: dmr/ai/qwen3:1.7b` : le préfixe **`dmr/`** désigne un modèle servi par **Docker Model Runner** : aucune clé d'API
- `instruction` : le rôle de l'agent (équivalent d'un « prompt système »)
- `toolsets` : les outils disponibles (`think` = un espace de réflexion)

---

## Étape 3 — Lancer un premier agent

```bash
docker agent run agent-simple.yaml
```

Une interface dans le terminal s'ouvre. Posez :

```text
Comment réinitialiser un mot de passe Windows oublié ?
```

Quittez avec `Ctrl+C` quand vous avez lu la réponse.

Puis lancez une tâche **ponctuelle**, sans interface :

```bash
docker agent run --exec agent-simple.yaml "Donne trois conseils pour choisir un mot de passe."
```

**Observez :** la différence entre la session interactive et le mode `--exec` (une seule réponse, utile dans un script).

---

## Étape 4 — Donner accès aux fichiers

Ouvrez `agent-fichiers.yaml` : il ajoute l'outil `filesystem`. Le fichier `donnees/incidents.txt` contient des incidents fictifs.

```bash
docker agent run agent-fichiers.yaml
```

Posez :

```text
Lis le fichier donnees/incidents.txt et dis-moi quelle catégorie d'incident est la plus fréquente.
```

**Observez :** avant d'utiliser l'outil de lecture, l'agent **demande votre autorisation**. Lisez la demande avant d'accepter.

**Résultat attendu :** la catégorie **VPN** (4 incidents sur 10 dans le fichier).

> **Attention :** l'option `--yolo` accepte **automatiquement tous les appels d'outils**. Ne l'utilisez pas avec un agent qui peut écrire des fichiers ou lancer des commandes.

**Question :** que se passerait-il si on donnait aussi l'outil `shell` à cet agent, et qu'un fichier lu contenait des instructions cachées ? (Voir le lab S6 : injection par le contenu.)

---

## Étape 5 — Ajouter un serveur MCP (recherche web)

Ouvrez `agent-web.yaml` : l'agent utilise le serveur DuckDuckGo du catalogue MCP (`ref: docker:duckduckgo`, lab A4). Il demande **Docker Desktop**.

```bash
docker agent run agent-web.yaml
```

Posez :

```text
Cherche ce qu'est Docker Agent et résume en deux phrases.
```

**Observez :** l'agent demande l'autorisation d'appeler l'outil de recherche, puis cite le site consulté.

**Lien avec le lab A4 :** même serveur, mais ici il est déclaré **dans le YAML de l'agent**, sans passer par le Toolkit en interface.

---

## Étape 6 — Une équipe d'agents

Ouvrez `equipe.yaml` : trois agents.

| Agent | Rôle |
|---|---|
| `root` | Coordinateur : répartit le travail |
| `analyste` | Lit le fichier d'incidents (outil `filesystem`) |
| `redacteur` | Rédige le message aux utilisateurs |

Le coordinateur délègue avec `sub_agents` : chaque sous-agent travaille dans sa propre session, puis rend son résultat.

```bash
docker agent run equipe.yaml
```

Posez :

```text
Analyse donnees/incidents.txt puis rédige un message aux utilisateurs sur les problèmes en cours.
```

**Observez :** les délégations entre agents et le message final.

**Questions :**
- Quand une équipe est-elle préférable à un seul agent ? (Tâches distinctes, outils différents à isoler.)
- Quel coût ajoute-t-on ? (Plus d'appels au modèle, plus de temps, plus de points d'erreur.)

---

## Étape 7 — Encadrer un agent (lien avec Docker Sandboxes)

Un agent qui lit des fichiers ou lance des commandes agit **sur votre machine**. Deux protections complémentaires :

1. **Les autorisations** : demande de confirmation avant chaque outil sensible (à ne pas contourner avec `--yolo`).
2. **L'isolation** : exécuter l'agent dans un environnement isolé. La documentation de Docker Agent mentionne un mode sandbox (`--sandbox`) qui lance l'agent dans un conteneur Docker ; les **Docker Sandboxes** (labs S1 à S13) offrent une isolation par microVM.

**Question :** pour une tâche qui modifie du code, quelle protection choisiriez-vous, et pourquoi ?

---

## Étape 8 — Nettoyer

Rien ne tourne en arrière-plan. Pour libérer l'espace :

```bash
docker model rm ai/qwen3:1.7b
```

---

## ✅ Récapitulatif

| Élément | Rôle |
|---|---|
| `docker agent run fichier.yaml` | Lance l'agent dans le terminal |
| `docker agent run --exec …` | Tâche ponctuelle, sans interface |
| `model: dmr/…` | Modèle local servi par Model Runner |
| `toolsets` | Outils de l'agent : `think`, `filesystem`, `mcp`… |
| `ref: docker:duckduckgo` | Serveur MCP du catalogue Docker |
| `sub_agents` | Équipe d'agents, délégation de tâches |
| `--yolo` | Accepte tous les appels d'outils (**à éviter**) |

**À retenir :**
- un agent se **décrit** (modèle, instruction, outils) au lieu de se programmer
- plus un agent a d'outils, plus il faut l'encadrer
- un petit modèle local peut mal utiliser les outils : c'est un bon sujet de discussion

---

➡️ **Suivant :** Lab A8 — Boucle complète : assistant IA et agent en sandbox
