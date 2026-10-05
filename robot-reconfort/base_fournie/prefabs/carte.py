from enum import Enum
from typing import Any, Dict

class Cellule(Enum) :
    MUR = 0
    LIBRE = 1
    ARMOIRE = 2
    DICTIONNAIRE = 3
    RESIDENT = 4


class Carte:
    """
    La classe est initialisée à partir du chemin du fichier donnée, le vérifie (pas encore), et stocke la carte
    Elle permettra ensuite d'observer l'entourage d'une case.

    TODO : 
    - Rajouter des vérifications sur le format du json qui est lu
    - Implémenter la fonction observer
    - Que faire de la position de départ du robot, la stockée à part ? (pour l'instant elle est ignorée)
    """

    def __init__(self, base_carte: Dict[str, Any]):
        self.hauteur = 0
        self.largeur = 0
        self.carte = []

        self.hauteur = base_carte.get("dimensions").get("hauteur")
        self.largeur = base_carte.get("dimensions").get("largeur")

        legende = base_carte.get("legende")
        for string in base_carte.get("grille"):
            line = []
            for char in string:
                match legende.get(char):
                    case 'mur' : line.append(Cellule.MUR)
                    case 'libre' : line.append(Cellule.LIBRE)
                    case 'depart du robot' : line.append(Cellule.LIBRE) # A modifier
                    case 'armoire' : line.append(Cellule.ARMOIRE)
                    case 'dictionnaire' : line.append(Cellule.DICTIONNAIRE)
                    case 'resident' : line.append(Cellule.RESIDENT)
                    case _ : raise "Cellule inconnue dans la carte"
            self.carte.append(line)