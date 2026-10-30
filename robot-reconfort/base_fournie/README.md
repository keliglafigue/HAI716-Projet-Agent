# Robot de réconfort — RATHGEBER-KIVITS Eloi & SOARES--QUEBRIAC Kélig

Projet de semestre, master informatique. Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : *python* — 3.14.8

## Lancer

```
python main.py <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json>
```

Exemple :

```
python main.py cartes/appartement_01.json cartes/scenario_01.json donnees sortie.json
```

Dépendances : Uniquement la bibliothèque standard python a été utilisé

## Tester

```
<votre commande de test>
```

*Une phrase sur ce que couvrent les tests.*

## Organisation du code

| Fichier | Rôle |
|---|---|
| `main.py` | point d'entrée, chargement des fichiers et envoie des requêtes |
| `prefabs/monde.py` | représentation complète du monde, gestion du cycle récupération/validation/application de l'action |
| `prefabs/robot.py` | gestion de l'agent, retourne un coup selon les données qui lui sont envoyés et son historique de découverte |
| `prefabs/carte.py` | représentation de la carte du monde |
| `prefabs/armoire.py` | gestion des objets dans l'armoire |
| `prefabs/utils.py` | divers structure de donnée (Position, File...) |

## État

**Ce qui marche.**
- Décodage des fichiers
- Représentation de l'appartement
- Perception local du monde
- Représentation de l'armoire
- Fouille de l'armoire
- Les différentes actions
- Lecture de l'émotion dans le dictionnaire
- Ecriture de la trace
- Divers stratégie de repli (aucune, intensité, voisin 1 et voisin 2)
- Les échecs avec leur raison (résident inaccessible, objet absent, émotion non décodé...)
- Mémoire des cases déjà exploré au niveau du robot

**Ce qui ne marche pas.** *À compléter — soyez honnêtes, c'est noté en
votre faveur.*
- Les émotions/intensité de l'armoire peuvent ne pas correspondre à leurs positions attendus

## Vidéo
Vous pouvez retrouver une vidéo de démo : `demo.webm`, également déclarée dans `rendu.json`.
