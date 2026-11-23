# Notes formateur — Lab A7 (à valider avant la formation)

Sources : documentation Docker Agent (pages Introduction, Quick Start, CLI reference, Configuration, Multi-agent, Tips) et page du Labspace `labspace-docker-agent`. **Lab non exécuté.** Les fichiers YAML ont été validés syntaxiquement seulement.

Faits repris de la documentation :
- Docker Agent est inclus dans Docker Desktop 4.63 et plus ; les versions 4.49 à 4.62 l'appelaient `cagent`
- `docker agent run [config] [message]`, `--exec` pour une tâche ponctuelle, `--yolo` pour tout accepter, `docker agent new`, `docker agent getting-started`
- toolsets : `think`, `filesystem`, `shell`, `memory`, `mcp` (avec `ref: docker:duckduckgo`, qui exige Docker Desktop)
- les modèles `dmr/...` n'exigent pas de clé d'API
- équipe : `sub_agents` et outil de délégation `transfer_task`
- un mode `--sandbox` existe (la page « Tips » le cite pour exécuter un agent dans un conteneur isolé)

À valider :
1. **Modèle `dmr/ai/qwen3:1.7b`** : la documentation cite `dmr/ai/gemma3-qat:12B` en exemple. Vérifier que `qwen3` est reconnu et **gère l'appel d'outils** ; sinon changer le nom du modèle dans les quatre fichiers YAML. Un petit modèle local peut être peu fiable avec plusieurs outils.
2. **Syntaxe exacte** : les YAML sont construits à partir d'exemples de la documentation reformulés (la page ne permettait pas de les recopier mot pour mot). Lancer `docker agent run` sur chacun ; ajouter `version:` en tête si la version installée le demande.
3. **`type: filesystem`** : confirmer le périmètre accessible par défaut (dossier courant ?) et le texte des demandes d'autorisation.
4. **Résultat attendu de l'étape 4** : le fichier `incidents.txt` contient 4 incidents VPN sur 10 (INC-002, 005, 007, 010) ; vérifier que le modèle répond correctement.
5. **Étape 5** : nécessite Docker Desktop et un accès Internet ; confirmer que `docker:duckduckgo` est résolu.
6. **Étape 6** : l'équipe peut échouer si le modèle ne délègue pas ; prévoir une démonstration de secours.
7. **`--sandbox`** (étape 7) : option citée dans les conseils d'utilisation ; non testée, et à ne pas confondre avec `sbx` (Docker Sandboxes).
8. **Labspace complémentaire** : `docker compose -f oci://dockersamples/labspace-docker-agent up` (page du Labspace : https://localhost:3030 ; la page indique que l'usage de Model Runner avec Docker Agent y est marqué « en cours de développement »). À proposer en bonus.
9. **Lien avec A8** : l'agent du lab A8 sera exécuté dans un sandbox.

12. **Modèle aligné sur A5** : `ai/qwen3:1.7b` (1,1 Go) est utilisé partout, car `ai/qwen3` sans étiquette (8B, 5 Go) est trop lourd pour la classe, d'après l'exécution du lab A5. Ce choix n'a pas été testé avec Docker Agent.
