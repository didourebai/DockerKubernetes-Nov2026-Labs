# Notes formateur — Lab A4 (à valider avant la formation)

> Exécution du 21/11/2026 (CLI seulement, interface non pilotée) : MCP Toolkit v0.44.3. `docker mcp server ls/enable/disable` sont **obsolètes** : remplacés par `docker mcp profile server ls/add/remove` (testés). `docker mcp gateway run` sans `--profile` charge le profil `default`. Les serveurs sont lancés en `docker run --rm` le temps d'une requête : `docker ps` ne les montre pas, `docker events --filter label=docker-mcp=true` montre `die`/`destroy` (étape 5 réécrite).

Sources : diapos 133-134 ; documentation Docker (pages MCP Toolkit, MCP Gateway, « Use MCP Toolkit from the CLI », dépôt docker/mcp-gateway) trouvée par recherche web. **Commandes non exécutées avec Docker.** L'interface a été vérifiée sur des captures d'écran de Docker Desktop 4.100 : onglets Profiles / Catalog (313) / Clients / OAuth, Default Profile avec GitHub déjà présent, serveur DuckDuckGo affiché « Private Web Search » (nickclyde), modèles de profils.

À valider :
1. **Activation** (déjà visible sur le poste du formateur ; étape de secours conservée) : chemin « Settings > Beta features > Enable Docker MCP Toolkit » (Apply ou Apply & restart selon la version). Le libellé peut changer si la fonctionnalité sort de la Bêta.
2. **Profils** : les versions récentes organisent les serveurs par **profils** (`docker mcp profile ...`, `docker mcp gateway run --profile <id>`). Vérifier si `docker mcp server enable/ls` agit bien sur le profil par défaut dans la version installée ; sinon adapter les étapes 3-4. Avec la CLI seule (hors Docker Desktop), il faut peut-être `docker mcp feature enable profiles`.
3. **`docker mcp catalog init`** : la documentation de l'ancien plugin le mentionne pour initialiser le catalogue par défaut ; à tester si `server ls` ou le catalogue est vide.
4. **Nom du serveur** : `duckduckgo` (ID du catalogue). Confirmer avec la fiche du catalogue (champ Server ID).
5. **Étape 5** : confirmer que les conteneurs `mcp/...` apparaissent bien dans `docker ps` pendant que la passerelle tourne (certains serveurs sont démarrés à la demande, au premier appel d'outil).
6. **Étape 6 (Gordon)** : libellé de l'écran de connexion de Gordon au Toolkit et comportement de demande d'autorisation ; optionnel, à ne conserver que si démontré.
7. **Accès Internet** sortant requis pour DuckDuckGo (réseaux d'entreprise : proxy possible).
8. **Étape 7** : la comparaison avec `sbx mcp` (lab S11) est conceptuelle ; relire la page « MCP gateway » de Sandboxes pour valider la formulation.
9. **Lien avec A5** : la passerelle sera exécutée comme service Compose (diapo 134) avec Model Runner.
10. **Étape 4b (Clients)** : onglet Clients vérifié sur capture (Connect your MCP client, puis Claude Code « Connect to », Claude Desktop et Cline « Download »). Le choix du profil lors de la connexion et le résultat dans la carte du profil sont à valider.
11. **GitHub déjà dans le profil par défaut** : si un serveur demandant OAuth est déjà là, ne pas l'activer pendant la démo sans l'avoir autorisé.
