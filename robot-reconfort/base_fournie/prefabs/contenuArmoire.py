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
        
    
    def regarderObjet(pos:Pos) -> str:
        if (pos.x < 0 or pos.x >= largeur or pos.y < 0 or pos.y >= hauteur): raise "Contenu Armoire : index hors range"
        return mat[pos.x][pos.y]
    
    def ajouterObjet(x:int, y:int, objet:str) -> str:
        if (pos.x < 0 or pos.x >= largeur or pos.y < 0 or pos.y >= hauteur): raise "Contenu Armoire : index hors range"
        mat[pos.x][pos.y] = objet
    
    def supprimerObjet(x:int, y:int) -> str:
        if (pos.x < 0 or pos.x >= largeur or pos.y < 0 or pos.y >= hauteur): raise "Contenu Armoire : index hors range"
        if (mat[pos.x][pos.y] == ""): raise "Contenu Armoire : Suppression d'un objet inexistant"
        mat[pos.x][pos.y] = ""
        
        
