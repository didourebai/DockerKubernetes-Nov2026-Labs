# Notes formateur — Lab A6 (à valider avant la formation)

> Exécution du 21/11/2026 : `up -d` en 110 s ; modèle `ai/llama3.2:3B-Q4_K_M` (1,9 Go) ; 7 services (configurator s'arrête après la préparation), proxy du socket `mikesir87/docker-socket-proxy`. Interface http://localhost:3030 : HTTP 200. Parcours des 7 modules **non suivi** (interface web). `down` laisse 5 volumes : `down -v` recommandé dans la fiche.

Sources : page « Lab: Building Agentic Apps with Docker » (docs.docker.com/guides/lab-agentic-apps), dépôt dockersamples/labspace-agentic-apps-with-docker, pages Docker Hub des Labspaces. **Lab non exécuté.** Le contenu des modules appartient au Labspace officiel : ce lab ne le reproduit pas, il l'encadre.

Faits repris de la documentation :
- commande : `docker compose -p labspace -f oci://dockersamples/labspace-agentic-apps-with-docker up -d`, interface sur http://localhost:3030, arrêt par `docker compose -p labspace down`
- 7 modules : Introduction, Understanding Model Interactions, The Docker Model Runner, Understanding Tools and MCP, The Docker MCP Gateway, Putting It All Together, Conclusion
- la page indique que le lancement peut prendre quelques minutes (téléchargement d'un modèle) ; elle ne donne ni prérequis ni durée (la durée de 60 minutes est une estimation à ajuster)

À valider :
1. **Compose OCI** : la commande exige une version de Docker Compose qui accepte `-f oci://…` ; vérifier sur les postes.
2. **Réseau** : accès à Docker Hub depuis le réseau de formation (téléchargement du Labspace, des images et du modèle). Prévoir un téléchargement préalable (`up -d` la veille) si le débit est faible.
3. **Port 3030** libre ; **mémoire** suffisante pour le modèle du Labspace (relever lequel dans `docker model list`).
4. **Conflit avec A5** : arrêter l'assistant du lab A5 avant (`docker compose down`) pour libérer la mémoire.
5. **Tableau de l'étape 3** : le nombre et les rôles des conteneurs sont à relever en séance (non vérifiés) ; la présence d'un proxy du socket Docker vient des fichiers Compose publiés des Labspaces.
6. **Correspondance des modules** (étape 4) : établie d'après les titres ; confirmer le contenu réel de chaque module.
7. **Version du Labspace** : le contenu évolue (Docker Hub indique des mises à jour récentes) ; refaire une passe juste avant la formation.
8. **Labspaces voisins** (hors périmètre mais possibles en bonus) : labspace-docker-agent (voir A7), labspace-devduck, labspace-compose-quickstart.
