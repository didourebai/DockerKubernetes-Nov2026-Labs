# Module IA — Lab avancé S11 : MCP dans un sandbox (MCP gateway)

> **Niveau :** Intermédiaire | **Durée estimée :** 40 minutes
> **Prérequis :** Labs S1, S4 et S5 terminés ; **Docker installé et démarré sur l'hôte** (le serveur MCP du lab s'exécute sur l'hôte) ; `sbx` version **0.48.0 ou plus** (pour `sbx mcp unload`)
> **Accès à un modèle :** **non requis** pour les étapes 1 à 6 (on démarre les sandboxes sans ouvrir de session d'agent) ; requis seulement pour l'étape 7, facultative

## 🎯 Objectifs

- Enregistrer **une fois**, sur l'hôte, un serveur MCP (Model Context Protocol)
- Le rendre disponible dans un sandbox via la **MCP gateway** de `sbx`
- Comparer le mode **statique** et le mode **dynamique**
- Charger et décharger un serveur dans un sandbox en cours d'exécution
- Comprendre **où s'exécute** un serveur MCP, et ce que cela change pour la sécurité

> **Rappel (diapo 133) :** MCP est un protocole ouvert qui permet à une application d'IA d'utiliser des outils externes ; la MCP Gateway est le point d'accès central qui route les appels vers les serveurs MCP.
>
> **Ne pas confondre :** la gateway de **Docker Sandboxes** (`sbx mcp`) est distincte du **MCP Toolkit** de Docker Desktop. Les réglages de l'un ne sont pas partagés avec l'autre, et le MCP Toolkit n'est pas nécessaire ici.

> **Note Windows / Mac :** une commande par ligne, identique dans PowerShell et dans le Terminal.

---

## Étape 1 — Comprendre ce que l'on construit

Sans gateway, on configurerait le serveur MCP **dans l'agent** (par exemple dans Claude Code). Avec Docker Sandboxes :

1. vous **enregistrez** les serveurs une seule fois sur l'hôte (`sbx mcp add`)
2. la **gateway** du sandbox expose à l'agent un **seul** point d'accès MCP
3. `sbx` gère les identifiants (OAuth, secrets) et le cycle de vie côté hôte

Un serveur peut être **distant** (une URL), ou **local** (démarré sur l'hôte, en `stdio`). L'agent, dans le sandbox, ne parle jamais qu'à la gateway.

---

## Étape 2 — Enregistrer un serveur MCP local

On enregistre le serveur `fetch` (récupération de pages web), décrit dans le registre communautaire MCP sous forme de paquet OCI. Docker doit être démarré sur l'hôte :

```bash
sbx mcp add fetch --local --url https://registry.modelcontextprotocol.io/v0/servers/fetch-mcp/versions/latest
sbx mcp ls
sbx mcp inspect fetch
```

**Résultat attendu :** `fetch` est listé avec son transport, son statut et sa gateway. L'enregistrement est **sur l'hôte** : il n'est attaché à aucun sandbox pour l'instant.

> Si l'entrée du registre ne publie pas de paquet OCI en `stdio`, `sbx` refuse l'enregistrement. Dans ce cas, utilisez la variante `sbx mcp add fetch --url dhi.io/fetch-mcp:latest` (image durcie) ou demandez au formateur.

> ⚠️ **Sécurité :** un serveur `stdio` local s'exécute **sur l'hôte, hors de l'isolation du sandbox**. Le processus ou conteneur peut accéder aux fichiers et au réseau de l'hôte. Ne l'enregistrez qu'avec des commandes et des images de confiance.

---

## Étape 3 — Mode statique : charger un serveur au démarrage

On crée un sandbox qui charge **uniquement** `fetch`. On le démarre en arrière-plan, sans ouvrir de session d'agent :

```bash
sbx run --detach --name lab-s11-statique --static-mcp fetch claude
sbx inspect lab-s11-statique
```

**Résultat attendu :** `MCP mode : static` et `MCP servers : fetch`.

En mode statique, l'agent ne reçoit **aucun** outil de découverte : il ne peut pas aller chercher d'autres serveurs. Le choix reste en vigueur après un redémarrage.

---

## Étape 4 — Mode dynamique : l'agent découvre les serveurs

Sans `--static-mcp`, aucun serveur n'est préchargé, et l'agent reçoit des outils pour **chercher et attacher** les serveurs enregistrés (`mcp-find`, `mcp-add`, `mcp-config-set`) :

```bash
sbx run --detach --name lab-s11-dynamique claude
sbx inspect lab-s11-dynamique
```

**Résultat attendu :** `MCP mode : dynamic`, `MCP servers : none`.

**Question :** quel mode choisir pour un agent qui exécute des tâches sensibles ? (celui où **vous** décidez à l'avance des outils disponibles.)

---

## Étape 5 — Charger et décharger un serveur à chaud

Depuis l'hôte, attachez `fetch` au sandbox dynamique **déjà en cours d'exécution** :

```bash
sbx mcp load fetch --sandbox lab-s11-dynamique
sbx inspect lab-s11-dynamique
```

**Résultat attendu :** `MCP servers : fetch`. Une session d'agent déjà ouverte reçoit la mise à jour de la liste d'outils, sans reconnexion.

Retirez-le :

```bash
sbx mcp unload fetch --sandbox lab-s11-dynamique
sbx inspect lab-s11-dynamique
```

**Résultat attendu :** `MCP servers : none`. L'enregistrement et les identifiants restent sur l'hôte ; les autres sandboxes ne sont pas touchés.

> 💡 En mode dynamique, `unload` n'empêche pas l'agent de **rattacher** le serveur lui-même ensuite : pour interdire cela, utilisez le mode statique.

---

## Étape 6 — Aucun serveur du tout

```bash
sbx run --detach --name lab-s11-vide --static-mcp none claude
sbx inspect lab-s11-vide
```

**Résultat attendu :** mode statique, aucun serveur, et **aucun** outil de découverte. Ce mode reste statique même après chargement/déchargement et redémarrage.

---

## Étape 7 (facultative) — Avec un vrai agent

Les agents qui configurent MCP au démarrage : Claude Code, Codex, Devin, Kiro, OpenCode. Avec un accès à Claude Code :

```bash
sbx run claude --name lab-s11-agent --static-mcp fetch
```

Demandez : « Utilise l'outil `fetch` pour lire https://example.org et résume la page. » Observez l'appel d'outil.

**Questions (lien avec le lab S4) :**
- Le serveur `fetch` s'exécute sur l'**hôte**, pas dans le sandbox. La requête vers `example.org` passe-t-elle par la **politique réseau du sandbox** ? Vérifiez avec `sbx policy log`.
- Qu'est-ce que cela implique pour une organisation qui compte sur la politique réseau pour limiter ce qu'un agent peut joindre ?

Quittez l'agent quand vous avez terminé.

---

## Étape 8 — Lire : serveurs protégés et outils internes de la gateway

**Serveur distant avec clé d'API** (à lire, non exécuté) : la clé est stockée avec `sbx secret` et référencée par un *placeholder* dans l'en-tête ; elle reste sur l'hôte :

```bash
sbx mcp add acme --url https://mcp.acme.com/mcp --header 'Authorization: Bearer ${api-key}'
sbx secret set mcp:acme:api-key
```

**Serveur distant avec OAuth :** `sbx mcp add` ouvre le flux d'autorisation ; les jetons restent sur l'hôte (`sbx mcp auth status|auth|auth rm`). Les connexions OAuth sont exposées à l'agent via un outil `<serveur>-authorize`.

**Outils propres à la gateway** (visibles dans les listes d'outils, journaux et politiques) :

| Outil | Rôle |
|---|---|
| `mcp-exec` | Exécute un outil par son nom, via la gateway |
| `code-mode` | Crée un outil JavaScript éphémère qui appelle d'autres outils |
| `mcp-find` / `mcp-add` / `mcp-config-set` | Découvrir, attacher, configurer un serveur (**mode dynamique** seulement) |
| `<serveur>-authorize` | Démarrer ou relancer l'autorisation OAuth d'un serveur distant |

Les organisations avec **AI Governance** peuvent contrôler l'enregistrement des serveurs, les appels d'outils et les approbations par des politiques MCP.

---

## Étape 9 — Nettoyer

Supprimez d'abord les sandboxes, puis l'enregistrement (supprimer une inscription ne détache pas un serveur déjà chargé dans un sandbox) :

```bash
sbx rm --force lab-s11-statique lab-s11-dynamique lab-s11-vide lab-s11-agent
sbx mcp rm fetch
sbx mcp ls
sbx ls
```

---

## ✅ Récapitulatif

| Commande | Action |
|----------|--------|
| `sbx mcp add NOM --url URL` | Enregistrer un serveur distant |
| `sbx mcp add NOM --local --url URL_METADONNEES` | Serveur local décrit par un paquet OCI (`stdio`) |
| `sbx mcp add NOM --command CMD --args …` | Serveur local par commande explicite |
| `sbx mcp ls` / `inspect NOM` | Lister / inspecter |
| `sbx run … --static-mcp a,b AGENT` | Mode statique : seuls `a` et `b` |
| `sbx run … --static-mcp none AGENT` | Aucun serveur, pas de découverte |
| `sbx mcp load NOM --sandbox S` / `unload` | Attacher / détacher à chaud |
| `sbx inspect S` | Voir le mode MCP et les serveurs connectés |
| `sbx mcp rm NOM` | Supprimer l'enregistrement |

**À retenir :** la gateway centralise les serveurs et les identifiants sur l'hôte, mais un serveur local `stdio` s'exécute **hors de l'isolation du sandbox**. Préférez le mode statique pour décider à l'avance des outils de l'agent.

---

➡️ **Suivant :** Lab S12 — Piloter un sandbox par code (SDK TypeScript / API REST)
