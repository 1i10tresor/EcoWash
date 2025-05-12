import numpy as np
import pandas as pd
import os 

def solvantInitial(fichier_excel):

    base_dir = os.path.dirname(__file__)  # Répertoire du script actuel
    recette = os.path.join(base_dir, 'recette',fichier_excel)  # Chemin vers le dossier "recette"
    df = pd.read_excel(recette)
    solvant_initial = {}
    for _, row in df.iterrows():
        solvant_initial[row['Composant']] = {
            "concG": row['concG'],
            "density": row['density'],
            "IR": row['IR']
        }
    return solvant_initial

print(solvantInitial('EcoWash - 1B.xlsx'))