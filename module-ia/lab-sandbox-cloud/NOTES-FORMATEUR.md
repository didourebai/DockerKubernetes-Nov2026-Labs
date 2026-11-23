# Notes formateur — Lab S9 (à valider avant la formation)

Sources : pages *Use cloud sandboxes* et *Move a sandbox* de la doc (fournies), référence CLI, cheatsheet vidéo (Collabnix, 8 nov. 2026). **Non exécuté** (nécessite un abonnement cloud). La page de **facturation** n'a pas été fournie : l'avertissement de coût reste général (calcul facturé à l'usage pendant l'exécution, non facturé à l'arrêt) ; vérifier les tarifs et quotas du compte avant la formation.

## Écarts avec le cheatsheet vidéo : tranchés par la doc
| Vidéo | Documentation |
|---|---|
| `sbx --cloud ports N --publish 8080` | `sbx --cloud port publish N 8080` (sous-commande `port`) |
| `sbx --cloud ttl +2h N` | `sbx --cloud ttl +30m N` (nom du sandbox après la durée) ; extension limitée à 24 h après la création |
| `sbx --cloud run -d --name N claude` | `sbx --cloud run --detach claude --name N` ; `-d` = `--detach` |
| `--allow-network github.com` | Valide à la **création** (rejeté à la reprise d'un sandbox existant) |
| `sbx rm my-box` (sans `--cloud`) | Pour le cloud : `sbx --cloud rm N` |

## À tester
1. Accès cloud et crédits pour la classe : prévoir un compte de démonstration ou faire le lab en démo.
2. `sbx --cloud create … claude` sans identifiant cloud : la création doit réussir sans session d'agent. Les identifiants cloud (page *credentials*, non lue) sont nécessaires seulement pour lancer l'agent.
3. Étape 6 : un serveur lancé par `sbx --cloud exec … bash -c "nohup … &"` survit-il à la fin de la commande `exec` ? Sinon, trouver une autre méthode (ex. lancer un conteneur avec le moteur Docker privé ; attention à la limitation connue : `docker exec`/healthchecks dans le cloud peuvent viser le mauvais système de fichiers).
4. `python3` présent dans l'image cloud de l'agent `claude`.
5. Étape 8 : `sbx --cloud run --detach claude --name cloud-lab` pour reprendre : ne demande-t-il pas un identifiant de modèle ?
6. Agent `shell` dans le cloud : non vérifié, d'où l'usage de `claude`.
7. Chemins Windows de `sbx --cloud cp` : confirmer que `C:\…\site` est accepté comme source locale.
8. Abonnement : l'API/SDK exige l'abonnement *Docker Agentic Platform* ; vérifier s'il est aussi requis pour la CLI cloud.
9. `sbx move` : voir l'espace disque temporaire (jusqu'à 32 Gio en cloud → local) et l'architecture (`--platform`) avant toute démonstration.
