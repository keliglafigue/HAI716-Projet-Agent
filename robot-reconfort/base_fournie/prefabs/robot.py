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
    AVANCER_N = 0
    AVANCER_S = 1
    AVANCER_E = 2
    AVANCER_O = 3

    # Recherche dans le dictionnaire
    CONSULTER = 4

    # Déplacement du curseur dans l'armoire
    # TODO : chercher une manière d'encoder la stratégie de replis au sein de l'action
    CHERCHER_N = 5
    CHERCHER_S = 6
    CHERCHER_E = 7
    CHERCHER_O = 8

    # Récupère un objet de l'armoire au curseur
    PRENDRE = 9

    # Remet un objet dans l'armoire 
    DONNER = 10

    ATTENDRE = 11

class Robot:
    """
    Classe de l'agent
    """
    def __init__(self, largeur: int, hauteur: int, posArmoire: Pos, posDico: Pos):
        self.emotion = ("","")
        self.objet = ""
        self.carte = CarteRobot(largeur, hauteur)
        self.posArmoire = posArmoire
        self.posDico = posDico
        self.mission = None

    def isTacheEnCours(self) -> bool:
        return self.mission is not None

    def nouvelleDemande(self, requete:str, posRendu: Pos):
        self.mission = (requete, posRendu)

    def _aller_vers(self, percu:Perception, emplacement: Pos):
        if percu.posRobot == emplacement:
            # Peut être remplacer par
            # return Action.ATTENDRE
            raise "Erreur : Demande de déplacement alors qu'on est déjà présent"

        self.carte.calculerDistanceDepuis(emplacement)

        dir = self.carte.getNextMove(percu.posRobot)

        match dir:
            case None:
                raise "Erreur : Emplacement inaccessible"
            case Direction.N:
                return Action.AVANCER_N
            case Direction.S:
                return Action.AVANCER_S
            case Direction.E:
                return Action.AVANCER_E
            case Direction.O:
                return Action.AVANCER_O

    def _procedureEmotion(self, percu: Perception) -> Action:
        if percu.posRobot == self.posDico:
            return Action.CONSULTER
        else :
            return self._aller_vers(percu, self.posDico)

    def _procedureArmoire(self, percu: Perception) -> Action:
        if percu.posRobot == self.posArmoire:
            # TODO: implémenter la stratégie de déplacement au sein de l'armoire
            return Action.PRENDRE
        else:
            return self._aller_vers(percu, self.posArmoire)

    def _procedureResident(self, percu: Perception) -> Action:
        if percu.posRobot == self.mission[1]:
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
            self.carte.changerCase(percu.posRobot.getNord(), percu.celluleO)

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