from typing import Any, Dict, List

from prefabs.utils import Pos
from prefabs.robot import Robot, Perception
from prefabs.dictionnaire import Dictionnaire
from prefabs.carte import Carte
from prefabs.armoire import Armoire

class Monde:

    def __init__(self, carte:Dict[str, Any], dico:Dict[str, Any], armoire:Dict[str, Any]):
        self.carte = Carte(carte)
        self.dico = Dictionnaire(dico)
        self.armoire = Armoire(armoire)
        print(self.armoire.contenu.mat)
        self.pos_robot = self.carte.getPosDepartRobot()
        self.robot = Robot(self.carte.getLargeur(), self.carte.getHauteur(), self.carte.getPosArmoire(), self.carte.getPosDico())

    def initPerception(self) -> Perception:
        return Perception(
            self.pos_robot,
            self.carte.getNeigboringCells(self.pos_robot)
        )

    def executer_requete(self, requete: Dict[str, Any]) -> None:
        if self.robot.isTacheEnCours():
            raise "Houlala"

        message = requete.get("message")
        posResident = self.carte.getPosResident(requete.get("resident"))
        self.robot.nouvelleDemande(message, posResident)

        percu = self.initPerception()
        
        while self.robot.isTacheEnCours():
            action = self.robot.executerPas(percu) # Les paramètres nécessaire à l'exécution seront passés en paramètre
            """
            vérifier action valide
            exécuter action
            mettre perception à jour
            """
