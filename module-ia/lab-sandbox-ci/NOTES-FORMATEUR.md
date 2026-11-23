# Notes formateur — Lab S13 (à valider avant la formation)

Source : page *Run sandboxes in CI* (fournie) ; référence CLI. **Non exécuté.** Les exécutions planifiées (`sbx schedule`, cloud) font l'objet du lab S13b.

À tester :
1. `sbx login --username ID --password-stdin` avec un PAT de portée *Read* : et son effet sur une session interactive déjà ouverte (le lab S1 est supposé avoir fait `sbx login`).
2. `scripts/ci-job.sh` / `.ps1` : `sbx create --name ci-task --clone shell .` (agent `shell` à confirmer), puis `sbx exec ci-task -- sh -c "…"`. La page *Usage* indique qu'après `sbx create` le sandbox local s'arrête quand plus aucune session ne le garde actif, et la page *Git workflows* que `git fetch sandbox-NOM` échoue si le sandbox est arrêté : le tutoriel de la page CI enchaîne pourtant `exec` puis `git fetch`. **Vérifier que le `fetch` réussit** ; sinon, utiliser `sbx run --detach` ou récupérer avant la fin de l'exec.
3. Le commit dans le clone : identité `git -c user.name=CI -c user.email=ci@example.org`, branche `ci/rapport`. Vérifier que `git switch -c` fonctionne dans le sandbox.
4. Codes de sortie : 125, 127 et le code propre à la commande (valeurs de la doc, pour un sandbox **local**).
5. `echo y | sbx rm NOM` doit échouer avec le code 1 (documenté).
6. `sbx ls --json` en 0.48.0 : tableau, champs `snake_case`. Vérifier `sbx --version` ≥ 0.48.0 avant le lab.
7. PowerShell : `Read-Host -MaskInput` exige PowerShell 7 ; sous PowerShell 5, utiliser `Read-Host -AsSecureString` et convertir, ou saisir le jeton via une variable d'environnement.
8. `jq` n'est pas installé par défaut sous Windows : voir la variante PowerShell.
9. Exécuteur CI : la virtualisation n'est pas garantie sur les exécuteurs hébergés ; la page ne le précise pas. Le fichier `ci-exemple.yml` est un exemple à lire, jamais exécuté. L'étape d'installation de `sbx` sur Linux y est volontairement laissée en commentaire.
10. Sécurité : insister sur la révocation du PAT à la fin du lab.
