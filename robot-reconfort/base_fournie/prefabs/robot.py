from typing import List
from prefabs.utils import Pos
from prefabs.carte import CarteRobot, Cellule, Direction
from enum import Enum

class Perception:
    """
    Classe contenant les données perçu par le robot avant de prendre sa décision
    Les cases révelés doivent suivre cette ordre : Est (0), Nord (1), Ouest (2), Sud (3)
    """
    def __init__(
            self, 
            position: Pos, 
            celluleCarteRevele: tuple[(None | Cellule), (None | Cellule), (None | Cellule), (None | Cellule)],
            caseArmoireRevele: None | tuple[Pos, str] = None,  # La position de la case révélé ainsi que son contenu
            emotionRecupere: None | tuple[str, str] = None
    ):
        self.posRobot = position
        self.celluleE = celluleCarteRevele[0]
        self.celluleN = celluleCarteRevele[1]
        self.celluleO = celluleCarteRevele[2]
        self.celluleS = celluleCarteRevele[3]
        self.caseArmoireRevele = caseArmoireRevele
        self.emotionRecupere = emotionRecupere

class Action(Enum):
    # Déplacement sur le plan
    AVANCER_N = ("AVANCER", "N")
    AVANCER_S = ("AVANCER", "S")
    AVANCER_E = ("AVANCER", "E")
    AVANCER_O = ("AVANCER", "O")

    # Recherche dans le dictionnaire
    CONSULTER = ("CONSULTER", None)

    # Déplacement du curseur dans l'armoire
    CHERCHER_N = ("CHERCHER", "N")
    CHERCHER_S = ("CHERCHER", "S")
    CHERCHER_E = ("CHERCHER", "E")
    CHERCHER_O = ("CHERCHER", "O")

    # Récupère un objet de l'armoire au curseur
    PRENDRE = ("PRENDRE", None)

    # Remet un objet dans l'armoire 
    DONNER = ("DONNER", None)

    ATTENDRE = ("ATTENDRE", None)

    def __str__(self):
        return self.name

class Repli(Enum):
    AUCUN = "aucun"
    INTENSITE = "intensite"
    VOISINE_1 = "voisine_1"
    VOISINE_2 = "voisine_2"

class Robot:
    """
    Classe de l'agent
    """
    def __init__(self, largeur: int, hauteur: int, posArmoire: Pos, posDico: Pos):
        self.emotion = ("","")
        self.objet = ""
        self.carte = CarteRobot(largeur, hauteur)

        # Initialisation de la mémoire de l'armoire
        self.armoire = []
        for i in range(8):
            tab = []
            for i in range(3):
                tab.append(None)
            self.armoire.append(tab)
        self.repli = Repli.AUCUN

        self.posArmoire = posArmoire
        self.posDico = posDico
        self.mission = None

    def isTacheEnCours(self) -> bool:
        return self.mission is not None

    def nouvelleDemande(self, requete:str, posRendu: Pos, idResident: str, numRequete: int):
        self.mission = (requete, posRendu, idResident, numRequete)

    def _aller_vers(self, percu:Perception, emplacement: Pos):
        if percu.posRobot == emplacement:
            # Peut être remplacer par
            # return Action.ATTENDRE
            raise Exception("Erreur : Demande de déplacement alors qu'on est déjà présent")

        self.carte.calculerDistanceDepuis(emplacement)

        dir = self.carte.getNextMove(percu.posRobot)

        match dir:
            case None:
                raise Exception("resident/emplacement inaccessible")
            case Direction.N:
                return Action.AVANCER_N
            case Direction.S:
                return Action.AVANCER_S
            case Direction.E:
                return Action.AVANCER_E
            case Direction.O:
                return Action.AVANCER_O

    def _procedureEmotion(self, percu: Perception) -> Action:
        if percu.posRobot.taxicabDistanceTo(self.posDico.x, self.posDico.y) == 1:
            return Action.CONSULTER
        else :
            return self._aller_vers(percu, self.posDico)

    def _deplacementArmoire(self, depart:Pos, target:Pos) -> Action:
        dx = (target.x - depart.x) % 8

        if dx != 0:
            if dx <= 4:
                return Action.CHERCHER_E
            return Action.CHERCHER_O

        if target.y < depart.y:
            return Action.CHERCHER_N
        return Action.CHERCHER_S

    def _emotionToPos(self, emotion : tuple[str, str]) -> Pos:
        x = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"].index(emotion[0])
        y = ["faible", "moyenne", "forte"].index(emotion[1])
        return Pos(x, y)

    def _updateRepli(self):
        bestCase = self._emotionToPos(self.emotion)
        if self.repli == Repli.AUCUN:
            if self.armoire[bestCase.x][bestCase.y] != "": return
            self.repli = Repli.INTENSITE

        if self.repli == Repli.INTENSITE:
            posToCheck = [Pos(bestCase.x, y) for y in range(3) if y!=bestCase.y]
            if any(self.armoire[p.x][p.y] != "" for p in posToCheck): return
            self.repli = Repli.VOISINE_1

        if self.repli == Repli.VOISINE_1:
            posToCheck = [Pos((bestCase.x + x) % 8, y) for x in (1, -1) for y in range(3)]
            if any(self.armoire[p.x][p.y] != "" for p in posToCheck): return
            self.repli = Repli.VOISINE_2

        if self.repli == Repli.VOISINE_2:
            posToCheck = [Pos((bestCase.x + x) % 8, y) for x in (2, -2) for y in range(3)]
            if any(self.armoire[p.x][p.y] != "" for p in posToCheck): return
        raise Exception("armoire vide")

    def _getGoal(self) -> Pos:
        candidats = []
        bestCase = self._emotionToPos(self.emotion)
        orderedY = sorted(range(3), key=lambda y: (abs(y - bestCase.y), y))
        match self.repli:
            case Repli.AUCUN:
                return bestCase
            case Repli.INTENSITE:
                candidats = [
                    Pos(bestCase.x, y) 
                    for y in orderedY
                    # if y != bestCase.y and self.armoire[bestCase.x][y] != ""
                ]
            case Repli.VOISINE_1:
                candidats = [
                    Pos((bestCase.x + x) % 8, y) 
                    for x in (1, -1) 
                    for y in orderedY
                    # if self.armoire[(bestCase.x + x) % 8][y] != ""
                ]
            case Repli.VOISINE_2:
                candidats = [
                    Pos((bestCase.x + x) % 8, y) 
                    for x in (2, -2) 
                    for y in orderedY
                    # if self.armoire[(bestCase.x + x) % 8][y] != ""
                ]

        for pos in candidats:
            if self.armoire[pos.x][pos.y] != "":
                return pos
            
        raise Exception("armoire vide")

    def _procedureArmoire(self, percu: Perception) -> Action:
        if percu.posRobot.taxicabDistanceTo(self.posArmoire.x, self.posArmoire.y) == 1:
            case, objet = percu.caseArmoireRevele
            self.armoire[case.x][case.y] = objet
            self._updateRepli()
            goal = self._getGoal()

            if case == goal: return Action.PRENDRE
            return self._deplacementArmoire(case, goal)

        else:
            return self._aller_vers(percu, self.posArmoire)

    def _procedureResident(self, percu: Perception) -> Action:
        if percu.posRobot.taxicabDistanceTo(self.mission[1].x, self.mission[1].y) == 1 :
            return Action.DONNER
        else:
            return self._aller_vers(percu, self.mission[1])

    def _updateAttribut(self, percu: Perception) -> None:
        # Maj de la carte
        if percu.celluleN is not None:
            self.carte.changerCase(percu.posRobot.getNord(), percu.celluleN)

        if percu.celluleS is not None:
            self.carte.changerCase(percu.posRobot.getSud(), percu.celluleS)

        if percu.celluleE is not None:
            self.carte.changerCase(percu.posRobot.getEst(), percu.celluleE)

        if percu.celluleO is not None:
            self.carte.changerCase(percu.posRobot.getOuest(), percu.celluleO)

        if percu.emotionRecupere is not None:
            self.emotion = percu.emotionRecupere

        # gérer le cas de l'armoire derrière
        # if percu.caseArmoireRevele is not None:

    def executerPas(self, percu: Perception) -> Action:
        self._updateAttribut(percu)

        # Tout les champs de emotion doivent être rempli
        isEmotionConnu = all(elt != "" for elt in self.emotion)
        isObjetConfortTenu = self.objet != ""

        match (isEmotionConnu, isObjetConfortTenu):
            case (False, _):
                return self._procedureEmotion(percu)
            case (_, False):
                return self._procedureArmoire(percu)
            case (True, True):
                return self._procedureResident(percu)

    def reset(self):
        self.mission = None
        self.emotion = ("", "")
        self.objet = ""
        self.repli = Repli.AUCUN

    def isObjetTenu(self) -> bool:
        return self.objet != ""

    def getCurrentRequest(self) -> str:
        if self.isTacheEnCours():
            return self.mission[0]
        else:
            raise Exception("Erreur : Aucune requête en cours pour le robot")

    def getWhoMadeRequest(self):
        if self.isTacheEnCours():
            return self.mission[2]
        else:
            raise Exception("Erreur : Aucune requête en cours pour le robot")

    def __str__(self):
        return str(self.carte)

    def get_repli(self):
        return self.repli

    def getRequeteNum(self):
        if self.isTacheEnCours():
            return self.mission[3]
        raise Exception("Erreur : Aucune requête en cours pour le robot")