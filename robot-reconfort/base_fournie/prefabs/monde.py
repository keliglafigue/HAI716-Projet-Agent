from utils import Pos
from robot import Robot

class Monde:
    def __init__(self, carte, dico, armoire):
        self.pos_robot = Pos()
        self.robot = Robot()

    def executer_requete(self, requete: str) -> None:
        if self.robot.isTacheEnCours():
            raise "Houlala"
        
        while self.robot.isTacheEnCours():
            action = self.robot.executerPas() # Les paramètres nécessaire à l'exécution seront passés en paramètre
            """
            vérifier action valide
            exécuter action
            """
