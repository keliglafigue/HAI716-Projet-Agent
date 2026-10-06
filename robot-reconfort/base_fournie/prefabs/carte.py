from enum import Enum
from typing import Any, Dict
from prefabs.utils import Pos, File

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


class Case:
    """
    Représentation d'une case du monde pour la carte du robot
    """
    def __init__(self):
        self.type = Cellule.LIBRE
        self.distance = -1
        self.estParcouru = False

    def changerType(self, nouveauType: Cellule):
        self.type = nouveauType

    def marquer(self):
        if self.estParcouru: 
            raise "Erreur: Marquage d'une case déjà marqué"
        self.estParcouru = True

    def reinitialiser(self):
        self.estParcouru = False

    def setDistance(self, n: int):
        if n < 0:
            raise "Erreur: distance négative affecté à une case"
        self.distance = n


class CarteRobot:
    """
    Représentation du monde tel que connu par le robot.
    """
    def __init__(self, largeur: int, hauteur: int) -> None:
        self.hauteur = hauteur
        self.largeur = largeur
        # Obliger de faire ça plutôt que * pour éviter d'avoir tout le temps la même référence
        self.carte = [[Case() for _ in range(largeur)] for _ in range(hauteur)] 

    def reinitialiserMarquage(self):
        for ligne in self.carte:
            for case in ligne:
                case.reinitialiser()

    def calculerDistanceDepuis(self, objectif: Pos) -> None:
        self.reinitialiserMarquage()

        if not (0 <= objectif.x and objectif.x < self.largeur and 0 <= objectif.y and objectif.y < self.hauteur):
            return

        caseInit = self.carte[objectif.y][objectif.x]

        file = File((objectif, 0))
        caseInit.marquer()

        types_obstacles = (Cellule.MUR, Cellule.ARMOIRE, Cellule.DICTIONNAIRE)

        while not file.isEmpty():
            posCourant, distCourant = file.pop()
            self.carte[posCourant.y][posCourant.x].setDistance(distCourant)

            voisins = [
                posCourant.moveUp(),
                posCourant.moveDown(),
                posCourant.moveLeft(),
                posCourant.moveRight()
            ]

            for p in voisins:
                if 0 <= p.x < self.largeur and 0 <= p.y < self.hauteur:
                    caseVoisine = self.carte[p.y][p.x]
                    if caseVoisine.type not in types_obstacles and not caseVoisine.estParcouru:
                        caseVoisine.marquer()
                        file.add((p, distCourant + 1))