from enum import Enum
from typing import Any, Dict
from prefabs.utils import Pos, File, Direction

class Cellule(Enum) :
    MUR = "mur"
    LIBRE = "libre"
    ARMOIRE = "armoire"
    DICTIONNAIRE = "dictionnaire"
    RESIDENT = "resident"


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
        self.nom = base_carte.get("nom")

        yPosArmoire, xPosArmoire = base_carte.get("armoire").get("position")
        self.posArmoire = Pos(xPosArmoire, yPosArmoire)

        yPosDico, xPosDico = base_carte.get("dictionnaire").get("position")
        self.posDisco = Pos(xPosDico, yPosDico)

        yPosDepart, xPosDepart = base_carte.get("depart_robot")
        self.posDepartRobot = Pos(xPosDepart, yPosDepart)

        legende = base_carte.get("legende")
        for string in base_carte.get("grille"):
            line = []
            for char in string:
                match legende.get(char):
                    case 'mur' : line.append(Cellule.MUR)
                    case 'libre' : line.append(Cellule.LIBRE)
                    case 'depart du robot' : line.append(Cellule.LIBRE) # A modifier # Pourquoi ?
                    case 'armoire' : line.append(Cellule.ARMOIRE)
                    case 'dictionnaire' : line.append(Cellule.DICTIONNAIRE)
                    case 'resident' : line.append(Cellule.RESIDENT)
                    case _ : raise Exception("Cellule inconnue dans la carte")
            self.carte.append(line)
        
        self.residents = {}
        for resident in base_carte.get("residents"):
            self.residents[resident.get("id")] = (resident.get("nom"), Pos(resident.get("position")[1], resident.get("position")[0]))

    def getHauteur(self):
        return self.hauteur

    def getLargeur(self):
        return self.largeur

    # On s'assure de renvoyer une copie et non une référence
    # Ce serait couillon que les meubles puissent se déplacer
    def getPosArmoire(self):
        return self.posArmoire.copy()

    def getPosDico(self):
        return self.posDisco.copy()

    def getPosDepartRobot(self):
        return self.posDepartRobot.copy()

    def getPosResident(self, id: str):
        return self.residents.get(id)[1].copy()

    def inBound(self, coord: Pos) -> bool:
        return 0 <= coord.x and coord.x < self.largeur and 0 <= coord.y and coord.y < self.hauteur

    def getNeigboringCells(self, emplacement:Pos) -> tuple[(None | Cellule), (None | Cellule), (None | Cellule), (None | Cellule)]:
        voisins = [
            emplacement.getEst(),
            emplacement.getNord(),
            emplacement.getOuest(),
            emplacement.getSud()
        ]

        res = []

        for voisin in voisins:
            if self.inBound(voisin):
                res.append(self.carte[voisin.y][voisin.x])
            else:
                res.append(None)

        return tuple(res)

    def getCellule(self, pos: Pos) -> Cellule:
        if self.inBound(pos):
            return self.carte[pos.y][pos.x]
        else:
            raise AttributeError("Erreur : la case demandé est hors des limites de la grille")

    def __str__(self):
        res = ""
        for y in range(self.hauteur):
            for x in range(self.largeur):
                res += self.carte[y][x].value
            res += "\n"
        return res

    def getEquipe(self):
        return [self.residents[k][0] for k in self.residents]

class Case:
    """
    Représentation d'une case du monde pour la carte du robot
    """
    def __init__(self):
        self.type = Cellule.LIBRE
        self.distance = float('inf')
        self.estParcouru = False

    def changerType(self, nouveauType: Cellule):
        self.type = nouveauType

    def marquer(self):
        if self.estParcouru: 
            raise Exception("Erreur: Marquage d'une case déjà marqué")
        self.estParcouru = True

    def reinitialiser(self):
        self.estParcouru = False
        self.distance = float('inf')

    def setDistance(self, n: int):
        if n < 0:
            raise Exception("Erreur: distance négative affecté à une case")
        self.distance = n

    def __str__(self):
        return self.type.value

class CarteRobot:
    """
    Représentation du monde tel que connu par le robot.
    """
    def __init__(self, largeur: int, hauteur: int) -> None:
        self.hauteur = hauteur
        self.largeur = largeur
        # Obliger de faire ça plutôt que * pour éviter d'avoir tout le temps la même référence
        self.carte = [[Case() for _ in range(largeur)] for _ in range(hauteur)]

    def reinitialiserCase(self) -> None:
        for ligne in self.carte:
            for case in ligne:
                case.reinitialiser()

    def inBound(self, emplacement: Pos) -> None:
        return (emplacement.x >= 0 and emplacement.x < self.largeur
                and emplacement.y >= 0 and emplacement.y < self.hauteur)

    def changerCase(self, emplacement: Pos, type: Cellule) -> None:
        if not (self.inBound(emplacement)):
            raise Exception("Erreur : Position en dehors de la carte")
        case = self.carte[emplacement.y][emplacement.x]
        case.changerType(type)
        if type is Cellule.MUR:
            case.setDistance(float('inf'))

    def calculerDistanceDepuis(self, objectif: Pos) -> None:
        # TODO : Rajouter des attributs pour actualiser les distances seulement si nécessaire
        self.reinitialiserCase()

        if not (self.inBound(objectif)):
            return

        caseInit = self.carte[objectif.y][objectif.x]

        file = File((objectif, 0))
        caseInit.marquer()

        # En fait faut peut être que le robot soit SUR la case étagère pour y accéder
        # types_obstacles = (Cellule.MUR,)
        # En fait non 
        types_obstacles = (Cellule.MUR, Cellule.ARMOIRE, Cellule.DICTIONNAIRE, Cellule.RESIDENT)

        while not file.isEmpty():
            posCourant, distCourant = file.pop()
            self.carte[posCourant.y][posCourant.x].setDistance(distCourant)

            voisins = [
                posCourant.getNord(),
                posCourant.getSud(),
                posCourant.getEst(),
                posCourant.getOuest()
            ]

            for p in voisins:
                if self.inBound(p):
                    caseVoisine = self.carte[p.y][p.x]
                    if caseVoisine.type not in types_obstacles and not caseVoisine.estParcouru:
                        caseVoisine.marquer()
                        file.add((p, distCourant + 1))

    def getNextMove(self, depuis: Pos) -> (Direction | None):
        voisins = [
            (depuis.getNord(), Direction.N),
            (depuis.getSud(), Direction.S),
            (depuis.getOuest(), Direction.O),
            (depuis.getEst(), Direction.E)
        ]
        actuel = self.carte[depuis.y][depuis.x]
        meilleur = None

        for (pos, dir) in voisins:
            if not self.inBound(pos):
                continue
            case = self.carte[pos.y][pos.x]
            if meilleur is None or case.distance < meilleur[1]:
                meilleur = (dir, case.distance)

        return meilleur[0] if meilleur is not None and meilleur[1] < actuel.distance else None

    def __str__(self):
        res = ""
        for y in range(self.hauteur):
            for x in range(self.largeur):
                res += str(self.carte[y][x])
            res += '\n'
        return res