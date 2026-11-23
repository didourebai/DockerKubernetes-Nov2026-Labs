# Lab S13 : une « tâche CI » dans un sandbox, sans terminal interactif (PowerShell).
# À lancer depuis la racine du dépôt Git de test (ex. mon-projet).
$nom = "ci-task"

Write-Host "== Création du sandbox (mode clone) =="
sbx create --name $nom --clone shell .
if ($LASTEXITCODE -ne 0) { Write-Host "Échec de la création"; exit 1 }

Write-Host "== Tâche dans le sandbox =="
sbx exec $nom -- sh -c "git switch -c ci/rapport && echo 'Rapport CI' > rapport.txt && git add rapport.txt && git -c user.name=CI -c user.email=ci@example.org commit -m 'Rapport CI'"
$code = $LASTEXITCODE
Write-Host "Code de sortie de la tâche : $code"

Write-Host "== Récupération du travail =="
git fetch "sandbox-$nom"
git log --oneline "sandbox-$nom/ci/rapport"

Write-Host "== Nettoyage =="
sbx rm --force $nom
exit $code
