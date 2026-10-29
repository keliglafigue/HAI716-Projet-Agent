# Rapport projet de POA/SMA

Auteurs : Rathgeber-Kivits Eloi, Soares--Quebriac Kélig, M1 Imagine

[TOC]

## Architecture

<img src="diagramme.svg" alt="diagramme"  />

Ci-dessus, vous pouvez retrouver le diagramme de classe utiliser par notre architecture. Nous y retrouvons la classe monde, qui est le chef d'orchestre du programme. Elle dispose de l'ensemble des informations connus. Pour chaque requête, elle va construire un objet "Perception" contenant les différentes informations obtenu par le robot ce tour, l'envoyer au robot qui va alors évaluer quel action faire. Suite à cela, elle va vérifier si l'action du robot est valide, et si c'est le cas, exécuter les changements nécessaire sur le monde.



Nous avons veillé à ce que le robot n'est aucun accès à la classe Monde : sa représentation de la carte est complètement distincte de celle de Monde, et les positions qui lui sont envoyés le sont faits en copie, ainsi le robot ne peut en aucun cas modifier sa position ou les cases du monde, seuls la classe Monde en est capable. Une stratégie similaire a été adopté pour l'armoire.

## Stratégie de replanification

En cas de découverte d'un mur, le robot va replanifier l'ensemble de sa trajectoire. Soit $l$ la largeur de la carte et $h$ sa hauteur, l'algorithme utilisé pour planifier la trajectoire du robot a alors une complexité $\in O(l \times h)$. Cependant, bien que ce ne soit pas reflété dans le code, nous avons réfléchi à comment éviter de recalculer l'ensemble des cases. Nous avions pensé à créer un graphe de dépendance, où chaque case serait associé à la case lui ayant donné sa distance à l'objectif. Ainsi si une case venait à se transformer en mur, la chaîne de dépendance nous permettra de dire précisément quels cases ont été affectés.

## Critique de la règle de repli

Nous pensons que cela peut se défendre car la distance entre deux émotions sur la roue semble représenter une distance psychologique aux émotions, il parait raisonnable de dire que le dégoût est plus proche de la colère que de la confiance, cependant les objets qui sont associés à chacune de ces émotions ne vont pas nécessairement respecter cette distance là : si quelqu'un se sent moyennement triste et que le robot apporte un déodorant, cette personne pourrait mal le prendre.



Quelque chose de plus approprié pourrait être d'associer à chaque objet la liste des émotions/intensité auxquels il est approprié de répondre, mais cela rendrait le rangement et la navigation au sein de l'armoire plus compliqué.

## Échecs de notre robot

 : trois situations où il se comporte mal, avec l'analyse de la cause. Un rapport qui
affirme que tout fonctionne parfaitement sera lu comme un rapport qui n'a pas cherché.

### Echec 1

Blablabla

### Echec 2

Bliblibli

### Echec 3

Brad, Brooke, Broc, Broc, Brooke, Brak