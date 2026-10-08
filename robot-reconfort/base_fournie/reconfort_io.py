"""
Base de code fournie -- projet "Robot de reconfort".

Ce module fait DEUX choses, et rien d'autre :

  1. lire les quatre fichiers d'entree (carte, dictionnaire, armoire,
     scenario) ;
  2. construire et exporter le fichier de trace attendu a la sortie.

Tout le reste du projet -- perception, carte mentale, planification de
chemin, consultation du dictionnaire, fouille de l'armoire, boucle de
decision -- est a votre charge. Ne cherchez pas ces fonctions ici : elles
n'y sont pas, et c'est volontaire.

Vous avez le droit de modifier ce fichier. Vous avez surtout le devoir de
le comprendre : les verifications faites ici sont minimales (voir la
section "Ce qui n'est PAS verifie" plus bas), et les validations
manquantes font partie du travail demande.

Python 3.9+. Aucune dependance externe.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from prefabs.utils import Pos

__all__ = [
    "ErreurFichier",
    "charger_carte",
    "charger_dictionnaire",
    "charger_armoire",
    "charger_scenario",
    "normaliser",
    "Trace",
]

VERSION_ATTENDUE = 1


class ErreurFichier(Exception):
    """Fichier d'entree absent, illisible, ou d'un type inattendu."""

class ErreurCarte(Exception):
    """Erreur du format du fichier de carte fourni"""
class ErreurCarteParamManquant(ErreurCarte):
    def __init__(self, name:str):
        super().__init__(f"Paramètre '{name}' manquant")
class ErreurCarteMauvaisType(ErreurCarte):
    def __init__(self, name:str, type:str):
        super().__init__(f"Mauvais type du paramètre {name}, {type} attendu")
class ErreurCarteParamInvalide(ErreurCarte):
    def __init__(self, name:str, raison:str): 
        super().__init__(f"Paramètre {name} invalide : {raison}")

class ErreurDico(Exception):
    """Erreur du format du fichier de dictionnaire fourni"""
class ErreurDicoParamManquant(ErreurDico):
    def __init__(self, name:str):
        super().__init__(f"Paramètre '{name}' manquant")
class ErreurDicoMauvaisType(ErreurDico):
    def __init__(self, name:str, type:str):
        super().__init__(f"Mauvais type du paramètre {name}, {type} attendu")
class ErreurDicoParamInvalide(ErreurDico):
    def __init__(self, name:str, raison:str): 
        super().__init__(f"Paramètre {name} invalide : {raison}")

class ErreurArmoire(Exception):
    """Erreur du format du fichier d'armoire fourni"""
class ErreurArmoireParamManquant(ErreurArmoire):
    def __init__(self, name:str):
        super().__init__(f"Paramètre '{name}' manquant")
class ErreurArmoireMauvaisType(ErreurArmoire):
    def __init__(self, name:str, type:str):
        super().__init__(f"Mauvais type du paramètre {name}, {type} attendu")
class ErreurArmoireParamInvalide(ErreurArmoire):
    def __init__(self, name:str, raison:str): 
        super().__init__(f"Paramètre {name} invalide : {raison}")

# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

def _lire_json(chemin: str | Path, format_attendu: str) -> Dict[str, Any]:
    """Lit un fichier JSON UTF-8 et verifie son en-tete.

    Ce qui EST verifie ici :
      - le fichier existe et se lit en UTF-8 ;
      - son contenu est du JSON valide ;
      - la racine est un objet ;
      - les champs "format" et "version" sont presents et corrects.

    Ce qui n'est PAS verifie (a vous de le faire, enonce section 5.6) :
      - la presence et le type de chacun des autres champs ;
      - la coherence des donnees (grille rectangulaire, positions dans les
        bornes, resident pose sur un mur, casier hors de l'armoire,
        emotion inconnue, resident cite par un scenario mais absent de la
        carte...).
    """
    chemin = Path(chemin)
    try:
        texte = chemin.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErreurFichier(f"fichier introuvable : {chemin}") from None
    except UnicodeDecodeError as err:
        raise ErreurFichier(
            f"{chemin} n'est pas encode en UTF-8 (octet {err.start})"
        ) from None
    except OSError as err:
        raise ErreurFichier(f"{chemin} illisible : {err}") from None

    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError as err:
        raise ErreurFichier(
            f"{chemin} n'est pas un JSON valide : {err.msg} "
            f"(ligne {err.lineno}, colonne {err.colno})"
        ) from None

    if not isinstance(donnees, dict):
        raise ErreurFichier(
            f"{chemin} : la racine doit etre un objet JSON, "
            f"pas {type(donnees).__name__}"
        )

    format_trouve = donnees.get("format")
    if format_trouve != format_attendu:
        raise ErreurFichier(
            f"{chemin} : format attendu '{format_attendu}', "
            f"trouve {format_trouve!r}"
        )

    version = donnees.get("version")
    if version != VERSION_ATTENDUE:
        raise ErreurFichier(
            f"{chemin} : version {VERSION_ATTENDUE} attendue, trouve {version!r}"
        )

    return donnees

def charger_carte(chemin: str | Path) -> Dict[str, Any]:
    """Charge un fichier carte. Voir l'enonce, section 5.1."""
    carte = _lire_json(chemin, "robot-reconfort/carte")

    # Nom
    if not carte.get("nom"): raise ErreurCarteParamManquant("nom")
    if not isinstance(carte.get("nom"), str): raise ErreurCarteMauvaisType("nom", "str")

    # Dimension
    dimensions = carte.get("dimensions")
    if not dimensions: raise ErreurCarteParamManquant("dimensions")
    if not isinstance(dimensions, dict): raise ErreurCarteMauvaisType("dimensions", "dict")
    if "hauteur" not in dimensions: raise ErreurCarteParamManquant("hauteur")
    if "largeur" not in dimensions: raise ErreurCarteParamManquant("largeur")

    hauteur = dimensions.get("hauteur")
    largeur = dimensions.get("largeur")
    if not isinstance(hauteur, int): raise ErreurCarteMauvaisType("hauteur", "int")
    if not isinstance(largeur, int): raise ErreurCarteMauvaisType("largeur", "int")
    if hauteur <= 0: raise ErreurCarteParamInvalide("hauteur", "doit être supérieur à 0")
    if largeur <= 0: raise ErreurCarteParamInvalide("largeur", "doit être supérieur à 0")

    # Légende
    legende = carte.get("legende")
    if not legende: raise ErreurCarteParamManquant("legende")
    if not isinstance(legende, dict): raise ErreurCarteMauvaisType("legende", "dict")

    for symbole in legende.keys():
        if not isinstance(symbole,str): raise ErreurCarteMauvaisType("legende", "dict(str, str)")
    for case in legende.values():
        if not isinstance(case,str): raise ErreurCarteMauvaisType("legende", "dict(str, str)")
    for case in ["mur", "libre", "depart du robot", "armoire", "dictionnaire", "resident"]:
        if case not in legende.values(): raise ErreurCarteParamManquant(f"legende[*]='{case}']")
    if len(legende.keys()) > 6: raise ErreurCarteParamInvalide("legende", "doit comporter uniquement les symboles nécessaires")
        

    # Grille
    grille = carte.get("grille")
    if not grille: raise ErreurCarteParamManquant("grille")
    if not isinstance(grille, list): raise ErreurCarteMauvaisType("grille", "list")
    if len(grille) != hauteur: raise ErreurCarteParamInvalide("grille", "le nombre de lignes doit être égal à la hauteur indiquée dans les dimensions")

    for i, ligne in enumerate(grille):
        if not isinstance(ligne, str): raise ErreurCarteMauvaisType(f"grille[{i}]", "str")
        if len(ligne) != largeur: raise ErreurCarteParamInvalide(f"grille[{i}]", "la longueur doit être égale à la largeur indiquée dans les dimensions")

        for symbole in ligne:
            if symbole not in legende: raise ErreurCarteParamInvalide(f"grille[{i}]", f"symbole '{symbole}' absent de la légende")

    # Départ du robot
    depart_robot = carte.get("depart_robot")

    if not depart_robot: raise ErreurCarteParamManquant("depart_robot")
    if not isinstance(depart_robot, list): raise ErreurCarteMauvaisType("depart_robot", "list")
    if len(depart_robot) != 2: raise ErreurCarteParamInvalide("depart_robot", "doit contenir exactement 2 coordonnées")

    for i, coordonnee in enumerate(depart_robot):
        if not isinstance(coordonnee, int): raise ErreurCarteMauvaisType(f"depart_robot[{i}]", "int")

    if not (0 <= depart_robot[0] < hauteur): raise ErreurCarteParamInvalide("depart_robot", "la ligne est hors de la grille")
    if not (0 <= depart_robot[1] < largeur): raise ErreurCarteParamInvalide("depart_robot", "la colonne est hors de la grille")

    # Armoire
    armoire = carte.get("armoire")

    if not armoire: raise ErreurCarteParamManquant("armoire")
    if not isinstance(armoire, dict): raise ErreurCarteMauvaisType("armoire", "dict")
    if "position" not in armoire: raise ErreurCarteParamManquant("armoire.position")

    position_armoire = armoire.get("position")

    if not isinstance(position_armoire, list): raise ErreurCarteMauvaisType("armoire.position", "list")
    if len(position_armoire) != 2: raise ErreurCarteParamInvalide("armoire.position", "doit contenir exactement 2 coordonnées")

    for i, coordonnee in enumerate(position_armoire):
        if not isinstance(coordonnee, int): raise ErreurCarteMauvaisType(f"armoire.position[{i}]","int")

    if not (0 <= position_armoire[0] < hauteur): raise ErreurCarteParamInvalide("armoire.position", "la ligne est hors de la grille")
    if not (0 <= position_armoire[1] < largeur): raise ErreurCarteParamInvalide("armoire.position", "la colonne est hors de la grille")

    # Dictionnaire
    dictionnaire = carte.get("dictionnaire")

    if not dictionnaire:raise ErreurCarteParamManquant("dictionnaire")
    if not isinstance(dictionnaire, dict):raise ErreurCarteMauvaisType("dictionnaire", "dict")
    if "position" not in dictionnaire: raise ErreurCarteParamManquant("dictionnaire.position")

    position_dictionnaire = dictionnaire.get("position")

    if not isinstance(position_dictionnaire, list): raise ErreurCarteMauvaisType("dictionnaire.position", "list")
    if len(position_dictionnaire) != 2: raise ErreurCarteParamInvalide("dictionnaire.position", "doit contenir exactement 2 coordonnées")

    for i, coordonnee in enumerate(position_dictionnaire):
        if not isinstance(coordonnee, int): raise ErreurCarteMauvaisType(f"dictionnaire.position[{i}]", "int")

    if not (0 <= position_dictionnaire[0] < hauteur): raise ErreurCarteParamInvalide("dictionnaire.position", "la ligne est hors de la grille")
    if not (0 <= position_dictionnaire[1] < largeur): raise ErreurCarteParamInvalide("dictionnaire.position", "la colonne est hors de la grille")

    # Résident
    residents = carte.get("residents")
    ids = []
    positions = []

    if "residents" not in carte : raise ErreurCarteParamManquant("residents")
    if not isinstance(residents, list): raise ErreurCarteMauvaisType("residents", "list")

    for i, resident in enumerate(residents):
        if not isinstance(resident, dict): raise ErreurCarteMauvaisType(f"residents[{i}]", "dict")

        # ID
        if not resident.get("id"): raise ErreurCarteParamManquant(f"residents[{i}].id")
        if not isinstance(resident.get("id"), str): raise ErreurCarteMauvaisType(f"residents[{i}].id","str")
        if resident.get("id") in ids: raise ErreurCarteParamInvalide("residents.id", "les identifients doivent être uniques")
        else : ids.append(resident.get("id"))

        # Nom
        if not resident.get("nom"): raise ErreurCarteParamManquant(f"residents[{i}].nom")
        if not isinstance(resident.get("nom"), str): raise ErreurCarteMauvaisType(f"residents[{i}].nom", "str")

        # Position
        if "position" not in resident: raise ErreurCarteParamManquant(f"residents[{i}].position")

        position = resident.get("position")
        if not isinstance(position, list): raise ErreurCarteMauvaisType(f"residents[{i}].position", "list")
        if len(position) != 2: raise ErreurCarteParamInvalide(f"residents[{i}].position", "doit contenir exactement 2 coordonnées")
        for j, coordonnee in enumerate(position):
            if not isinstance(coordonnee, int): raise ErreurCarteMauvaisType(f"residents[{i}].position[{j}]", "int")
        if not (0 <= position[0] < hauteur): raise ErreurCarteParamInvalide(f"residents[{i}].position", "la ligne est hors de la grille")
        if not (0 <= position[1] < largeur): raise ErreurCarteParamInvalide(f"residents[{i}].position", "la colonne est hors de la grille")

        pos = Pos(position[0], position[1])
        for autre_pos in positions: 
            if pos.equals(autre_pos): raise ErreurCarteParamInvalide("residents.position", "les positions doivent être uniques")
        positions.append(pos)

        if legende.get(grille[pos.x][pos.y]) != "resident": raise ErreurCarteParamInvalide(f"residents[{i}].position", "la position doit être indiquée sur la carte")

    return carte

def charger_dictionnaire(chemin: str | Path) -> Dict[str, Any]:
    dictionnaire = _lire_json(chemin, "robot-reconfort/dictionnaire") 

    # Nom 
    if not dictionnaire.get("nom"): raise ErreurDicoParamManquant("nom") 
    if not isinstance(dictionnaire.get("nom"), str): raise ErreurDicoMauvaisType("nom", "str") 
    
    # Emotions 
    emotions = dictionnaire.get("emotions") 
    if not emotions: raise ErreurDicoParamManquant("emotions") 
    if not isinstance(emotions, list): raise ErreurDicoMauvaisType("emotions", "list") 
    for i, emotion in enumerate(emotions): 
        if not isinstance(emotion, str): raise ErreurDicoMauvaisType(f"emotions[{i}]", "str") 
    for emo in ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]:
            if emo not in emotions: raise ErreurDicoParamManquant(f"emotions[{emo}]")
    if len(emotions) > 8: raise ErreurDicoParamInvalide("emotions", "doit contenir uniquement les émotions prédéfinies")
    
    # Intensités 
    intensites = dictionnaire.get("intensites") 
    if not intensites: raise ErreurDicoParamManquant("intensites") 
    if not isinstance(intensites, list): raise ErreurDicoMauvaisType("intensites", "list") 
    for i, intensite in enumerate(intensites): 
        if not isinstance(intensite, str): raise ErreurDicoMauvaisType(f"intensites[{i}]", "str") 
    for i in ["faible", "moyenne", "forte"]:
        if i not in intensites: raise ErreurDicoParamManquant(f"intensites[{i}]")
    if len(intensites) > 3: raise ErreurDicoParamInvalide("intensites", "doit contenir uniquement les intensités prédéfinies")
        
    # Entrées 
    entrees = dictionnaire.get("entrees") 
    if "entrees" not in dictionnaire : raise ErreurDicoParamManquant("entrees") 
    if not isinstance(entrees, list): raise ErreurDicoMauvaisType("entrees", "list") 
    for i, entree in enumerate(entrees): 
        if not isinstance(entree, dict): raise ErreurDicoMauvaisType(f"entrees[{i}]", "dict") 
        
        # Formes 
        formes = entree.get("formes") 
        if not formes: raise ErreurDicoParamManquant(f"entrees[{i}].formes") 
        if not isinstance(formes, list): raise ErreurDicoMauvaisType(f"entrees[{i}].formes", "list") 
        for j, forme in enumerate(formes): 
            if not isinstance(forme, str): raise ErreurDicoMauvaisType( f"entrees[{i}].formes[{j}]", "str" ) 
        
        # Emotion 
        emotion = entree.get("emotion") 
        if not emotion: raise ErreurDicoParamManquant(f"entrees[{i}].emotion") 
        if not isinstance(emotion, str): raise ErreurDicoMauvaisType( f"entrees[{i}].emotion", "str" ) 
        if emotion not in emotions: raise ErreurDicoParamInvalide( f"entrees[{i}].emotion", "doit correspondre à une émotion présente dans la liste des émotions" ) 
        
        # Intensité 
        intensite = entree.get("intensite") 
        if not intensite: raise ErreurDicoParamManquant(f"entrees[{i}].intensite") 
        if not isinstance(intensite, str): raise ErreurDicoMauvaisType( f"entrees[{i}].intensite", "str" ) 
        if intensite not in intensites: raise ErreurDicoParamInvalide( f"entrees[{i}].intensite", "doit correspondre à une intensité présente dans la liste des intensités" ) 
    
    return dictionnaire

#TODO : Faire les vérifications du fichier
def charger_armoire(chemin: str | Path) -> Dict[str, Any]:
    armoire = _lire_json(chemin, "robot-reconfort/armoire") 
    
    # Nom 
    if not armoire.get("nom"): raise ErreurArmoireParamManquant("nom") 
    if not isinstance(armoire.get("nom"), str): raise ErreurArmoireMauvaisType("nom", "str") 
    
    # Emotions 
    emotions = armoire.get("emotions") 
    if not emotions: raise ErreurArmoireParamManquant("emotions") 
    if not isinstance(emotions, list): raise ErreurArmoireMauvaisType("emotions", "list") 
    for i, emotion in enumerate(emotions): 
        if not isinstance(emotion, str): raise ErreurArmoireMauvaisType(f"emotions[{i}]", "str") 
    for emo in ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]:
            if emo not in emotions: raise ErreurArmoireParamManquant(f"emotions[{emo}]")
    if len(emotions) > 8: raise ErreurArmoireParamInvalide("emotions", "doit contenir uniquement les émotions prédéfinies")
    
    # Intensités 
    intensites = armoire.get("intensites") 
    if not intensites: raise ErreurArmoireParamManquant("intensites") 
    if not isinstance(intensites, list): raise ErreurArmoireMauvaisType("intensites", "list") 
    for i, intensite in enumerate(intensites): 
        if not isinstance(intensite, str): raise ErreurArmoireMauvaisType(f"intensites[{i}]", "str") 
    for i in ["faible", "moyenne", "forte"]:
        if i not in intensites: raise ErreurArmoireParamManquant(f"intensites[{i}]")
    if len(intensites) > 3: raise ErreurArmoireParamInvalide("intensites", "doit contenir uniquement les intensités prédéfinies")

    # Casier départ
    casier_depart = armoire.get("casier_depart")
    if not casier_depart: raise ErreurArmoireParamManquant("casier_depart")
    if not isinstance(casier_depart, list): raise ErreurArmoireMauvaisType("casier_depart", "list")
    for i, coord in enumerate(casier_depart):
        if not isinstance(coord, int): raise ErreurArmoireMauvaisType(f"casier_depart[{i}]", "int")
        if i >= 2 : raise ErreurArmoireParamInvalide("casier_depart", "doit contenir exactement 2 coordonnées")
        max = (i == 0) if 2 else 7
        if coord < 0 or coord > max: raise ErreurArmoireParamInvalide("casier_depart", f"casier_depart[{i}] doit être compris entre 0 et {max}")

    # Casiers
    casiers = armoire.get("casiers")
    if not casiers: raise ErreurArmoireParamManquant("casiers")
    if not isinstance(casiers, list) : raise ErreurArmoireParamManquant("casiers")
    for i, casier in enumerate(casiers):
        if not isinstance(casier, dict) : raise ErreurArmoireMauvaisType(f"casiers[{i}]", "dict")

        # Ligne
        ligne = casier.get("ligne")
        if "ligne" not in casier : raise ErreurArmoireParamManquant(f"casiers[{i}][ligne]")
        if not isinstance(ligne, int): raise ErreurArmoireMauvaisType(f"casiers[{i}][ligne]", "int")
        if ligne < 0 or ligne > 2: raise ErreurCarteParamInvalide(f"casiers[{i}][ligne]", "doit être compris entre 0 et 2")

        # Colonne
        colonne = casier.get("colonne")
        if "colonne" not in casier : raise ErreurArmoireParamManquant(f"casiers[{i}][colonne]")
        if not isinstance(colonne, int): raise ErreurArmoireMauvaisType(f"casiers[{i}][colonne]", "int")
        if colonne < 0 or colonne > 7: raise ErreurCarteParamInvalide(f"casiers[{i}][colonne]", "doit être compris entre 0 et 7")
        

    return armoire

#TODO : Faire les vérifications du fichier
def charger_scenario(chemin: str | Path) -> Dict[str, Any]:
    """Charge un fichier scenario. Voir l'enonce, section 5.4."""
    return _lire_json(chemin, "robot-reconfort/scenario")


# ---------------------------------------------------------------------------
# Normalisation des messages
# ---------------------------------------------------------------------------

def normaliser(texte: str) -> List[str]:
    """Decoupe un message en mots comparables au dictionnaire.

    Minuscules, accents retires, decoupage sur tout ce qui n'est pas une
    lettre. C'est exactement la regle de l'enonce, section 6.1 ;
    reimplementez-la vous-meme si vous travaillez dans un autre langage.

        >>> normaliser("Je suis TERRIFIEE, vraiment !")
        ['je', 'suis', 'terrifiee', 'vraiment']
    """
    decompose = unicodedata.normalize("NFD", texte.lower())
    sans_accents = "".join(
        c for c in decompose if unicodedata.category(c) != "Mn"
    )
    mots: List[str] = []
    courant: List[str] = []
    for caractere in sans_accents:
        if caractere.isalpha():
            courant.append(caractere)
        elif courant:
            mots.append("".join(courant))
            courant = []
    if courant:
        mots.append("".join(courant))
    return mots


# ---------------------------------------------------------------------------
# Ecriture de la trace
# ---------------------------------------------------------------------------

ACTIONS = ("AVANCER", "CONSULTER", "CHERCHER", "PRENDRE", "DONNER", "ATTENDRE")
DIRECTIONS = ("N", "S", "E", "O")
REPLIS = ("aucun", "intensite", "voisine_1", "voisine_2")


class Trace:
    """Accumule les pas et les livraisons, puis ecrit le fichier de sortie.

    Utilisation typique :

        trace = Trace(nom_carte="appartement_01",
                      nom_scenario="scenario_01",
                      equipe=["Dupont", "Martin"])
        ...
        trace.ajouter_pas(demande=1, position=(6, 1), casier=(1, 0),
                          action="AVANCER", argument="E",
                          perception={"N": "libre", "S": "mur",
                                      "E": "libre", "O": "mur"})
        ...
        trace.ajouter_livraison(demande=1, resident="R1",
                                emotion="tristesse", intensite="moyenne",
                                casier_choisi=(1, 4), repli="aucun",
                                objet="couverture", succes=True)
        trace.ecrire("sorties/trace_01.json")
    """

    def __init__(
        self,
        nom_carte: str,
        nom_scenario: str,
        equipe: Optional[Sequence[str]] = None,
    ) -> None:
        self.nom_carte = nom_carte
        self.nom_scenario = nom_scenario
        self.equipe: List[str] = list(equipe or [])
        self.pas: List[Dict[str, Any]] = []
        self.livraisons: List[Dict[str, Any]] = []

    # -- pas ---------------------------------------------------------------

    def ajouter_pas(
        self,
        demande: Optional[int],
        position: Sequence[int],
        casier: Sequence[int],
        action: str,
        argument: Optional[str] = None,
        perception: Optional[Dict[str, str]] = None,
        contenu_casier: Optional[str] = None,
        commentaire: Optional[str] = None,
    ) -> None:
        """Enregistre un pas de simulation.

        `position`  : couple (ligne, colonne) du robot AVANT l'action.
        `casier`    : couple (ligne, colonne) du selecteur dans l'armoire,
                      AVANT l'action.
        `perception`: ce que le robot voit depuis sa position, sous la forme
                      d'un dictionnaire des quatre directions vers "mur",
                      "libre", "armoire", "dictionnaire" ou "resident".
        `contenu_casier` : l'objet du casier courant, quand le robot est
                      devant l'armoire et peut donc le voir ; None sinon.
        """
        if action not in ACTIONS:
            raise ValueError(
                f"action inconnue {action!r} (attendu : {', '.join(ACTIONS)})"
            )
        if action in ("AVANCER", "CHERCHER") and argument not in DIRECTIONS:
            raise ValueError(
                f"{action} attend une direction parmi {DIRECTIONS}, "
                f"pas {argument!r}"
            )
        self.pas.append({
            "t": len(self.pas),
            "demande": demande,
            "position": [int(position[0]), int(position[1])],
            "casier": [int(casier[0]), int(casier[1])],
            "action": action,
            "argument": argument,
            "perception": dict(perception) if perception else None,
            "contenu_casier": contenu_casier,
            "commentaire": commentaire,
        })

    # -- livraisons --------------------------------------------------------

    def ajouter_livraison(
        self,
        demande: int,
        resident: str,
        emotion: Optional[str],
        intensite: Optional[str],
        casier_choisi: Optional[Sequence[int]],
        repli: str,
        objet: Optional[str],
        succes: bool,
        motif_echec: Optional[str] = None,
    ) -> None:
        """Enregistre l'issue d'une demande, reussie ou non.

        En cas d'echec, `succes` vaut False et `motif_echec` explique
        pourquoi en une chaine courte (par exemple "resident inaccessible",
        "armoire vide", "emotion indeterminee").
        """
        if repli not in REPLIS:
            raise ValueError(
                f"repli inconnu {repli!r} (attendu : {', '.join(REPLIS)})"
            )
        if not succes and not motif_echec:
            raise ValueError("un echec doit etre accompagne d'un motif_echec")
        self.livraisons.append({
            "demande": int(demande),
            "resident": resident,
            "emotion": emotion,
            "intensite": intensite,
            "casier_choisi": ([int(casier_choisi[0]), int(casier_choisi[1])]
                              if casier_choisi is not None else None),
            "repli": repli,
            "objet": objet,
            "pas_utilises": sum(1 for p in self.pas if p["demande"] == demande),
            "succes": bool(succes),
            "motif_echec": motif_echec,
        })

    # -- export ------------------------------------------------------------

    def en_dictionnaire(self) -> Dict[str, Any]:
        reussies = sum(1 for l in self.livraisons if l["succes"])
        return {
            "format": "robot-reconfort/trace",
            "version": VERSION_ATTENDUE,
            "carte": self.nom_carte,
            "scenario": self.nom_scenario,
            "equipe": self.equipe,
            "pas": self.pas,
            "livraisons": self.livraisons,
            "resume": {
                "demandes": len(self.livraisons),
                "reussies": reussies,
                "echecs": len(self.livraisons) - reussies,
                "pas_total": len(self.pas),
            },
        }

    def ecrire(self, chemin: str | Path) -> Path:
        """Ecrit la trace en JSON UTF-8 indente. Cree le dossier au besoin."""
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(
            json.dumps(self.en_dictionnaire(), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        return chemin
