#!/usr/bin/env bash
# Lab S13 : une « tâche CI » dans un sandbox, sans terminal interactif.
# À lancer depuis la racine du dépôt Git de test (ex. mon-projet).
set -u
NOM=ci-task

echo "== Création du sandbox (mode clone) =="
sbx create --name "$NOM" --clone shell . || { echo "Échec de la création"; exit 1; }

echo "== Tâche dans le sandbox =="
sbx exec "$NOM" -- sh -c "git switch -c ci/rapport && echo 'Rapport CI' > rapport.txt && git add rapport.txt && git -c user.name=CI -c user.email=ci@example.org commit -m 'Rapport CI'"
code=$?
echo "Code de sortie de la tâche : $code"

echo "== Récupération du travail =="
git fetch "sandbox-$NOM" && git log --oneline "sandbox-$NOM/ci/rapport"

echo "== Nettoyage =="
sbx rm --force "$NOM"
exit $code
