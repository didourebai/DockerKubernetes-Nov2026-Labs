# Notes formateur — Lab S1

Sources : présentation (diapos 141, 145, 146), pages *Get started* et *Usage* de la doc Docker Sandboxes. **Les commandes n'ont pas été exécutées de bout en bout** : à tester sur un poste cible.

Confirmé par la page *Usage* :
- `sbx run claude` / `sbx run claude .` / `sbx run --name NOM claude` : syntaxes valides ; reprise avec `sbx run --name NOM` ; `sbx rm` demande une confirmation (`--force`) ; `sbx run --rm` pour une session jetable ; `sbx run claude -- "consigne"` pour passer une consigne.
- `--clone` : le clone suit la branche extraite sur l'hôte ; l'état n'est pas récupéré automatiquement.

À valider :
1. `sbx run --clone --name lab-s1-clone claude` : ordre des options (la doc montre `sbx run --clone claude .` et `sbx run claude --name x ~/chemin`).
2. Étape 6 : `docker ps` sur l'hôte ne montre pas les conteneurs de l'agent (moteur privé), y compris avec Docker Desktop.
3. `sbx policy init balanced` hors invite interactive.
4. Windows : `winget install -h Docker.sbx` (terminal à rouvrir) ; activer *Windows Hypervisor Platform*.
5. Prévoir un plan B pour les stagiaires sans accès Claude Code (démo du formateur).
