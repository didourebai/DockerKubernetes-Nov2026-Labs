# Module IA — Lab basique A4 : MCP Toolkit et MCP Gateway

> **Niveau :** Débutant | **Durée estimée :** 40 minutes
> **Prérequis :** Docker Desktop récent avec la fonctionnalité **MCP Toolkit** disponible (Bêta ; testé visuellement avec Docker Desktop 4.100), Lab A1 recommandé (Gordon)
> **Accès à un service externe :** **oui** pour le serveur DuckDuckGo (accès Internet sortant, aucun compte requis)

## 🎯 Objectifs

- Repérer le **MCP Toolkit** dans Docker Desktop, parcourir le **MCP Catalog** et utiliser les **profils**
- Ajouter un **serveur MCP** (DuckDuckGo, affiché « Private Web Search ») en interface graphique puis en ligne de commande
- Démarrer la **MCP Gateway** et constater que les serveurs MCP tournent dans des **conteneurs isolés**
- Distinguer la MCP Gateway de Docker Desktop de la passerelle MCP de **Docker Sandboxes** (lab S11)

> **Rappel (diapos 133-134) :** MCP (Model Context Protocol) est un protocole qui permet à un modèle ou à un agent d'utiliser des **outils** externes. Le **MCP Catalog** liste des serveurs MCP prêts à l'emploi sous forme d'images, le **MCP Toolkit** les gère depuis Docker Desktop (y compris les identifiants), et la **MCP Gateway** est le point d'entrée unique entre les clients et ces serveurs.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Vérifier que le MCP Toolkit est disponible

Dans le menu de gauche de Docker Desktop, repérez l'entrée **MCP Toolkit** (badge **BETA**).

> **Si elle est absente :** ouvrez les **paramètres**, puis **Beta features**, cochez **Enable Docker MCP Toolkit** et cliquez sur **Apply** (ou **Apply & restart**).

Vérifiez que le plugin en ligne de commande répond :

```bash
docker mcp --help
```

**Résultat attendu :** l'aide de `docker mcp` s'affiche, avec les sous-commandes `catalog`, `server`, `gateway`, etc.

Ouvrez **MCP Toolkit** : quatre onglets sont présents, **Profiles**, **Catalog**, **Clients** et **OAuth**.

---

## Étape 2 — Parcourir le MCP Catalog

Ouvrez l'onglet **Catalog** (plus de 300 serveurs).

**À faire :**
- chercher « DuckDuckGo » : le serveur s'affiche sous le nom **Private Web Search** (auteur `nickclyde`, 2 outils, maintenu par la communauté)
- repérer aussi le serveur **GitHub Official**
- ouvrir la fiche de chaque serveur et lire sa description et ses outils

**Questions :**
- Quel serveur demande des identifiants (secret ou OAuth) ? Lequel n'en demande pas ? (voir aussi l'onglet **OAuth**)
- Pourquoi un catalogue d'images vérifiées est-il préférable à un serveur MCP téléchargé au hasard sur Internet ?

---

## Étape 3 — Ajouter un serveur MCP à un profil

Un **profil** regroupe des serveurs et des clients. L'onglet **Profiles** contient un **Default Profile**.

1. Dans l'onglet **Catalog**, cochez **Private Web Search** pour l'ajouter (au profil par défaut si l'interface vous le demande)
2. Revenez à l'onglet **Profiles** : le serveur apparaît dans la carte **Default Profile**

Puis en ligne de commande :

```bash
docker mcp profile ls
docker mcp profile server ls
```

**Résultat attendu :**
```
PROFILE | TYPE  | IDENTIFIER
default | image | duckduckgo
default | image | github-official
```

Le serveur ajouté (identifiant `duckduckgo`) figure dans le profil `default`, avec les serveurs déjà présents (par exemple GitHub).

> **Anciennes versions de la documentation :** `docker mcp server ls`, `enable` et `disable` sont **obsolètes** (« This command is obsolete »). Les serveurs se gèrent maintenant **par profil** avec `docker mcp profile server …`.

---

## Étape 4 — Retirer et ajouter un serveur en ligne de commande

Pour voir que l'interface et la CLI se complètent :

```bash
docker mcp profile server remove default duckduckgo
docker mcp profile server ls
docker mcp profile server add default --server catalog://mcp/docker-mcp-catalog/duckduckgo
docker mcp profile server ls
```

**Résultat attendu :** `Removed 1 server(s) from profile default`, le serveur disparaît de la liste ; puis `Added 1 server(s) to profile default`, il revient. Vérifiez aussi la carte **Default Profile** dans l'interface.

> `catalog://mcp/docker-mcp-catalog/duckduckgo` désigne le serveur `duckduckgo` du catalogue Docker (`docker mcp catalog ls`).

**Pour aller plus loin (optionnel) :** dans l'onglet **Profiles**, la section « Need inspiration? » propose des modèles de profils (AI coding, Dev workflow, Terminal control) et une visite guidée **Start tour**.

---

## Étape 4b — Connecter un client

Votre profil indique **No client connected** : aucun outil ne l'utilise encore.

1. Ouvrez l'onglet **Clients** : il propose **Connect your MCP client** (n'importe quel client MCP) ou des clients préconfigurés (Claude Code, Claude Desktop, Cline, etc.)
2. Choisissez un client installé sur votre poste et cliquez sur **Connect to** (ou **Download** si le client n'est pas installé), puis choisissez le **Default Profile** si l'interface le demande

**Observez :** la carte du profil affiche maintenant le client. Un client **se connecte à la passerelle**, pas à chaque serveur séparément : c'est le rôle de la MCP Gateway.

---

## Étape 5 — Démarrer la MCP Gateway

Les serveurs MCP tournent dans des conteneurs **éphémères** (`docker run --rm`) : ils ne vivent que le temps d'une requête, et `docker ps` les montre rarement. Pour les voir passer, ouvrez d'abord un **second terminal** et suivez les événements Docker :

```bash
docker events --filter label=docker-mcp=true
```

Puis, dans le **premier terminal**, démarrez la passerelle (la commande reste au premier plan) :

```bash
docker mcp gateway run
```

Sans option `--profile`, la passerelle utilise le **profil par défaut**.

**Observez dans les messages de démarrage :**
```
- Those servers are enabled: github-official, duckduckgo
  - Running mcp/duckduckgo with [run --rm -i --init --security-opt no-new-privileges --cpus 1 --memory 2Gb ...]
  > duckduckgo: (2 tools)
```

La ligne `Running` montre la commande `docker run` exacte : `--rm`, `--security-opt no-new-privileges`, 1 CPU et 2 Go de mémoire au plus. Un avertissement `Secret 'github.personal_access_token' not found` est normal si vous n'avez pas autorisé GitHub.

**Résultat attendu dans le second terminal :** des événements `die` puis `destroy` pour l'image `mcp/duckduckgo` : le conteneur a été créé pour lister les outils, puis supprimé. (`Ctrl+C` pour arrêter `docker events`.)

**Question :** pourquoi est-ce important que chaque serveur MCP tourne dans **son propre conteneur** avec des restrictions ? (Un serveur compromis ou un outil malveillant reste confiné ; on retrouve l'isolation vue dans les modules Docker.)

Arrêtez la passerelle avec `Ctrl+C` quand vous avez terminé l'observation.

---

## Étape 6 — Utiliser les outils depuis Gordon (optionnel)

Si Gordon est activé (lab A1), le MCP Toolkit peut lui donner accès aux serveurs que vous avez activés.

Dans Docker Desktop, ouvrez **Ask Gordon** et demandez :

```text
Cherche sur le web ce qu'est le Model Context Protocol et résume en trois phrases.
```

**Observez :** Gordon demande l'autorisation d'utiliser un outil du serveur DuckDuckGo avant de l'appeler.

> Selon votre version de Docker Desktop, l'écran qui connecte Gordon au Toolkit peut s'appeler différemment : suivez les indications du formateur.

---

## Étape 7 — Ne pas confondre avec Docker Sandboxes

| | MCP Gateway (ce lab) | Passerelle MCP de `sbx` (lab S11) |
|---|---|---|
| Fourni par | Docker Desktop (MCP Toolkit) | Docker Sandboxes (`sbx mcp`) |
| Commande | `docker mcp ...` | `sbx mcp ...` |
| Utilisé par | Gordon, éditeurs, clients MCP | Les agents dans les sandboxes |
| Rôle | Exposer des serveurs MCP du catalogue | Donner à l'agent des outils depuis l'extérieur de la microVM |

**Question :** pour qui travaillez-vous (vous, dans votre éditeur ? un agent isolé ?) et laquelle des deux passerelles choisir ?

---

## Étape 8 — Nettoyer

Si vous avez ajouté DuckDuckGo pour ce lab et ne voulez pas le garder :

```bash
docker mcp profile server remove default duckduckgo
docker mcp profile server ls
```

(Gardez-le si vous enchaînez avec le lab A5.) Dans Docker Desktop, vous pouvez aussi décocher **Enable Docker MCP Toolkit** si vous ne l'utilisez plus.

---

## ✅ Récapitulatif

| Élément | Rôle |
|---|---|
| **MCP** | Protocole standard pour donner des outils à un modèle |
| **MCP Catalog** | Serveurs MCP prêts à l'emploi, sous forme d'images |
| **MCP Toolkit** | Interface Docker Desktop pour activer et configurer les serveurs, gérer les secrets |
| **MCP Gateway** | Point d'entrée unique ; lance chaque serveur dans un conteneur isolé |
| `docker mcp profile server ls/add/remove` | Gérer les serveurs d'un profil depuis la CLI |
| `docker mcp gateway run` | Démarrer la passerelle |

**À retenir :**
- un seul point de connexion pour plusieurs serveurs d'outils
- les serveurs MCP sont des **conteneurs**, avec les mêmes bénéfices d'isolation
- les identifiants sont gérés par le Toolkit, pas collés dans des fichiers de configuration

---

➡️ **Suivant :** Lab A5 — Un assistant IA pour le portail IT-Support (Model Runner + MCP Gateway dans Compose)
