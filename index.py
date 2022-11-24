# Ma version actuelle de python : Python 3.9.0 64-bit
import sys, random, time

if sys.version_info[0] == 3: # Si version : Python 3
    from tkinter import *
    from tkinter import messagebox
    from tkinter.font import *
    
else: # Si version : Python 2
    from Tkinter import *
    from tkMessageBox import *
    from TkFont import * 


cellules = {} # La liste de toutes les cellules, avec les coordonnées pour clé, les objets représentant les cellules graphiquement et le nombre de mines dans le voisinage
cellulesMine = {} # La liste des cellules pièges

cellulesInconnu = {} # La liste des cellules Inconnues
cellulesDecouvertes = {} # La liste des cellules Découvertes
cellulesDrapeau = {} # La liste des cellules minées, suspecter par le joueur
cellulesQuestion = {} # La liste des cellules en questionnement

celluleCouleur = ["#767676", "#EAEAEA", "#C25D5D","#DADC58", "#E49E4F"] # La couleur des cellules en fonction de leur état [INCONNU, DECOUVERTE, MINE, QUESTION, DRAPEAU]
celluleSize = 32 # Taille des cellules composant le quadrillage

largeurLigne = 1 # Largeur des lignes composant la grille du plateau

grilleWidth = 0 # Largeur de la grille
grilleHeight = 0 # Hauteur de la grille 

nombreDeLigne = 0 # Le nombre de ligne composant la grille du plateau de jeu
nombreDeColonne = 0 # Le nombre de colonne composant la grille
nombreDeCellules = 0 # Le nombre total de cellule composant le plateau du jeu (le nombre de colonne X le nombre de ligne)

nombreMineAPoser = 0 # Le nombre de mines a placer sur les cellules composant le jeu (< nombre total de cellules)


jeuCommence = 0.0 # Le nombre de secondes depuis 1970 à l'instant t (moment de la première interaction du joueur)


gagner = False # Détermine si le joueur a gagné ou perdu a la fin de la partie
partieTerminer = True # Lorsque la partie est terminée, le joueur ne peut plus interagir avec les cellules


difficulter = 1 # La difficulté de la nouvelle partie
maxDifficulter = 4 # La difficulté maximale que l'on peut avoir dans le jeu
difficulterStringList = ["Facile", "Normal", "Difficile", "Impossible"] # La liste des difficultés sous forme de chaine de caractères
difficulterOption = {1 : [9, 9, 10], 2 : [16, 16, 40], 3 : [16, 30, 80], 4 : [30, 50, 250]} # Les options du jeu en fonction de la difficulté -> difficulté : [nombre de ligne, nombre de colonne, nombre de mine]


# IA Variables

IA_EstActiver = False # L'IA est activée dans la partie, le partie se jouera donc "toute seule"
IA_Vitesse = [1000, 500, 200, 50, 0] # Liste des vitesses possible d'action de l'IA (temps entre chaque action)  
IA_VitesseNomListe = ["tres lent", "lent", "Normal", "Rapide", "Instantané"] # Liste des vitesses possible d'action de l'IA (temps entre chaque action) sous forme de chaine de caractere
IA_VitesseActuelle = 0 # Index de la liste des vitesse, determinant la vitesse actuelle

# Activation / desactivation de l'IA
def ActiverIA():
    global IA_EstActiver
    
    IA_EstActiver = not IA_EstActiver # On inverse l'etat de l'IA, comme un interupteur, soit allumer soit eteint
    if IA_EstActiver:
        IA_BoutonActiverOuNon.set("IA : Activer")
        IA_Interaction()
    else:
        IA_BoutonActiverOuNon.set("IA : Désactiver")
    
# Changement de vitesse de l'IA
def IA_ChangementVitesse():
    global IA_VitesseActuelle
    
    IA_VitesseActuelle += 1
    if IA_VitesseActuelle > 4:
        IA_VitesseActuelle = 0
    IA_VitesseNom.set("Vitesse : " + IA_VitesseNomListe[IA_VitesseActuelle])
    
    
# Analyse les cellules voisines des voisines
def AnalyseVoisineDeVoisine(lig2, col2):
    nombreCelluleVoisineDeVoisine = 0 # Le nombre de cellule que la voisine a (selon la position de la cellule en quesion : sur les bord de la grille / dans un coin ...)
    nombreCelluleVoisineDeVoisineDecouverte = 0 # Le nombre de cellule voisine decouverte de la voisine de la cellule inconnue 
    nombreCelluleVoisineDeVoisineDrapeau = 0 # Le nombre de cellule voisine avec un drapeau de la voisine de la cellule inconnue 
    
    # Recherche dans les voisines des voisines de la cellule inconnue
    for voisineDeVoisine in ((lig2-1, col2-1), (lig2-1, col2), (lig2-1, col2+1), (lig2, col2-1), (lig2, col2+1), 
    (lig2+1, col2-1), (lig2+1, col2), (lig2+1, col2+1)):
        if voisineDeVoisine in cellules: # Si la cellule existe
            nombreCelluleVoisineDeVoisine += 1 # On augmente le nombre de cellule
            if voisineDeVoisine in cellulesDecouvertes: # si elle est decouverte
                nombreCelluleVoisineDeVoisineDecouverte += 1 # on augmente le nombre de cellules voisine decouvertes
            if voisineDeVoisine in cellulesDrapeau: # si elle a un drapeau (est une mine potentielle)
                nombreCelluleVoisineDeVoisineDrapeau += 1 # On augmente le nombre de voisine avec un drapeau
    
    return nombreCelluleVoisineDeVoisine, nombreCelluleVoisineDeVoisineDecouverte, nombreCelluleVoisineDeVoisineDrapeau
        

# Jeu de l'IA
def IA_Interaction():
    actionDecouverteCell = True # Au debut nous supposons que le prochain coup sera une decouverte de cellule.
    coordProchaineAction = (0, 0) # Les coordonnées de la cellule sur laquelle nous allons interagir
        
    uneMeilleurCelluleEstTrouver = False # Si on a trouver une cellule ou il est interessant d'interagir avec (pour placer un drpeau / la decouvrir)
    
    # On analyse les cellules Inconnues
    for x in cellulesInconnu:
        if uneMeilleurCelluleEstTrouver: # Si on a deja trouver une bonne cellule avec laquelle interagir
            break # On quitte la boucle pour interagir avec celle-ci, le Break n'est pa une bonne habiude de programmation,
            # Ici nous aurions pu utiliser une boucle While(not uneCelluleTrouver et Parcours de la liste des cellule pas fini) mais cela
            # impliquerait un code plus compliquer a lire et a comprendre, mais aussi de moins bonne performance etant donner qu'il faudrait
            # tester le parcours du tableau à chaque iteraton, rajouter des variables ect..

        # Decompostion des coordonnées de la cellule inconnue que nous etudions
        lig = x[0]
        col = x[1]
        
        # Recherche dans les voisines de la cellule inconnue
        for voisine in ((lig-1, col-1), (lig-1, col), (lig-1, col+1), (lig, col-1), (lig, col+1), 
        (lig+1, col-1), (lig+1, col), (lig+1, col+1)):
            if not voisine in cellules: # Si la cellule n'existe pas (en cas de cellules dans les coins et bord de la grille)
                continue # On passse a la prochaine voisine
            
            # Decompostion des coordonnées de la cellule voisine a la cellule inconnue que nous etudions
            lig2 = voisine[0]
            col2 = voisine[1]
            
            nombreCelluleVoisineDeVoisine, nombreCelluleVoisineDeVoisineDecouverte, nombreCelluleVoisineDeVoisineDrapeau = AnalyseVoisineDeVoisine(lig2, col2) # On analyse les cellules voisines des voisines
            
            if (nombreCelluleVoisineDeVoisineDecouverte == nombreCelluleVoisineDeVoisine - 1 
            or nombreCelluleVoisineDeVoisineDecouverte + nombreCelluleVoisineDeVoisineDrapeau == nombreCelluleVoisineDeVoisine - 1): # On regarde si la cellule est interessante
                coordProchaineAction = x # On retient ses coordonnées
                if nombreCelluleVoisineDeVoisineDrapeau == cellules[voisine][1] - 1: # Si elle est une mine potentielle
                    actionDecouverteCell = False # On place un drapeau
                uneMeilleurCelluleEstTrouver = True 
                    
    if not uneMeilleurCelluleEstTrouver: # Si aucune cellule avec un emplacement interessant est trouver, on decouvre une cellule au hasard
        coordProchaineAction = random.choice(list(cellulesInconnu.keys()))
            
    # On agit en fonction de l'action determiner precedemment (placement de drapeau ou decouverte de la cellule inconnue trouver, au hasard ou non)
    if actionDecouverteCell:
        DecouverteCellule(coordProchaineAction[0], coordProchaineAction[1])
    else:
        DrapeauCellule(coordProchaineAction[0], coordProchaineAction[1])
    
    if not partieTerminer and IA_EstActiver: # Si la partie n'est pas terminer, on continue
        Grille.after(IA_Vitesse[IA_VitesseActuelle], IA_Interaction) # Temps entre chaque actions de l'IA


# Création de la nouvelle partie
def CreeNouvellePartie():
    global cellules, cellulesDecouvertes, cellulesMine, partieTerminer, gagner, jeuCommence
    global cellulesInconnu, cellulesDrapeau, cellulesQuestion
    
    partieTerminer = False # On commence une nouvelle partie
    gagner = False # Lorsque FinDePartie est appeler, si gagner est toujours a False -> le joueur a perdu.
    
    cellules = {} # La liste de toutes les cellules, avec les coordonnées pour clé, les objets représentant les cellules graphiquement et le nombre de mines dans le voisinage
    cellulesMine = {} # La liste des cellules pièges
    
    cellulesInconnu = {} # La liste des cellules Inconnues
    cellulesDecouvertes = {} # La liste des cellules Découvertes
    cellulesDrapeau = {} # La liste des cellules minées, suspecter par le joueur
    cellulesQuestion = {} # La liste des cellules en questionnement
    
    jeuCommence = 0.0 # Le nombre de seconde depuis 1970, on prend cette valeur lorsque la partie est lancer, a la prmeiere interaction du joueur
    DefinirOptionJeuParDifficulter() # On configure les parametre de la partie
    
    CreationGrille() # On dessine la grille en dernier (Pour faciliter son affichage)
    
    nbrMine_label.configure(text=" Mines : " + str(nombreMineAPoser)) # On met a jour le nombre de mine sur le plateau
    
    # Si on active l'IA
    if IA_EstActiver:
        IA_Interaction()


# Creation du quadrillage qui accueillera les cellules
def CreationGrille():
    global grilleWidth, grilleHeight
    
    grilleCouleur = "grey" # Couleur du quadrillage
    
    grilleWidth = nombreDeColonne * (celluleSize + largeurLigne) # Largeur de la grille (utiliser pour le canvas ect)
    grilleHeight = nombreDeLigne * (celluleSize + largeurLigne) # Hauteur de la grille (utiliser pour le canvas ect)
    
    Grille.configure(width=grilleWidth, height = grilleHeight) # On reconfigure la taille du canvas
    
    ligneCoord_V = largeurLigne # On commence a la largeur de la ligne (pour pas dessiner dessu) 
    ligneCoord_H = largeurLigne # On commence a la largeur de la ligne (pour pas dessiner dessu)
    
    Grille.delete(ALL) # On supprime tout pour refaire
    
    InitialisationCellules() # On dessine les cellules + Pose Mines
    PoseMine() # On pose n mines sur les cellules aleatoires
    
    # Création des lignes verticales
    for _x in range(nombreDeColonne + 1):
        Grille.create_line(ligneCoord_V, largeurLigne, ligneCoord_V , grilleHeight, 
                           fill = grilleCouleur, width = largeurLigne, tags = "ligneV")
        
        ligneCoord_V += (celluleSize + largeurLigne) # On avance d'une cellule (sa taille + la largeur de la ligne du quadrillage)
    
    # Création des lignes horizontales
    for _y in range(nombreDeLigne + 1):
        Grille.create_line(largeurLigne, ligneCoord_H, grilleWidth, ligneCoord_H, 
                           fill = grilleCouleur, width = largeurLigne, tags = "ligneH")
        
        ligneCoord_H += (celluleSize + largeurLigne) # On avance d'une cellule (sa taille + la largeur de la ligne du quadrillage)
         

# Initialise toutes les cellules du démineur, elles sont toutes non minés, avec l'etat INCONNU et un nombre de voisine minées a 0.
def InitialisationCellules():
    global nombreDeCellules
    
    nombreDeCellules = nombreDeColonne * nombreDeLigne # On met a jour le nombre de cellule totale
    coordGrille_X = largeurLigne # On commence a la largeur de la ligne (pour pas dessiner dessu) 
    coordGrille_Y = largeurLigne # On commence a la largeur de la ligne (pour pas dessiner dessu) 
    
    for x in range(0, nombreDeLigne): 
        for y in range(0, nombreDeColonne):
            i = [0, 0]
            
            # On récupere l'ID de rectangle que l'on cree (pour le modifier plus tard)
            i[0] = Grille.create_rectangle(coordGrille_X, coordGrille_Y, coordGrille_X + celluleSize, coordGrille_Y + celluleSize, 
                                        fill = celluleCouleur[0])
            
            # On récupere l'ID de l'image que l'on cree (pour la modifier plus tard en fonction de l'Etat de la cellule)
            coordX, coordY = CalculCoordCentreDeCellule(i[0])
            i[1] = Grille.create_image(coordX, coordY, image = drapeauImg, state = HIDDEN)
            
            cellules[(x, y)] = [i, 0]  # [[ID du rectangle, ID de l'image],  Nombre mines dans le voisinage]
            cellulesInconnu.setdefault((x, y))
            
            coordGrille_X += (celluleSize + largeurLigne) # On avance d'une cellule + la largeur de la ligne pour dessiner sa voisine
        
        coordGrille_X = largeurLigne # On revient au debut de la ligne (largeur de la ligne (pour pas dessiner dessu))
        coordGrille_Y += (celluleSize + largeurLigne) # On avance d'une cellule + la largeur de la ligne pour dessiner sa voisine
     

# Pose un nombre de mines (selon la difficulter) sur des cellules du jeu de facon aleatoire
def PoseMine():
    global nombreMineAPoser
    
    if nombreMineAPoser > nombreDeCellules: # On verifie que l'on a pas plus de mines a poser que de cellules ou les poser. (surtout pour debug)
        nombreMineAPoser = nombreDeCellules
    
    cellulesDisponiblePourPose = list(cellules.keys())  # Tableau contenant les coordonnees des cellules ou il est possible de poser une mine de facon aleatoire, 
    # possibiliter de choisir les cellules ou l'on peut poser des mines -> on peut exclure les coins si on veut.
    
    for _x in range(0, nombreMineAPoser):
        celluleAMiner = random.choice(cellulesDisponiblePourPose) # On choisit une cellule aleatoirement dans la liste
        cellulesDisponiblePourPose.remove(celluleAMiner) # On retire la cellule selectionner de la liste pour eviter de retomber dessu
        cellulesMine.setdefault(celluleAMiner) # On ajoute la cellule a la liste des cellules miné
        
        lig = celluleAMiner[0] # On recupere la ligne de la nouvelle cellule piege
        col = celluleAMiner[1] # On recupere la colonne de la nouvelle cellule piege
        
        #Grille.itemconfigure(cellules[(lig, col)][0] [0], fill = "blue") # Montre l'emplacement des mines -> debug uniquement
        
        # On incremente le nombre de mine dans le voisinage de chaque voisine de la mine
        for voisine in ((lig-1, col-1), (lig-1, col), (lig-1, col+1), (lig, col-1), (lig, col+1), 
        (lig+1, col-1), (lig+1, col), (lig+1, col+1)):
            if voisine in cellules: # Si la cellule voisine est existante
                cellules[voisine][1] += 1


# Calcul les coordonnées du milieu d'une cellule pour placer un element dedans
def CalculCoordCentreDeCellule(objectID):
    pos = Grille.coords(objectID) # On recupere les coordonnees de l'objet sur le canvas avec son ID
    x = pos[0] + ((celluleSize + largeurLigne)/2) # On calcul le centre X
    y = pos[1] + ((celluleSize + largeurLigne)/2) # On calcul le centre Y

    return x, y # On retourne les coordonnées x et y


# Change la difficulter de la nouvelle partie
def ChangeDifficulter():
    global difficulter, difficulterString
    
    difficulter += 1 # On incremente la difficulter
    if difficulter > maxDifficulter: # Si la difficulter est > que la difficulter Maximale, on revient a 1 (difficulter facile)
        difficulter = 1
    
    difficulterString.set(difficulterStringList[difficulter-1]) # On change le texte du bouton en fonction du texte correspondant a la nouvelle difficulter


# Change les options de la nouvelle partie 
def DefinirOptionJeuParDifficulter():
    global nombreDeColonne, nombreDeLigne, nombreMineAPoser
    
    # On change les options en fonction de la difficulter : Taille du plateau (largeur et hauteur) & nombre de mine a poser
    nombreDeLigne = difficulterOption[difficulter][0]
    nombreDeColonne = difficulterOption[difficulter][1]
    nombreMineAPoser = difficulterOption[difficulter][2]
   

# Calcul et retourne la position de la cellule a modifier (sa ligne et sa colonne).
def CalculCoordEtNumLigne(event):
    global celluleSize

    x = event.x - (event.x % (celluleSize + largeurLigne)) # Coord x du click -> coord x de la cellule
    y = event.y - (event.y % (celluleSize + largeurLigne)) # Coord y du click -> coord y de la cellule
    lig = int(y / (celluleSize + largeurLigne)) # Ligne
    col = int(x / (celluleSize + largeurLigne)) # Colonne
    return lig, col          


# Decouverte d'une cellule avec ses coordonnées
def DecouverteCellule(lig, col):
    global gagner, jeuCommence

    if not (lig, col) in cellulesDecouvertes and not (lig, col) in cellulesDrapeau: # Si cellule pas encore decouverte et pas Drapeau
        cellulesDecouvertes.setdefault((lig, col)) # On l'ajoute dans la liste des cellules decouverte
        
        # On le retire de ce que c'etait avant
        if (lig, col) in cellulesInconnu:
            del cellulesInconnu[(lig, col)]
        elif (lig, col) in cellulesQuestion:
            del cellulesQuestion[(lig, col)]
        
        if len(cellulesDecouvertes.keys()) == 1: # Si c'est la premiere cellule decouverte -> prmeiere interaction du joueur
            jeuCommence = time.time() # On recupere le nombre de seconde depuis 1970
        
        if (lig, col) in cellulesMine.keys(): # La cellule decouverte serait-elle une mine ?
            FinPartie() # Fin de la partie, le joueur a perdu. Pas besoin d'afficher graphiquement que c'est une mine ici puisque l'on va montrer toutes les mines  a la foi dans FinPartie()
            return
        
        #### Si on arrive ici, c'est quie la cellule decouverte n'etait pas une mine.
        
        Grille.itemconfigure(cellules[(lig, col)][0][0], fill = celluleCouleur[1]) # On configure le rectangle pour afficher que la cellule est decouverte
        Grille.itemconfigure(cellules[(lig, col)][0][1], state = HIDDEN) # On configure le rectangle pour afficher que la cellule est decouverte
        
        if len(cellulesDecouvertes) == (len(cellules) - len(cellulesMine)): # Si on a autant de cellules decouverte que de cellule a decouvrir
            gagner = True # On gagne
            FinPartie() # On termine la partie
            return
        
        ### Si on arrive ici, c'est qu'il reste d'autres cellules a decouvrir

        if cellules[(lig, col)][1] > 0: # Si la cellule decouverte a au moins une mine dans le voisinage
            coordX, coordY = CalculCoordCentreDeCellule(cellules[(lig, col)][0][0]) # On calcul la position du texte qui affichera le nombre de mines dans le voisinage (1 - 8)
            Grille.create_text(coordX, coordY, text=str(cellules[(lig, col)][1]), font = helv12) # Creation du texte au milieu de la cellule
            return
        
        ###Si on arrive ici, c'est que la cellule decouverte n'a aucune mine dans le voisinage (parmis ses 8 voisines (gauche droite haut bas et diagonales)
        
        # On va donc decouvrir les cellules voisine de la cellule decouverte
        for voisine in ((lig-1, col-1), (lig-1, col), (lig-1, col+1), (lig, col-1), (lig, col+1), 
        (lig+1, col-1), (lig+1, col), (lig+1, col+1)):
            if voisine in cellules: # Si la cellule voisine est existante
                DecouverteCellule(voisine[0], voisine[1]) # self call, la fonction s'appelle elle même, en passant en parametre les coordonnées de la voisine


# Change l'etat d'une cellule en fonction de son Etat actuel
def ChangeEtatCellule(lig, col):
    if (lig, col) in cellulesInconnu:
        DrapeauCellule(lig, col)     
    elif (lig, col) in cellulesDrapeau:
        QuestionCellule(lig, col)
    else:
        InconnuCellule(lig, col)    


# Change l'etat d'une cellule : DRAPEAU
def DrapeauCellule(lig, col):
    global nombreMineAPoser
    
    if (lig, col) in cellulesQuestion: # Si la cellule a un point d'interrogation
        del cellulesQuestion[(lig, col)] # On supprime 
    elif (lig, col) in cellulesInconnu: # Si la cellule est Inconnue
        del cellulesInconnu[(lig, col)] # On supprime
    
    cellulesDrapeau.setdefault((lig, col)) # On ajoute la cellule aux drapeaux
    Grille.itemconfigure(cellules[(lig, col)][0][0], fill = celluleCouleur[4]) # Couleur cellule = Orange
    Grille.itemconfigure(cellules[(lig, col)][0][1], state = NORMAL) # Image = On affiche le drapeau
    
    nombreMineAPoser -= 1 # On met a jour le nombre de mine a decouvrir
    nbrMine_label.configure(text=" Mines : " + str(nombreMineAPoser)) # On met a jour le nombre de mines


# Change l'etat d'une cellule : QUESTION
def QuestionCellule(lig, col):
    global nombreMineAPoser
    
    if (lig, col) in cellulesDrapeau:
        del cellulesDrapeau[(lig, col)]
    elif (lig, col) in cellulesInconnu:
        del cellulesInconnu[(lig, col)]
        
    cellulesQuestion.setdefault((lig, col))
    Grille.itemconfigure(cellules[(lig, col)][0][0], fill = celluleCouleur[3]) # Couleur cellule = Jaune
    Grille.itemconfigure(cellules[(lig, col)][0][1], image = questionImg) # Image = Question
    
    nombreMineAPoser += 1 # On re-met a jour le nombre de mine a decouvrir
    nbrMine_label.configure(text=" Mines : " + str(nombreMineAPoser)) # On met a jour le label


# Change l'etat d'une cellule : INCONNU
def InconnuCellule(lig, col):
    global nombreMineAPoser
    
    if (lig, col) in cellulesDrapeau:
        del cellulesDrapeau[(lig, col)]
    elif (lig, col) in cellulesQuestion:
        del cellulesQuestion[(lig, col)]
    
    cellulesInconnu.setdefault((lig, col))
    Grille.itemconfigure(cellules[(lig, col)][0][0], fill = celluleCouleur[0]) # Couleur cellule = INCONNU
    Grille.itemconfigure(cellules[(lig, col)][0][1], image = drapeauImg, state = HIDDEN) # Image = drapeau -> cacher


# On gére l'evenement du clic gauche de la souris du joueur
def CliqueGaucheSurCellule(event):
    if partieTerminer: # Si la partie est deja terminer, rien ne se passe
        return

    lig, col = CalculCoordEtNumLigne(event) # Calcul ligne et colonne de la cellule cliqué
    if (lig, col) in cellules: # Si la cellule est bien existante
        DecouverteCellule(lig, col) # On la decouvre
              
    
# On gére l'evenement du clic droit de la souris du joueur
def CliqueDroitSurCellule(event):
    if partieTerminer: # Si la partie est deja terminer, rien ne se passe
        return

    lig, col = CalculCoordEtNumLigne(event) # Calcul ligne et colonne de la cellule cliqué
    if (lig, col) in cellules and not (lig, col) in cellulesDecouvertes: # Si la cellule est bien existante
        ChangeEtatCellule(lig, col) # On change l'etat de la cellule en fonction de son etat actuel


# Fonction qui gére la fin de la partie, affiche si la partie est gagner ou non
def FinPartie():
    global partieTerminer
    
    partieTerminer = True # On termine la partie pour arreter toutes interaction possible entre le joueur et les cellules du plateau de jeu
    # Arrete aussi l'IA si elle est activer
    
    for x in cellulesMine.keys(): # On affiche toutes les mines sur le plateau
        Grille.itemconfigure(cellules[x][0][0], fill = celluleCouleur[2]) # Change couleur de la cellule
        
        # On configure l'image de la cellule pour etre une mine, qui sera cacher au debut
        img = mineImg
        if x in cellulesDrapeau: # Si la mine avait un drapeau sur sa cellule, on montre que le drapeau etait bien placer
            img = mineDecouverteImg
        Grille.itemconfigure(cellules[x][0][1], image = img, state = NORMAL) # On change l'image des cellules mine pour les devoiler
            
    # Message
    tempsJeu = int(time.time() - jeuCommence) # On calcul la duree de la partie
    if IA_EstActiver:
        msg = "IA a Perdu... " +  str(tempsJeu) + " sec" # Message de defaite IA
    else: 
        msg = "Vous avez Perdu... " +  str(tempsJeu) + " sec" # Message de defaite Joueur
    
    if gagner: # Si la partie est gagner
        if IA_EstActiver:
            msg = "IA a Gagné ! " +  str(tempsJeu) + " sec" # Message de victoire IA
        else:
            msg = "Vous avez Gagné ! " +  str(tempsJeu) + " sec" # Message de victoire joueur
        
    # On affiche le message de fin de partie (gagner ou perdu)
    messagebox.showinfo(title="Result", message = msg)
    
    #CreeNouvellePartie() # Lancement nouvelle partie automatique apres fin de la precedente
    # Debug uniquement pour le moment, ajout d'un bouton pour l'activer / desactiver ? 


### Fenetre TK()
Ecran = Tk()
Ecran.title(" - Démineur -") # Nom de la fenetre
Ecran.geometry("+0+0") # "redimensionnable" par le canvas (la grille)
Ecran.resizable(0, 0) # L'utilisateur ne peut pas redimensionner la fenetre
Ecran.configure(bg="#484848") # Couleur du fond de l'Ecran

# Images
mineImg = PhotoImage(file='res/mine.png') # Img de mine
mineDecouverteImg = PhotoImage(file='res/mine_decouverte.png') # Img de mine decouverte
drapeauImg = PhotoImage(file='res/drapeau.png') # Img de drapeau
questionImg = PhotoImage(file='res/question.png') # Img de question

# Polices d'ecriture
helv12 = Font(family='Helvetica', size=12, weight='bold')
helv18 = Font(family='Helvetica', size=18, weight='bold')

# Frame au dessu du plateau de jeu, contenant le nombre de mine sur le plateau
InfosFrame = Frame(Ecran)
InfosFrame.configure(bg="#757575") # Couleur du fond
InfosFrame.grid(row=1, column=0, pady=4)

# Nombre de mines sur le plateau (qui change en fonction des drapeaux)
nbrMine_label = Label(InfosFrame, text="Mines : " + str(nombreMineAPoser), font=helv18, bg="grey70")
nbrMine_label.grid(row=1, column=1)

# Plateau du jeu
Grille = Canvas(Ecran, width = grilleWidth, height = grilleHeight, bg = "black")

Grille.bind("<Button-1>", CliqueGaucheSurCellule) # evenement clic souris gauche
Grille.bind("<Button-3>", CliqueDroitSurCellule) # evenement clic souris droit

Grille.grid(row=2, column=0, padx=10, pady=8)

# Les boutons du jeu
ButtonFrame = Frame(Ecran)
ButtonFrame.configure(bg="#757575")
ButtonFrame.grid(row=3, column=0, pady=4, padx=4)

buttonTextColor = "White" # Couleur du texte des boutons
largeurBouton = 16 # Largeur des boutons

# Texte des boutons

# Difficulter
difficulterString = StringVar()
difficulterString.set(difficulterStringList[difficulter-1])

# Vitesse IA
IA_VitesseNom = StringVar()
IA_VitesseNom.set("Vitesse : " + IA_VitesseNomListe[IA_VitesseActuelle])

# IA activer ou non
IA_BoutonActiverOuNon = StringVar()
IA_BoutonActiverOuNon.set("IA : Désactiver")

# Bouton pour créer une nouvelle partie
NouvellePartie = Button(ButtonFrame, text = 'Nouvelle partie', bg = "#38A027", fg = buttonTextColor, width = largeurBouton, height = 2, takefocus = False, command = CreeNouvellePartie)
NouvellePartie.grid(row=1, column = 0, padx=10, pady=4)

# Bouton pour régler le niveau de difficulté
Difficulter = Button(ButtonFrame, textvariable = difficulterString, bg = "#4040D5", fg = buttonTextColor, width = largeurBouton, height = 2, takefocus = False, command = ChangeDifficulter)
Difficulter.grid(row=1, column = 1, padx=10, pady=4)

# Bouton pour quitter l'application
Quitter = Button(ButtonFrame, text = 'Quitter', bg = "#E82B2B", fg = buttonTextColor, width = largeurBouton, height = 2, takefocus = False, command = Ecran.destroy)
Quitter.grid(row=1, column = 4, padx=10, pady=4)

# Bouton pour activer l'IA
ActiverIA =  Button(ButtonFrame, textvariable = IA_BoutonActiverOuNon, bg = "#45B8AF", fg = buttonTextColor, width = largeurBouton, height = 2, takefocus = False, command = ActiverIA)
ActiverIA.grid(row=2, column = 0, padx=10, pady=4)

# Bouton pour régler la vitesse déexecution de l'IA
VitesseAI =  Button(ButtonFrame, textvariable = IA_VitesseNom, bg = "#B84599", fg = buttonTextColor, width = largeurBouton, height = 2, takefocus = False, command = IA_ChangementVitesse)
VitesseAI.grid(row=2, column = 1, padx=10, pady=4)

CreeNouvellePartie() # Lancement d'une partie lorsque lancement de l'app
Ecran.mainloop() # l'app tourne en boucle, attendant les interactions du joueur