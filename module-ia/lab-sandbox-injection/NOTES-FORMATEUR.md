# Notes formateur — Lab S6 (à valider avant la formation)

Basé sur la diapo 138 (problème), les labs S3 à S5 et la doc (`sbx create` sans chemin = sandbox sans montage ; `sbx run claude -- "consigne"`). **Non exécuté dans un sandbox** : seul `agent-naif.sh` a été testé hors sandbox pour l'extraction de l'instruction (la requête réseau est bloquée dans mon environnement).

À valider :
1. Le script est exécuté avec `bash agent-naif.sh` (pas besoin de bit exécutable). Un fichier `.gitattributes` force les fins de ligne LF dans ce dossier : vérifier sur Windows que la copie vers `C:\Labs\projet-piege` n'introduit pas de CRLF (sinon `dos2unix` ou recopier depuis un clone récent).
2. Le sandbox contient `curl` et `sed`.
3. Étape 3 : le code HTTP renvoyé par `example.org` pour un POST sur `/collecte` (404 ou autre) : ce qui compte est que la requête **parte**. Adapter le texte.
4. Étape 4 : message exact quand le proxy bloque (erreur de connexion, 403…) et ce que `sbx policy log` affiche ; si `deny network example.org` ne bloque pas après un `allow` antérieur, faire `sbx policy rm network example.org` avant le `deny`.
5. Ordre de l'étape 5 : `sbx rm lab-s6` puis `create` : le mode sans montage est décrit dans le lab S3 (sbx 0.42.0 ou plus).
6. Étape 7 : la réponse d'un vrai agent varie ; ne pas en faire un test pass/fail.
7. Aucune donnée réelle : `example.org` ne reçoit que le faux secret. Prévenir les stagiaires et ne pas modifier l'instruction pour viser un autre site.
