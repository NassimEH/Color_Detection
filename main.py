# =============================================================================
# DÉTECTEUR DE COULEUR - ROUGE, BLEU, VERT
# =============================================================================
# Ce programme détecte les 3 couleurs primaires (Rouge, Bleu, Vert) 
# en temps réel via la caméra.
# 
# FONCTIONNEMENT :
# 1. Interface de sélection de couleur (Rouge/Bleu/Vert)
# 2. Conversion BGR → HSV pour une détection optimale
# 3. Masquage et détection des zones colorées
# 4. Affichage avec rectangle de détection
# =============================================================================

import cv2          # OpenCV - bibliothèque de vision par ordinateur
from PIL import Image    # Pillow - traitement d'images Python
import numpy as np       # NumPy - calculs numériques et tableaux
import tkinter as tk     # Interface graphique utilisateur
from tkinter import ttk  # Widgets avancés de tkinter
from tkinter import messagebox  # Boîtes de dialogue

from util import get_limits  # Fonction personnalisée pour calculer les limites HSV


# =============================================================================
# INTERFACE DE SÉLECTION - 3 COULEURS PRIMAIRES
# =============================================================================
def select_color():
    """Interface pour choisir entre Rouge, Bleu ou Vert"""
    
    # =========================================================================
    # DÉFINITION DES 3 COULEURS PRINCIPALES (ROUGE, BLEU, VERT)
    # =========================================================================
    # BGR = Blue, Green, Red (format utilisé par OpenCV)
    # Seulement les 3 couleurs primaires pour une détection optimale
    # =========================================================================
    colors = {
        "Rouge": [0, 0, 200],        # Rouge pur - gestion spéciale HSV
        "Bleu": [180, 60, 0],        # Bleu avec composante verte pour meilleure détection
        "Vert": [0, 180, 0],         # Vert pur
    }
    
    selected_color = None  # Variable pour stocker la couleur choisie
    
    # =========================================================================
    # FONCTIONS DE GESTION DES ÉVÉNEMENTS (CALLBACKS)
    # =========================================================================
    # Ces fonctions sont appelées quand l'utilisateur clique sur les boutons
    # =========================================================================
    
    def on_start():
        """Fonction appelée quand l'utilisateur clique sur 'Commencer'"""
        nonlocal selected_color  # Permet de modifier la variable externe
        color_name = combo_var.get()  # Récupère le nom de couleur sélectionné
        if color_name in colors:
            selected_color = colors[color_name]  # Récupère les valeurs BGR
            root.quit()  # Ferme la fenêtre de sélection
        else:
            messagebox.showwarning("Attention", "Veuillez sélectionner une couleur!")
    
    def on_cancel():
        """Fonction appelée quand l'utilisateur clique sur 'Annuler'"""
        root.quit()  # Ferme la fenêtre
        exit()       # Termine le programme
    
    # =========================================================================
    # CRÉATION DE L'INTERFACE GRAPHIQUE AVEC TKINTER
    # =========================================================================
    # Tkinter est la bibliothèque standard Python pour créer des interfaces
    # =========================================================================
    
    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("Sélection de couleur - Détecteur")
    root.geometry("350x200")      # Taille de la fenêtre
    root.resizable(False, False)  # Empêche le redimensionnement
    
    # Centrer la fenêtre sur l'écran
    root.eval('tk::PlaceWindow . center')
    
    # Titre principal de la fenêtre
    title_label = tk.Label(root, text="Détecteur RGB", 
                          font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    # Texte d'instructions pour l'utilisateur
    instruction_label = tk.Label(root, text="Choisissez une couleur primaire:", 
                                font=("Arial", 10))
    instruction_label.pack(pady=5)
    
    # =========================================================================
    # LISTE DÉROULANTE (COMBOBOX) POUR SÉLECTIONNER LA COULEUR
    # =========================================================================
    # La Combobox permet à l'utilisateur de choisir parmi les options prédéfinies
    # =========================================================================
    combo_var = tk.StringVar()  # Variable pour stocker la sélection
    combo = ttk.Combobox(root, textvariable=combo_var, 
                        values=list(colors.keys()),  # Liste des noms de couleurs
                        state="readonly", width=15)  # readonly = pas de saisie libre
    combo.pack(pady=10)
    combo.set("Rouge")  # Valeur sélectionnée par défaut
    
    # =========================================================================
    # CRÉATION DES BOUTONS D'ACTION
    # =========================================================================
    # Les boutons permettent à l'utilisateur de valider ou annuler sa sélection
    # =========================================================================
    button_frame = tk.Frame(root)  # Conteneur pour organiser les boutons
    button_frame.pack(pady=20)
    
    # Bouton pour démarrer la détection
    start_button = tk.Button(button_frame, text="Commencer la détection", 
                           command=on_start, bg="#4CAF50", fg="white",
                           font=("Arial", 10, "bold"))
    start_button.pack(side=tk.LEFT, padx=10)  # Alignement à gauche
    
    # Bouton pour annuler et quitter
    cancel_button = tk.Button(button_frame, text="Annuler", 
                            command=on_cancel, bg="#f44336", fg="white")
    cancel_button.pack(side=tk.LEFT, padx=10)  # Alignement à gauche
    
    # =========================================================================
    # LANCEMENT DE L'INTERFACE ET RÉCUPÉRATION DU RÉSULTAT
    # =========================================================================
    root.mainloop()  # Affiche la fenêtre et attend l'interaction utilisateur
    root.destroy()   # Détruit la fenêtre après utilisation
    
    return selected_color  # Retourne la couleur sélectionnée (ou None)


# =============================================================================
# FONCTION DE DÉTECTION PRINCIPALE
# =============================================================================
def start_detection(color_to_detect, color_name):
    """Détection en temps réel de la couleur sélectionnée"""
    print(f"Couleur sélectionnée: {color_name}")
    print("Couleur à détecter (BGR):", color_to_detect)

    # =========================================================================
    # INITIALISATION DE LA CAMÉRA
    # =========================================================================
    # OpenCV utilise VideoCapture pour accéder à la caméra
    # L'index 0 correspond généralement à la caméra par défaut
    # =========================================================================
    cap = cv2.VideoCapture(0)

    # =========================================================================
    # GESTION DES ERREURS DE CAMÉRA
    # =========================================================================
    # Si la caméra par défaut ne fonctionne pas, essayer d'autres indices
    # Certains ordinateurs ont plusieurs caméras (webcam, caméra intégrée, etc.)
    # =========================================================================
    if not cap.isOpened():
        print("Essai d'autres indices de caméra...")
        for i in range(1, 5):  # Teste les indices 1, 2, 3, 4
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Caméra trouvée à l'index {i}")
                break
        else:
            print("Aucune caméra trouvée")
            return  # Sort de la fonction si aucune caméra n'est disponible

    # =========================================================================
    # TEST DE CONVERSION BGR → HSV
    # =========================================================================
    # Affiche les valeurs HSV pour vérification et débogage
    # HSV = Hue (teinte), Saturation, Value (luminosité)
    # HSV est plus efficace que BGR pour la détection de couleurs
    # =========================================================================
    print("Conversion en HSV pour test:")
    test_color = np.uint8([[color_to_detect]])  # Format attendu par OpenCV
    hsv_test = cv2.cvtColor(test_color, cv2.COLOR_BGR2HSV)
    print("HSV:", hsv_test[0][0])

    # =========================================================================
    # BOUCLE PRINCIPALE DE DÉTECTION EN TEMPS RÉEL
    # =========================================================================
    # Cette boucle capture et traite les images de la caméra en continu
    # jusqu'à ce que l'utilisateur appuie sur 'q' pour quitter
    # =========================================================================
    while True:
        # =====================================================================
        # CAPTURE D'UNE IMAGE DE LA CAMÉRA
        # =====================================================================
        ret, frame = cap.read()  # ret = succès, frame = image capturée
        
        # =====================================================================
        # CONVERSION BGR → HSV POUR LA DÉTECTION
        # =====================================================================
        # HSV sépare la couleur (teinte) de la luminosité, rendant la détection
        # plus robuste aux changements d'éclairage
        # =====================================================================
        hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # =====================================================================
        # CALCUL DES LIMITES DE DÉTECTION
        # =====================================================================
        # La fonction get_limits() (dans util.py) calcule une plage de valeurs
        # HSV autour de la couleur cible pour une détection flexible
        # =====================================================================
        lowerLimit, upperLimit = get_limits(color=color_to_detect)

        # =====================================================================
        # CRÉATION DU MASQUE DE COULEUR (AVEC GESTION SPÉCIALE POUR LE ROUGE)
        # =====================================================================
        # cv2.inRange() crée un masque binaire (noir/blanc) où les pixels
        # blancs correspondent à la couleur recherchée
        # 
        # GESTION SPÉCIALE DU ROUGE :
        # Le rouge en HSV se trouve aux deux extrémités (0-10 et 170-180)
        # On doit donc créer deux masques et les combiner
        # =====================================================================
        if color_name == "Rouge":
            # Première plage du rouge (0-10)
            mask1 = cv2.inRange(hsvImage, np.array([0, 50, 50]), np.array([10, 255, 255]))
            # Deuxième plage du rouge (170-180)
            mask2 = cv2.inRange(hsvImage, np.array([170, 50, 50]), np.array([180, 255, 255]))
            # Combinaison des deux masques
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            # Pour toutes les autres couleurs
            mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

        # =====================================================================
        # DÉTECTION DE LA ZONE ENGLOBANTE (BOUNDING BOX)
        # =====================================================================
        # PIL.Image.getbbox() trouve le rectangle minimal qui englobe
        # tous les pixels détectés (blancs dans le masque)
        # =====================================================================
        mask_ = Image.fromarray(mask)  # Conversion pour PIL
        bbox = mask_.getbbox()         # Coordonnées du rectangle englobant

        # =====================================================================
        # DESSIN DU RECTANGLE DE DÉTECTION
        # =====================================================================
        # Si une zone colorée est détectée, dessiner un rectangle vert autour
        # =====================================================================
        if bbox is not None:  # Si quelque chose a été détecté
            x1, y1, x2, y2 = bbox  # Coordonnées du rectangle
            # Dessiner un rectangle vert avec une épaisseur de 5 pixels
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

        # =====================================================================
        # AFFICHAGE DU RÉSULTAT
        # =====================================================================
        # Affiche l'image avec la détection en temps réel
        # Le titre de la fenêtre indique la couleur recherchée
        # =====================================================================
        cv2.imshow(f'Detection de {color_name} (appuyer sur q pour quitter)', frame)

        # =====================================================================
        # GESTION DE LA SORTIE DU PROGRAMME
        # =====================================================================
        # Vérifie si l'utilisateur a appuyé sur la touche 'q' pour quitter
        # =====================================================================
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  # Sort de la boucle while

    # =========================================================================
    # NETTOYAGE DES RESSOURCES
    # =========================================================================
    # Libère la caméra et ferme toutes les fenêtres OpenCV
    # Important pour éviter les conflits avec d'autres applications
    # =========================================================================
    cap.release()           # Libère la caméra
    cv2.destroyAllWindows() # Ferme toutes les fenêtres OpenCV


# =============================================================================
# PROGRAMME PRINCIPAL - POINT D'ENTRÉE
# =============================================================================
# Cette section orchestre le programme complet :
# 1. Lance l'interface de sélection
# 2. Récupère la couleur choisie
# 3. Démarre la détection en temps réel
# =============================================================================


# Programme principal
if __name__ == "__main__":
    # =========================================================================
    # ÉTAPE 1 : SÉLECTION DE LA COULEUR PAR L'UTILISATEUR
    # =========================================================================
    # Lance l'interface graphique pour que l'utilisateur choisisse une couleur
    # =========================================================================
    selected_color = select_color()
    
    # =========================================================================
    # ÉTAPE 2 : VÉRIFICATION ET TRAITEMENT DE LA SÉLECTION
    # =========================================================================
    if selected_color is not None:  # Si l'utilisateur a choisi une couleur
        
        # =====================================================================
        # DICTIONNAIRE DES 3 COULEURS PRINCIPALES
        # =====================================================================
        colors = {
            "Rouge": [0, 0, 200],        # Rouge pur - gestion spéciale HSV
            "Bleu": [180, 60, 0],        # Bleu avec composante verte pour meilleure détection
            "Vert": [0, 180, 0],         # Vert pur
        }
        
        # =====================================================================
        # RECHERCHE DU NOM DE COULEUR CORRESPONDANT
        # =====================================================================
        # Parcourt le dictionnaire pour trouver quel nom correspond aux valeurs BGR
        # =====================================================================
        color_name = "Inconnue"  # Valeur par défaut
        for name, bgr in colors.items():
            if bgr == selected_color:  # Comparaison des listes BGR
                color_name = name
                break  # Sort de la boucle dès qu'on trouve une correspondance
        
        # =====================================================================
        # ÉTAPE 3 : LANCEMENT DE LA DÉTECTION
        # =====================================================================
        # Démarre le processus de détection en temps réel avec la couleur choisie
        # =====================================================================
        start_detection(selected_color, color_name)
        
    else:
        # =====================================================================
        # GESTION DU CAS OÙ L'UTILISATEUR ANNULE
        # =====================================================================
        print("Aucune couleur sélectionnée - Programme terminé")


# =============================================================================
# FIN DU PROGRAMME
# =============================================================================
# 
# RÉSUMÉ DU FONCTIONNEMENT COMPLET :
# 
# 1. L'utilisateur lance le programme
# 2. Une interface graphique s'ouvre pour choisir une couleur
# 3. Le programme initialise la caméra
# 4. Pour chaque image de la caméra :
#    - Conversion BGR → HSV pour une meilleure détection
#    - Création d'un masque pour isoler la couleur choisie
#    - Détection de la zone englobante des pixels colorés
#    - Dessin d'un rectangle vert autour des objets détectés
# 5. Affichage en temps réel jusqu'à ce que l'utilisateur appuie sur 'q'
# 6. Nettoyage et fermeture propre du programme
# 
# TECHNOLOGIES UTILISÉES :
# - OpenCV : Vision par ordinateur et traitement d'images
# - Tkinter : Interface graphique utilisateur
# - NumPy : Calculs numériques optimisés
# - PIL : Traitement d'images Python
# 
# =============================================================================
