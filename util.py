# =============================================================================
# UTILITAIRES POUR LA DÉTECTION DE COULEUR
# =============================================================================
# Fonctions helper pour calculer les limites HSV optimales
# =============================================================================

import numpy as np
import cv2


def get_limits(color):
    """
    Calcule les limites HSV pour la détection d'une couleur BGR.
    Gestion spéciale pour le rouge (teinte aux deux extrémités du spectre).
    
    Args:
        color: Couleur au format BGR [B, G, R]
    
    Returns:
        tuple: (limite_basse, limite_haute) au format HSV
    """
    c = np.uint8([[color]])  
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    
    hue = hsvC[0][0][0]
    
    # Gestion spéciale du rouge (teinte < 10 ou > 170)
    if hue < 10 or hue > 170:
        # Rouge : deux plages [0-10] et [170-180]
        lowerLimit1 = np.array([0, 50, 50], dtype=np.uint8)
        upperLimit1 = np.array([10, 255, 255], dtype=np.uint8)
        return lowerLimit1, upperLimit1
    else:
        # Autres couleurs : plage normale ±15
        lowerLimit = hue - 15, 50, 50
        upperLimit = hue + 15, 255, 255

        lowerLimit = np.array(lowerLimit, dtype=np.uint8)
        upperLimit = np.array(upperLimit, dtype=np.uint8)

        return lowerLimit, upperLimit
