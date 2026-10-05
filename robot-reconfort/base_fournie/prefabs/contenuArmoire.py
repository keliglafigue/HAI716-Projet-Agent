from prefabs.utils import Pos

class contenuArmoire:
    """
    Cette classe permet de représenter le contenu de l'armoire. Elle stocke les objets et permet d'y accéder grâce à leur position.
    """

    # La matrice doit s'utiliser mat[x][y]
    def __init__(self, hauteur:int, largeur:int, mat:list[list[str]]): 
        self.hauteur = hauteur
        self.largeur = largeur
        self.mat = mat
        
    
    def regarderObjet(self, pos:Pos) -> str:
        if (pos.x < 0 or pos.x >= self.largeur or pos.y < 0 or pos.y >= self.hauteur): raise "Contenu Armoire : index hors range"
        return self.mat[pos.x][pos.y]
    
    def ajouterObjet(self, pos:Pos, objet:str) -> str:
        if (pos.x < 0 or pos.x >= self.largeur or pos.y < 0 or pos.y >= self.hauteur): raise "Contenu Armoire : index hors range"
        self.mat[pos.x][pos.y] = objet
    
    def supprimerObjet(self, pos:Pos) -> str:
        if (pos.x < 0 or pos.x >= self.largeur or pos.y < 0 or pos.y >= self.hauteur): raise "Contenu Armoire : index hors range"
        if (self.mat[pos.x][pos.y] == ""): raise "Contenu Armoire : Suppression d'un objet inexistant"
        self.mat[pos.x][pos.y] = ""
        
        
