# Notes formateur — Lab S5 (à valider avant la formation)

Sources : *Get started* (`sbx secret set github --command 'gh auth token'`), cheatsheet vidéo (`echo "$ANTHROPIC_API_KEY" | sbx secret set anthropic`), diapo 143, référence CLI (`import`, `ls`, `rm`, `set`, `set-custom`). **Non exécuté.** À tester :

1. Confirmé par la page *Usage* : les variables d'environnement (`-e`) sont lisibles dans le sandbox ; les secrets `sbx secret` sont injectés par le proxy sans être exposés à l'agent. **À vérifier concrètement** à l'étape 4 (`env`, `~/.gitconfig`) et corriger la fiche si le jeton apparaît.
1b. `sbx run -e NOM=valeur --name X shell` : confirmer l'ordre des options.
2. `sbx secret ls` : colonnes affichées, et si la valeur est masquée.
3. Le secret `github` écrase-t-il un secret existant ? (précaution de la fiche : ne pas réécrire un secret existant).
4. `curl https://api.github.com` depuis le sandbox : résultat selon la politique réseau.
5. Syntaxe de `set-custom` : non documentée dans ce que j'ai lu : lab avancé éventuel.
6. Pas de fausse clé `anthropic` dans la fiche : elle écraserait une vraie clé sur le poste du stagiaire.
