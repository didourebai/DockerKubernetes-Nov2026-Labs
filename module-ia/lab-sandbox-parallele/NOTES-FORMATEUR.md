# Notes formateur — Lab S8 (à valider avant la formation)

Sources : page *Git workflows* de la doc (clone mode, tâches parallèles, remote `sandbox-<name>`, worktrees dans le sandbox). **Non exécuté.** À tester :

1. Le comportement de l'agent face à la consigne de worktrees : dépend de l'outil et de la version. La consigne reprend l'exemple de la doc.
2. Noms de branches : si l'agent en choisit d'autres, adapter les commandes `git log`/`merge`.
3. Branche principale (`main` ou `master`) : `git init` utilise la valeur de `init.defaultBranch` du poste.
4. Partie 2 : deux sessions `sbx run --clone --name …` sur le même dossier (noms distincts, comme dans la doc). Confirmer qu'aucun conflit ne survient entre les deux remotes.
5. Fusion : les deux tâches sont conçues pour ne pas entrer en conflit ; vérifier (si l'agent ajoute pytest au `requirements.txt`, il peut y avoir un conflit à résoudre : bon exercice).
6. Durée : prévoir 45 minutes seulement si les stagiaires ont déjà l'accès à Claude Code ; sinon, démonstration formateur.
7. Les routes testées par les tests (`/health`, `/api/status`) existent dans `app.py` du module 03 (à vérifier lors du test).
