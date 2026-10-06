from typing import Any, Dict, List

from prefabs.utils import Pos
from prefabs.robot import Robot
from prefabs.dictionnaire import Dictionnaire
from prefabs.carte import Carte
from prefabs.armoire import Armoire

class Monde:

    def __init__(self, carte:Dict[str, Any], dico:Dict[str, Any], armoire:Dict[str, Any]):
        self.pos_robot = Pos()
        self.robot = Robot(Pos(0,0))
        self.dico = Dictionnaire(dico)
        self.carte = Carte(carte)
        self.armoire = Armoire(armoire)


    def executer_requete(self, requete: Dict[str, Any]) -> None:
        if self.robot.isTacheEnCours():
            raise "Houlala"

        
        emotion = self.dico.recuperEmotion(requete["message"])
        print(emotion)
        self.robot.nouvelleDemande(emotion, requete["resident"])
        while self.robot.isTacheEnCours():
            action = self.robot.executerPas() # Les paramètres nécessaire à l'exécution seront passés en paramètre
            """
            vérifier action valide
            exécuter action
            """
