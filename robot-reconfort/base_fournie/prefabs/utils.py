"""
Ce fichier regroupe différentes structures de données utiles à différents endroits du programme
"""

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