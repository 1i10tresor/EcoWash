import pandas as pd
import os
import numpy as np

def liste_fichiers_recette():
    base_dir = os.path.dirname(__file__)  # Répertoire du script actuel
    dossier_recette = os.path.join(base_dir, 'recette')  # Chemin vers le dossier "recette"
    
    # Vérifier si le dossier existe
    if not os.path.exists(dossier_recette):
        print(f"Le dossier {dossier_recette} n'existe pas.")
        return []
    
    # Lister les fichiers
    fichiers = os.listdir(dossier_recette)
    return fichiers