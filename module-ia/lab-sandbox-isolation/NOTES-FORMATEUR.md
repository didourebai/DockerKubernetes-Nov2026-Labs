# Notes formateur — Lab S2 (à valider avant la formation)

Rédigé d'après la présentation (diapos 139-140, 142-143) et la référence CLI `sbx`. **Non exécuté de bout en bout.** À tester :

1. Existence de l'agent `shell` : `sbx run --name lab-s2 shell` (la doc liste « Shell » parmi les agents ; vérifier le nom exact avec `sbx run --help`).
2. `sbx exec` : la page *Usage* confirme `sbx exec -it NOM bash` ; la forme sans `-it` (`sbx exec NOM uname -r`) est à tester.
3. Étape 3 : confirmer que `/tmp` est bien propre au sandbox et que le dossier courant est monté en lecture-écriture.
4. Étape 4 : sur un poste sans Docker, la partie « hôte » échoue : prévoir Docker Desktop ou la démonstration du formateur.
5. Étape 5 : le résultat de `id` dépend de l'image du shell : relever la sortie réelle et adapter la consigne.
6. Étape 6 : avec le préréglage Balanced, noter quels domaines passent ou non (npmjs vs example.com) et ajuster le texte de la fiche en conséquence.
7. Remplir la colonne « observation » du tableau de synthèse avec les vraies valeurs.
