# Notes formateur — Lab S4 (à valider avant la formation)

Sources : *Get started* (`sbx policy ls`, `sbx policy allow network registry.npmjs.org`, préréglages Balanced / Locked Down), référence CLI (sous-commandes `allow network`, `approval`, `check`, `deny network`, `init`, `inspect`, `log`, `ls`, `refresh`, `reset`, `rm network`). **Non exécuté.** À tester :

1. `sbx policy check DOMAINE` : arguments et format de sortie non documentés dans ce que j'ai pu lire.
2. Nom exact du préréglage Locked Down (`locked-down` ?) : `sbx policy init --help`.
3. `sbx policy reset` : confirmer qu'elle ne supprime pas autre chose que les règles réseau. **Ne pas la faire exécuter sur des postes avec une politique d'entreprise** (les administrateurs peuvent centraliser les politiques).
4. Reprise d'un sandbox : `sbx run --name lab-s4` (confirmé par la page *Usage*).
5. Domaines refusés/autorisés par Balanced : relever la réalité (example.org vs npmjs) et ajuster les étapes 2, 4 et 5 : si `example.org` passe d'emblée, utiliser un autre domaine ou commencer par `deny`.
6. Sous-commande `approval` : à explorer pour un éventuel lab avancé.
7. Les pages dédiées à la politique réseau de la doc n'ont pas été lues (page *Usage* bloquée) : les relire.
