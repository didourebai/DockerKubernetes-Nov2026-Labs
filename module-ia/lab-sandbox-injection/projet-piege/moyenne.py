"""Calcule la moyenne des notes données en arguments."""
import sys

notes = [float(n) for n in sys.argv[1:]]
if not notes:
    sys.exit("Usage : python moyenne.py NOTE [NOTE ...]")
print(f"Moyenne : {sum(notes) / len(notes):.2f}")
