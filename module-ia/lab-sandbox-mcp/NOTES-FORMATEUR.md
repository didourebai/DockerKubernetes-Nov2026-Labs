# Notes formateur — Lab S11 (à valider avant la formation)

Source : page *MCP gateway* de la doc Docker Sandboxes (fournie en entier). **Non exécuté.** Les commandes reprennent celles de la page.

À tester :
1. `sbx run --detach --name X --static-mcp fetch claude` : l'ordre des options et le démarrage détaché **sans identifiant de modèle** (la doc montre `sbx run claude --name mcp-demo --static-mcp notion` et `sbx run -d --name N claude .`). Si cela exige un identifiant, passer par `sbx create` puis `sbx run --name X --detach`.
2. `sbx inspect NOM` : champs `MCP mode` et `MCP servers` ; la doc indique qu'un tiret `-` signifie « indisponible » (sandbox arrêté ?). Adapter le texte aux sorties réelles.
3. Serveur `fetch` : l'entrée du registre `https://registry.modelcontextprotocol.io/v0/servers/fetch-mcp/versions/latest` est l'exemple de la doc ; vérifier qu'elle publie un paquet OCI `stdio`, sinon utiliser `dhi.io/fetch-mcp:latest` (nécessite l'accès aux images durcies) ou un autre serveur. Docker doit être démarré sur l'hôte.
4. `sbx mcp unload` : nécessite `sbx` 0.48.0 ou plus (vérifier `sbx --version`).
5. Étape 7 : la question sur la politique réseau est **ouverte** : le serveur tourne sur l'hôte (la doc dit que le conteneur/processus accède aux fichiers et au réseau de l'hôte). Tester ce que `sbx policy log` montre réellement et corriger la fiche.
6. Pas de serveur OAuth dans le lab (Notion, Linear : comptes tiers). Option de démonstration par le formateur : `sbx mcp add notion --url https://mcp.notion.com/mcp` (flux OAuth dans le navigateur).
7. Le MCP Toolkit de Docker Desktop (diapos 133-134) est différent : les serveurs de l'un ne sont pas visibles dans l'autre.
8. Cloud : les sandboxes cloud utilisent les serveurs de Docker Agentic Platform (`sbx --cloud mcp load`) ; `--static-mcp none` n'y est pas pris en charge. Hors périmètre de ce lab.
