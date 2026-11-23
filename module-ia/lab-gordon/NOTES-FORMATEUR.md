# Notes formateur — Lab A1 (à valider avant la formation)

> Exécution du 21/11/2026 : panne reproduite (code 2, message `can't open file '/app/main.py'`), correction et `docker buildx build --check` sans avertissement : OK. `docker ai version` répond `v1.33.0` même quand Gordon est désactivé ; `docker ai "…"` renvoie alors `The "Docker AI" feature needs to be enabled in Docker Desktop settings` (étape 1 corrigée). Les étapes avec Gordon (4, 6, 7, 8) restent à jouer avec Gordon activé. `Copy-Item -Recurse` vers `C:\Labs\…` fonctionne même si `C:\Labs` n'existe pas ; sur Mac, `mkdir -p ~/labs` ajouté.

Sources : diapo 130 ; documentation Docker sur Gordon (page d'accueil, « Using Gordon via CLI », « Use cases ») trouvée par recherche web ; **les pages n'ont pas été lues en entier et le lab n'a pas été exécuté**.

À valider :
1. **Version minimale :** la page « CLI » indique Docker Desktop 4.74.0 ou plus pour `docker ai` ; un billet de blog mentionne 4.61. Vérifier sur le poste cible avec `docker ai version`.
2. **Activation :** la documentation consultée désigne deux libellés différents pour le réglage (section *AI* ou *Beta features*) : vérifier dans les paramètres de Docker Desktop de la version installée.
3. **Limites d'utilisation :** l'usage de Desktop et de la CLI compte dans les limites du plan : prévoir un compte de démonstration pour la classe.
4. **Interface interactive :** raccourcis de l'écran d'approbation non documentés ici : les relever à l'exécution et compléter l'étape 4.
5. **Réponse variable :** Gordon peut proposer des commandes différentes (`docker logs`, `docker inspect`…) ; la panne (`main.py` absent, code de sortie 2) doit être diagnostiquée dans tous les cas. Vérifier le message exact (« can't open file '/app/main.py' »).
6. **Demande en français :** `docker ai "pourquoi mon conteneur …"` : vérifier la langue de la réponse ; les exemples de la documentation sont en anglais.
7. **Étape 7 :** la consigne est de **refuser** l'action : ne jamais l'approuver sur un poste de stagiaire avec des volumes importants.
8. **Confidentialité :** Gordon lit le dossier de travail depuis lequel il est lancé ; insister sur le dossier du lab.
