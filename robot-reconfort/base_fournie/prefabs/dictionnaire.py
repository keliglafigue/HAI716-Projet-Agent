from typing import Any, Dict
import reconfort_io as rio

class Dictionnaire:
    """
    La classe a pour vocation d'être initialisé une fois par le monde et fait les vérifications liées au dictionnaire.
    Ensuite, elle permet au robot lorsqu'il est en face (a vérifier au préalable) de découper un message, et extraire son émotion

    TODO : 
    - Rajouter des vérifications sur le format du json qui est lu
    - Potentiellement transférer rio.normaliser dans cette classe, que je sache c'est le seul endroit ou elle est utile
    """

    def __init__(self, base_dico : Dict[str, Any]):
       self.dico = {}
       for o in base_dico.get("entrees") :
            entrees = o.get("formes")
            emotion = o.get("emotion")
            intensité = o.get("intensite")
            if not (entrees and emotion and intensité): # Erreur très basique, certainement à compléter et préciser
                raise "Erreur de format du dictionnaire"
            for e in entrees:
                self.dico[e] = [emotion, intensité]

    def recuperEmotion(self, chaine:str) -> list[str]:
        message = rio.normaliser(chaine)
        for mot in message:
            if self.dico.get(mot): return self.dico.get(mot) # Pas joli

        return [] # Le mot n'apparait pas dans le dictionnaire


        

