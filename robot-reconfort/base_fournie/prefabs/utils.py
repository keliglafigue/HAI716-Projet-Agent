"""
Ce fichier regroupe différentes structures de données utiles à différents endroits du programme
"""

from math import sqrt

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

    def moveLeft(self) -> tuple[(int | float), (int | float)]:
        self.x -= 1
        return self.x, self.y

    def moveRight(self) -> tuple[(int | float), (int | float)]:
        self.x += 1
        return self.x, self.y
    
    def moveDown(self) -> tuple[(int | float), (int | float)]:
        self.y -= 1
        return self.x, self.y
    
    def moveUp(self) -> tuple[(int | float), (int | float)]:
        self.y += 1
        return self.x, self.y

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