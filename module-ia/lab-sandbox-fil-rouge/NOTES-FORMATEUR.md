# Notes formateur — Lab S7 (à valider avant la formation)

Sources : modules 02, 03 et 04 du dépôt, diapos 138-146, page *Git workflows* (clone mode, `git fetch sandbox-NOM`, confirmé). **Non exécuté.** À tester :

1. Le portail v1.0 (module 02) a déjà une route `/health` (vérifié dans `app.py`). Le Dockerfile v1 utilise `ENV APP_ENV=développement` (accent) : à voir si l'agent le relève.
2. Le build de l'agent : gunicorn n'est pas dans `requirements.txt` du module 02 (il est dans celui des modules 03/04) : l'agent doit l'ajouter, d'où la consigne. Vérifier le comportement réel.
3. `docker inspect --format "{{.State.Health.Status}}"` : les guillemets simples/doubles diffèrent entre PowerShell et bash ; ici, des guillemets doubles fonctionnent dans les deux (à confirmer).
4. Disponibilité du remote `sandbox-lab-s7` si l'agent est quitté avant le `fetch` : la doc ne le garantit que sandbox en cours d'exécution.
5. Branche : la consigne impose `feat/dockerfile-v2` ; si l'agent choisit un autre nom, adapter les commandes `git log`/`diff`.
6. Étape 5 : comparaison avec le module 03 ; le chemin dépend de l'emplacement du dépôt des labs chez le stagiaire.
7. Variabilité : la sortie de l'agent change d'une exécution à l'autre ; la grille de validation sert à juger, pas à comparer mot à mot.
8. Plan B pour les stagiaires sans accès Claude Code : le formateur projette un résultat obtenu à l'avance.
