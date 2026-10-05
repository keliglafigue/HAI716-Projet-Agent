from typing import List
from prefabs.utils import Pos

class Robot:
    def __init__(self, pos:Pos):
        self.emotion = ["",""]
        self.objet = ""
        self.pos = pos

    def isTacheEnCours(self) -> bool:
        return False

    def nouvelleDemande(self, emotion: List[str], resident:str):
        self.emotion = emotion

    def executerPas(self):
        pass