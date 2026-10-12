from typing import Any, Dict, List

from prefabs.utils import Pos
from prefabs.robot import Robot
from prefabs.dictionnaire import Dictionnaire
from prefabs.carte import Carte
from prefabs.armoire import Armoire

class Monde:

    def __init__(self, carte:Dict[str, Any], dico:Dict[str, Any], armoire:Dict[str, Any]):
        self.carte = Carte(carte)
        self.dico = Dictionnaire(dico)
        self.armoire = Armoire(armoire)
        self.pos_robot = self.carte.getPosDepartRobot()
        self.robot = Robot(self.carte.getLargeur(), self.carte.getHauteur(), self.carte.getPosArmoire(), self.carte.getPosDico())


    def executer_requete(self, requete: Dict[str, Any]) -> None:
        if self.robot.isTacheEnCours():
            raise "Houlala"

        
        # emotion = self.dico.recuperEmotion(requete["message"])
        # print(emotion)
        # self.robot.nouvelleDemande(emotion, requete["resident"])
        message = requete.get("message")
        posResident = self.carte.getPosResident(requete.get("id"))
        self.robot.nouvelleDemande(message, posResident)
        
        while self.robot.isTacheEnCours():
            action = self.robot.executerPas() # Les paramètres nécessaire à l'exécution seront passés en paramètre
            """
            vérifier action valide
            exécuter action
            """
