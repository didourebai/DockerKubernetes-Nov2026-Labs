# Notes formateur — Lab S13b (à valider avant la formation)

Sources : pages *Run tasks on a schedule* (fournie en entier) et référence `sbx schedule` de la doc. **Non exécuté** (nécessite l'accès cloud et l'accès aux planifications du compte).

À tester :
1. `sbx --cloud schedule create claude … --command '…'` : la doc montre `--prompt` avec le kit `claude` et décrit `--command` comme l'alternative ; vérifier que `--command` fonctionne avec le kit `claude` (sinon, tester avec le kit `shell` ou un kit `oci://`).
2. Citations : sous PowerShell, une commande entre guillemets simples contenant des guillemets doubles (`echo "…" && date`) doit passer telle quelle ; sinon, déplacer la tâche dans un script. `&&` dans PowerShell 5 n'est pas un opérateur : il est évalué **dans le sandbox** (shell Linux), donc sans problème si la chaîne est transmise intacte : à vérifier.
3. Étape 4 : le délai avant la fin d'une exécution et le contenu de `runs inspect` (état, raison d'échec, code de sortie) ; adapter les captures. Les journaux de sortie de la commande ne semblent pas accessibles par `inspect` : c'est pourquoi la doc insiste sur un résultat externe.
4. Étape 4, exercice « chevauchement » : la doc dit que la seconde exécution est annulée comme chevauchante ; confirmer le message.
5. `--max-run-duration` : au moins 1 h. Ne pas combiner avec `--ttl`.
6. Étape 6 : la CLI avertit des réinitialisations ; relever le texte exact. Vérifier aussi si `update ID claude --max-run-duration 2h` sans `--command` est refusé ou réinitialise la tâche.
7. Accès : « accès aux planifications » activé sur le compte de démonstration ; connexion **interactive** (le PAT du lab S13 ne suffit pas). Renouvellement de l'identifiant tous les 90 jours.
8. L'exemple GitHub de l'étape 8 est repris de la doc (avec une consigne traduite et des placeholders) et **n'est pas exécuté** : si le formateur le démontre, utiliser un dépôt de test et un jeton à portée minimale (lecture des tickets, commentaires).
9. Coût : chaque exécution manuelle crée un sandbox cloud facturé ; limiter le nombre d'exécutions par stagiaire.
