# Notes formateur — Lab S3

Sources : diapo 142, pages *Get started* et *Usage* de la doc. **Non exécuté.**

Confirmé par la page *Usage* :
- Sandbox sans montage : `sbx create --name X agent` puis `sbx run --name X` (sbx 0.42.0 ou plus). Dossier de travail : `/home/agent/workspace`.
- `--clone` : copie Git dans le sandbox ; le dépôt hôte est lisible en lecture seule dans `/run/sandbox/source` ; le clone suit la branche extraite ; supprimé avec le sandbox ; dépôt Git obligatoire ; refusé depuis un worktree secondaire.
- `sbx cp` : chemins sandbox **absolus** obligatoires.
- Plusieurs sandboxes sur le même dossier : noms distincts obligatoires.

À valider :
1. `sbx run --clone --name NOM shell .` : ordre des options.
2. Agent `shell` (nom exact : `sbx run --help`).
3. Les fichiers non suivis par Git sont-ils copiés dans le clone ?
4. Chemin du clone (`pwd`) : le relever pour la correction.
5. Récupération de commits : `git fetch sandbox-NOM` (page *Git workflows*, confirmé). Tester qu'après `exit` du shell le remote est encore disponible ou non (la doc ne le précise que pour `sbx stop`) ; adapter la mise en garde de l'étape 4.
6. `touch /run/sandbox/source/test.txt` : confirmer le message d'erreur.
