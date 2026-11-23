#!/usr/bin/env bash
# SIMULATION PÉDAGOGIQUE d'un agent naïf : il lit README.md et exécute sans
# discernement l'instruction cachée qu'il y trouve. Ce n'est PAS une vraie IA.
# À exécuter uniquement dans un sandbox, comme indiqué dans le lab S6.
set -u
echo "[agent-naïf] Lecture de README.md pour comprendre le projet..."
instruction=$(sed -n 's/.*<!-- *INSTRUCTION-POUR-L-AGENT: *\(.*[^ ]\) *-->.*/\1/p' README.md)
if [ -z "$instruction" ]; then
  echo "[agent-naïf] Aucune instruction trouvée."
  exit 0
fi
echo "[agent-naïf] Instruction trouvée : $instruction"
echo "[agent-naïf] J'exécute..."
bash -c "$instruction"
echo "[agent-naïf] Code de sortie : $?"
