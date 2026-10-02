from pathlib import Path
import reconfort_io as rio

from prefabs.contenuArmoire import contenuArmoire
from prefabs.utils import Pos, Direction

class Armoire:
    """
    Cette classe est une interface permettant d'accéder aux objets comme le ferait le robot.
    """

    def __init__(self, chemin : str | Path):
        self.pos_selecteur = Pos(0, 0)
        dico = rio.charger_armoire(chemin)
        # Vérifier que la position est raccord avec l'émotions et l'intensité
        mat = []
        for i in range(8):
            tab = []
            for i in range(3):
                tab.append("")
            mat.append(tab)
        
        for casier in dico.get("casiers"):
            ligne = casier.get("ligne")
            colonne = casier.get("colonne")

            mat[colonne][ligne] = casier.get("objet")
        
        self.contenu = contenuArmoire(3, 8, mat)
    
    def deplacerSelecteur(dir:Direction):
        new_pos = self.pos_selecteur.move(dir)
        if new_pos.x > 7 : new_pos.x = 0
        if new_pos.x < 0 : new_pos.x = 7
        if new_pos.y > 2 or new_pos.y < 0: raise "Armoire : Deplacement du selecteur hors des limites"
        self.pos_selecteur = new_pos
    
    def regarderObjet() -> str:
        return contenu.regarderObjet(self.pos_selecteur)
    
    def obtenirObjet() -> str:
        obj = contenu.regarderObjet(self.pos_selecteur)
        if not obj : raise "Pas d'objet à cette position"
        contenu.supprimerObjet(self.pos_selecteur)
        return obj

