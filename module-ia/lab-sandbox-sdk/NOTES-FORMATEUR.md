# Notes formateur — Lab S12 (à valider avant la formation)

Sources : pages *Install the SDK* et *Run your first cloud sandbox* (tutoriel TypeScript) de la doc ; `index.ts` est le programme du tutoriel (messages traduits). **Non exécuté** (nécessite l'abonnement Docker Agentic Platform). Les pages *Authentication and authorization*, *Cookbook* (reçu vide), *API concepts*, *Errors and retries* et *Compute sizes and limits* n'ont pas été fournies : le lab ne code **que** ce que le tutoriel documente (`launchAndWait`, `processes.run`, `refresh`, `delete({ force })`, `waitUntilDeleted`, `client.close`, `client.get`). Pas d'authentification par jeton, pas de transfert de fichiers dans le code.

À tester :
1. Le programme complet de bout en bout, sur Windows et macOS (Node 20+).
2. `index-pause.ts` : dérivé du tutoriel (commande `uname -a` et pause via `setTimeout`) ; vérifier qu'il se compile et que `sbx --cloud ls` montre bien le sandbox créé par le SDK (même compte).
3. Le nom du sandbox créé par `launchAndWait('shell')` (généré par le service) : adapter les commandes `sbx --cloud inspect`.
4. L'abonnement : le SDK exige Docker Agentic Platform ; vérifier si la CLI cloud (S9) exige la même chose. Prévoir un compte de démonstration pour la classe.
5. Étape 6 : le comportement exact après `Ctrl+C` (le sandbox doit survivre ; confirmer).
6. Compléter avec la page PAT (CI) et le Cookbook (fichiers, ports, réseau) pour un lab S12b si ces pages sont fournies.
7. L'API REST : spécification OpenAPI dans la référence « Docker Sandboxes API » (non lue). Aucun exemple `curl` dans la fiche.
