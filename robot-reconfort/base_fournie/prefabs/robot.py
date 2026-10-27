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

    def __str__(self):
        return self.name

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
                tab.append("")
            self.armoire.append(tab)
        self.repli = 0 # Ré-initialisé à chaque nouvelle demande

        self.posArmoire = posArmoire
        self.posDico = posDico
        self.mission = None

    def isTacheEnCours(self) -> bool:
        return self.mission is not None

    def nouvelleDemande(self, requete:str, posRendu: Pos):
        self.mission = (requete, posRendu)
        self.repli = 0

    def _aller_vers(self, percu:Perception, emplacement: Pos):
        if percu.posRobot == emplacement:
            # Peut être remplacer par
            # return Action.ATTENDRE
            raise Exception("Erreur : Demande de déplacement alors qu'on est déjà présent")

        self.carte.calculerDistanceDepuis(emplacement)

        dir = self.carte.getNextMove(percu.posRobot)

        match dir:
            case None:
                raise Exception("Erreur : Emplacement inaccessible")
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


    # Il faut surement passer self.emotion plutot que percu.emotionRecupere
    def _procedureArmoire(self, percu: Perception) -> Action:
        if percu.posRobot.taxicabDistanceTo(self.posArmoire.x, self.posArmoire.y) == 1:
            # TODO: implémenter la stratégie de déplacement au sein de l'armoire
            case, objet = percu.caseArmoireRevele
            self.armoire[case.x][case.y] = objet
            goal = self._emotionToPos(self.emotion, self.repli)

            while self.repli < 15 and self.armoire[goal.x][goal.y] != "": # Itère dans l'armoire connu
                if self.armoire[goal.x][goal.y] != None:
                    if goal.equals(case) : return Action.PRENDRE
                    return self._deplacementArmoire(case, goal)
                self.repli += 1
                if self.repli < 15 : goal = self._emotionToPos(self.emotion, self.repli)

            if self.repli > 15 : return Action.ATTENDRE # TODO : A changer par un abandon
            
            return self._deplacementArmoire(case, goal)

        else:
            return self._aller_vers(percu, self.posArmoire)

    def _emotionToPos(self, emotion : tuple[str, str], repli:int) -> Pos:
        x = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"].index(emotion[0])
        y = ["faible", "moyenne", "forte"].index(emotion[1])

        if repli == 0 : pass

        elif repli <= 2: # On cherche les autres intensités de la même émotion
            y = self._replyY(y, repli)

        elif repli <= 5: # Casier 1 sup
            decal = 1
            x = (x + decal) % 8
            y = self._replyY(y, repli - 2)

        elif repli <= 8: # Casier 1 inf
            decal = 1
            x = (x - decal) % 8
            y = self._replyY(y, repli - 5)

        elif repli <= 11: # Casier sup 2
            decal = 2
            x = (x + decal) % 8
            y = self._replyY(y, repli - 5)

        else : # Casier inf 2
            decal = 2
            x = (x - decal) % 8
            y = self._replyY(y, repli - 11)

        
        return Pos(x, y)

    def _replyY(self, y:int, repli:int) -> int:
        if repli == 0: return y
        if y == 2 : return y - repli
        elif y == 0 : return y + repli
        else : return 0 if repli == 1 else 2

    def _deplacementArmoire(self, depart:Pos, target:Pos) -> Action:
        dx = (target.x - depart.x) % 8

        if dx != 0:
            if dx <= 4:
                return Action.CHERCHER_E
            return Action.CHERCHER_O

        if target.y < depart.y:
            return Action.CHERCHER_N
        return Action.CHERCHER_S

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

    def isObjetTenu(self) -> bool:
        return self.objet != ""

    def getCurrentRequest(self) -> str:
        return self.mission[0]

    def __str__(self):
        return str(self.carte)