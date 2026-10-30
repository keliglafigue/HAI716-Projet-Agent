from typing import Any, Dict, List

from prefabs.utils import Pos, Direction
from prefabs.robot import Robot, Perception, Action
from prefabs.dictionnaire import Dictionnaire
from prefabs.carte import Carte, Cellule
from prefabs.armoire import Armoire
from reconfort_io import Trace

class Monde:

    def __init__(self, carte:Dict[str, Any], dico:Dict[str, Any], armoire:Dict[str, Any], nom_scenar, out_file):
        self.carte = Carte(carte)
        self.dico = Dictionnaire(dico)
        self.armoire = Armoire(armoire)
        print(self.armoire.contenu.mat)
        self.pos_robot = self.carte.getPosDepartRobot()
        self.robot = Robot(self.carte.getLargeur(), self.carte.getHauteur(), self.carte.getPosArmoire(), self.carte.getPosDico())
        self.percu = self.initPerception()
        self.nextPercu = self.initPerception()
        self.logger = Trace(self.carte.nom, nom_scenar, self.carte.getEquipe())
        self.out_file = out_file
        
    def initPerception(self) -> Perception:
        return Perception(
            self.pos_robot.copy(),
            self.carte.getNeigboringCells(self.pos_robot)
        )

    def _extraire_direction(self, action: Action) -> Direction:
        match action:
            case Action.AVANCER_N | Action.CHERCHER_N:
                return Direction.N
            case Action.AVANCER_S | Action.CHERCHER_S:
                return Direction.S
            case Action.AVANCER_E | Action.CHERCHER_E:
                return Direction.E
            case Action.AVANCER_O | Action.CHERCHER_O:
                return Direction.O
            case _:
                raise AttributeError("Erreur : Une action dépourvu de direction a été transmis")

    def _valider_avancer(self, dir: Direction) -> bool:
        pos = self.pos_robot.copy()
        match dir:
            case Direction.N:
                pos = pos.getNord()
            case Direction.S:
                pos = pos.getSud()
            case Direction.E:
                pos = pos.getEst()
            case Direction.O:
                pos = pos.getOuest()

        case = self.carte.getCellule(pos)
        if case != Cellule.LIBRE:
            raise Exception("Erreur : Tentative de déplacement sur une cellule non libre")

        return True

    def _valider_chercher(self, dir: Direction) -> bool:
        # A côté de l'armoire
        pos_rob = self.pos_robot.copy()
        pos_armoire = self.carte.getPosArmoire()
        if pos_rob.taxicabDistanceTo(pos_armoire.x, pos_armoire.y) != 1:
            raise Exception("Erreur : Le robot n'est pas à côté de l'armoire")
            # return False
        # On "cycle" sur la largeur
        if dir in (Direction.E, Direction.O):
            return True
        # Mais pas sur la hauteur
        if dir == Direction.N and self.armoire.getPosSelecteur().y == 0:
            raise Exception("Erreur : le curseur est déjà tout en haut")
        if dir == Direction.S and self.armoire.getPosSelecteur().y == 2:
            raise Exception("Erreur : le curseur est déjà tout en bas")
        return True

    def _valider_consulter(self) -> bool:
        pos_rob = self.pos_robot.copy()
        pos_dico = self.carte.getPosDico()
        return pos_rob.taxicabDistanceTo(pos_dico.x, pos_dico.y) == 1

    def _valider_prendre(self) -> bool:
        pos_rob = self.pos_robot.copy()
        pos_armoire = self.carte.getPosArmoire()
        if pos_rob.taxicabDistanceTo(pos_armoire.x, pos_armoire.y) != 1:
            raise Exception("Erreur : le robot n'est pas à côté de l'armoire")
            # return False
        if self.robot.isObjetTenu():
            raise Exception("Erreur : le robot tient déjà un objet")
            # return False
        if self.armoire.regarderObjet() == "":
            raise Exception("Erreur : la case ne contient pas d'objet")
            # return False
        return True

    def _valider_donner(self):
        if not self.robot.isObjetTenu():
            raise Exception("Erreur : le robot ne tient aucun objet")
        idRes = self.robot.getWhoMadeRequest()
        posRes = self.carte.getPosResident(idRes)
        if self.pos_robot.taxicabDistanceTo(posRes.x, posRes.y) != 1:
            raise Exception("Erreur : le robot n'est pas à côté du bon résident")
        return True

    def valider_action(self, action: Action) -> bool:
        match action:
            case Action.ATTENDRE:
                return True
            case Action.AVANCER_N | Action.AVANCER_S | Action.AVANCER_E | Action.AVANCER_O:
                dir = self._extraire_direction(action)
                return self._valider_avancer(dir)
            case Action.CHERCHER_N | Action.CHERCHER_S | Action.CHERCHER_E | Action.CHERCHER_O:
                dir = self._extraire_direction(action)
                return self._valider_chercher(dir)
            case Action.CONSULTER:
                return self._valider_consulter()
            case Action.PRENDRE:
                return self._valider_prendre()
            case Action.DONNER:
                return self._valider_donner()

    def executer_action(self, action: Action) -> None:
        match action:
            case Action.ATTENDRE:
                RequestId = self.robot.getRequeteNum()
            case Action.AVANCER_N | Action.AVANCER_S | Action.AVANCER_E | Action.AVANCER_O:
                dir = self._extraire_direction(action)
                self.pos_robot.move(dir)
            case Action.CHERCHER_N | Action.CHERCHER_S | Action.CHERCHER_E | Action.CHERCHER_O:
                dir = self._extraire_direction(action)
                self.armoire.deplacerSelecteur(dir)
            case Action.CONSULTER:
                req = self.robot.getCurrentRequest()
                emotion = self.dico.recuperEmotion(req)
                self.nextPercu.emotionRecupere = emotion
            case Action.PRENDRE:
                self.robot.objet = self.armoire.obtenirObjet()
            case Action.DONNER:
                self.robot.reset()

    def update_perception(self):
        pos_arm = self.carte.getPosArmoire()
        if self.pos_robot.taxicabDistanceTo(pos_arm.x, pos_arm.y) == 1:
            self.nextPercu.caseArmoireRevele = (self.armoire.getPosSelecteur(), self.armoire.regarderObjet())
        self.percu = Perception(
            self.pos_robot.copy(),
            self.carte.getNeigboringCells(self.pos_robot),
            self.nextPercu.caseArmoireRevele,
            self.nextPercu.emotionRecupere
        )
        self.nextPercu = self.initPerception()

    def ecrire_pas(self, action: Action, percu: Perception):
        requestId = self.robot.getRequeteNum()
        dicoPos = {
            "N": percu.celluleN.value,
            "S": percu.celluleS.value,
            "E": percu.celluleE.value,
            "O": percu.celluleO.value
        }
        posArmoire = self.carte.getPosArmoire()
        contenuCasier = self.armoire.regarderObjet() if self.pos_robot.taxicabDistanceTo(posArmoire.x, posArmoire.y) == 1 else None
        self.logger.ajouter_pas(requestId, self.pos_robot, self.armoire.getPosSelecteur(), action.value[0], action.value[1], dicoPos, contenuCasier)

        if action == Action.DONNER:
            self.logger.ajouter_livraison(
                self.robot.getRequeteNum(), 
                self.robot.getWhoMadeRequest(), 
                self.robot.emotion[0],
                self.robot.emotion[1],
                self.armoire.getPosSelecteur(),
                self.robot.get_repli().value,
                self.robot.objet,
                True
            )

    def executer_requete(self, requete: Dict[str, Any]) -> None:
        if self.robot.isTacheEnCours():
            raise Exception("Erreur : Une requête est déjà en cours d'exécution sur ce robot")

        message = requete.get("message")
        posResident = self.carte.getPosResident(requete.get("resident"))
        self.robot.nouvelleDemande(message, posResident, requete.get("resident"), requete.get("numero"))

        while self.robot.isTacheEnCours():
            print(self)
            try:
                action = self.robot.executerPas(self.percu) # Les paramètres nécessaire à l'exécution seront passés en paramètre
                if self.valider_action(action):
                    self.ecrire_pas(action, self.percu)
                    self.executer_action(action)
                    
            except Exception as e:
                message = str(e)
                self.logger.ajouter_livraison(
                    self.robot.getRequeteNum(), 
                    self.robot.getWhoMadeRequest(), 
                    self.robot.emotion[0],
                    self.robot.emotion[1],
                    self.armoire.getPosSelecteur() if self.robot.objet != "" else None,
                    self.robot.get_repli().value,
                    self.robot.objet if self.robot.objet != "" else None,
                    False,
                    message
                )
                self.robot.reset()

            self.update_perception()

    def __str__(self):
        barre = "----------\n"
        carte = str(self.carte)
        pos = self.pos_robot.y * (self.carte.getLargeur() + 1) + self.pos_robot.x

        carte = carte[:pos] + "@" + carte[pos+1:]

        carte += "\nPos robot : " + str(self.pos_robot)
        carte += "\nCurseur Armoire : " + str(self.armoire.getPosSelecteur())
        carte += "\nStratégie de repli : " + self.robot.get_repli().value
        carte += "\nObjet tenu : " + str(self.robot.objet)
        carte += "\nMission actuel : " + str(self.robot.mission)

        return barre + carte

    def sortir(self):
        self.logger.ecrire(self.out_file)