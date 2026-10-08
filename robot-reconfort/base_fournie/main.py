#!/usr/bin/env python3
"""
Rendu de projet - Le Robot de Réconfort

Binome :
- RATHGEBER-KIVITS Éloi
- SOARES--QUEBRIAC Kélig
M1 Imagine

Pour lancer le programme, utiliser la commande suivante :
python3 main.py cartes/appartement_01.json cartes/scenario_01.json \
        donnees sorties/trace_01.json
"""

import sys
from pathlib import Path
import reconfort_io as rio
from prefabs.monde import Monde

def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(__doc__.strip())
        return 2
    
    chemin_carte, chemin_scenario = Path(argv[1]), Path(argv[2])
    dossier_donnees, chemin_sortie = Path(argv[3]), Path(argv[4])
    
    try:
        carte = rio.charger_carte(chemin_carte)
        # TODO : vérifier si les noms des cartes et armoire correspondent à ceux dans le scénario
        scenario = rio.charger_scenario(chemin_scenario)
        dictionnaire = rio.charger_dictionnaire(dossier_donnees / "dictionnaire.json")
        armoire = rio.charger_armoire(dossier_donnees / f"{scenario['armoire']}.json")
    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1
    except rio.ErreurCarte as err:
        print(f"erreur dans le fichier '{chemin_carte}' : {err}", file=sys.stderr)
        return 1
    except rio.ErreurScenario as err:
        print(f"erreur dans le fichier '{chemin_scenario}' : {err}", file=sys.stderr)
        return 1
    except rio.ErreurDico as err:
        print(f"erreur dans le fichier '{dossier_donnees / "dictionnaire.json"}' : {err}", file=sys.stderr)
        return 1
    except rio.ErreurArmoire as err:
        print(f"erreur dans le fichier '{dossier_donnees / f"{scenario['armoire']}.json"}' : {err}", file=sys.stderr)
        return 1

    monde = Monde(carte, dictionnaire, armoire)

    for demande in scenario["demandes"]:
        # Mettre dans un try plus tard pour une gestion propre des erreurs
        monde.executer_requete(demande)
        print("Demande numéro", demande["numero"],"effectuée")
        pass
 
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
