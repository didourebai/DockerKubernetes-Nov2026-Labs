# Notes formateur — Lab A8 (à valider avant la formation)

Lab de synthèse construit sur les labs A5 (assistant IT-Support), S7 (agent en mode clone) et A2/A4 (Model Runner, MCP). **Lab non exécuté.** Les choix techniques reprennent les résultats de l'exécution du 21/11/2026 des labs A1 à A6 (modèle `ai/qwen3:1.7b`, passerelle `docker/mcp-gateway:v0.44.3`, réponses lentes sur processeur et parfois fausses).

À valider :
1. **Durée** : sur processeur seul, trois questions au modèle (1, 1 et 2 à 3 minutes) plus le travail de l'agent : 75 minutes est une estimation, probablement serrée. Option : supprimer le test de l'outil `search` (étape 6) ou l'étape 7.
2. **Panne de la passerelle (étape 2)** : vérifier que l'erreur actuelle est bien affichée avant l'appel au modèle (la connexion à la passerelle échoue avant). Relever le texte exact pour le citer en séance. `docker compose stop mcp-gateway` : l'application reste démarrée (`depends_on` ne contrôle que le démarrage).
3. **Consigne à l'agent** : tester qu'il comprend « réponds quand même avec le modèle seul » ; relever le code produit (gestion d'exception autour de la connexion MCP). Le comportement attendu : message clair puis appel du modèle **sans** liste d'outils.
4. **Agent et Model Runner** : l'agent ne peut pas joindre Model Runner depuis le sandbox (moteur Docker privé) ; à confirmer, ainsi que le comportement réseau (politique Balanced/Locked Down) pour l'installation de paquets (`pip install`) pendant le build de l'image.
5. **Nom du conteneur** : `assistant-agent-assistant-1` suppose un dossier `assistant-agent` et Compose v2 ; sinon adapter (`docker compose ps`).
6. **Ports** : 8090 (et 8091 non utilisé ici) libres ; arrêter les stacks A5 / A6 avant.
7. **Étape 7 (second regard)** : `docker model run MODELE "texte"` avec un diff en argument ; sous PowerShell, la taille et les guillemets du diff peuvent poser problème. Si le diff est trop long, limiter à `app/app.py`. Résultat attendu : résumé approximatif, c'est le but pédagogique.
8. **Accès à Claude Code** : même prérequis que S7 (compte ou clé) ; prévoir une alternative si absent.
9. **Sommaire du module IA** : le lien final suppose un `module-ia/README.md` qui n'existe pas encore ; à créer ou retirer.
10. **Variante** : faire passer le lab en mode `--cloud` (labs S9) n'est pas prévu ici.
