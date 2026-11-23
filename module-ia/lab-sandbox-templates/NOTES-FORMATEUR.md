# Notes formateur — Lab S10 (à valider avant la formation)

Sources : page *Usage* de la doc (sections *Saving a sandbox as a template*, *Load a template*, *Updating agents*), référence CLI. **Non exécuté.** Les pages **Kits** (`customize/use-kits.md`, `customize/author/…`) et **Share agent skills** (`workflows/agent-skills.md`) n'ont pas été fournies : le lab se limite aux templates et ne fait qu'un aperçu des Kits et skills. À compléter si ces pages sont fournies (lab avancé distinct).

À tester :
1. Un sandbox sans montage (`sbx create --name X shell`) : l'agent `shell` doit exister (sinon, utiliser `claude` pour la création et `sbx exec -it X bash` pour y travailler).
2. `sbx template save SANDBOX nom:tag` : la doc dit « stop the sandbox (or let the CLI prompt you) » : confirmer que le sandbox peut être sauvegardé sans arrêt manuel.
3. `sbx run -t lab-s10:v1 --name lab-s10-copie shell` : ordre des options avec `-t` et `--name`.
4. `~` dans le sandbox : confirmer qu'il s'agit de `/home/agent` (système de fichiers du conteneur, inclus dans le template).
5. Export : `sbx template save SANDBOX nom:tag --output f.tar` (forme documentée). Pour la démonstration d'import, supprimer d'abord le template local (`sbx template rm`) pour qu'elle soit significative.
6. Étape 5 : le faux secret doit bien se retrouver dans le template `v2` ; sinon, ajuster le texte.
7. `sbx rm` avec plusieurs noms : une confirmation est demandée pour chacun.
