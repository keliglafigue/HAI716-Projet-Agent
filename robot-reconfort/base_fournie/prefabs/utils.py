"""
Ce fichier regroupe différentes structures de données utiles à différents endroits du programme
"""

from math import sqrt
from enum import Enum

class Direction(Enum):
    N = 0
    S = 1
    O = 2
    E = 3

class Pos:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def taxicabDistanceTo(self, x, y) -> (int | float):
        return abs(self.x - x) + abs(self.y - y)

    def eulerDistanceTo(self, x, y) -> float:
            return sqrt(self.x ** 2 + self.y ** 2)

    def distanceTo(self, x, y) -> (int | float):
        return self.taxicabDistanceTo(x, y)

    # Utiliser "moveX" pour déplacer la position actuelle
    def moveOuest(self) -> Pos:
        self.x -= 1
        return self

    def moveEst(self) -> Pos:
        self.x += 1
        return self
    
    def moveSud(self) -> Pos:
        self.y += 1
        return self
    
    def moveNord(self) -> Pos:
        self.y -= 1
        return self

    # Utiliser getX pour obtenir un nouvel emplacement sans modifier la position
    def getNord(self) -> Pos:
        return Pos(x = self.x, y = self.y - 1)

    def getSud(self) -> Pos:
        return Pos(x = self.x, y = self.y + 1)
    
    def getOuest(self) -> Pos:
        return Pos(x = self.x - 1, y = self.y)
    
    def getEst(self) -> Pos:
        return Pos(x = self.x + 1, y = self.y)
    
    def move(self, dir:Direction) -> "Pos":
        match dir:
            case Direction.N: return Pos(self.x, self.y+1)
            case Direction.S: return Pos(self.x, self.y-1)
            case Direction.O: return Pos(self.x+1, self.y)
            case Direction.E: return Pos(self.x-1, self.y)

    def equals(self, pos:"Pos") -> bool:
        return self.x == pos.x and self.y == pos.y

    def __eq__(self, other):
        return self.equals(other)

    def __str__(self):
        return "x: " + str(self.x) + ", y: " + str(self.y)

    def copy(self) -> Pos:
        return Pos(self.x, self.y)

# ATTENTION : Cette classe n'a pas encore été testée
class File :
    # Programmée de façon peu optimale, a revoir ?
    def __init__(self):
        self.elements = []

    def __init__(self, element):
        self.__init__()
        self.elements.append(element)

    def pop(self):
        return self.elements.pop(0);

    def add(self, element):
        self.elements.append(element)

    def isEmpty(self):
        return len(self.elements) == 0