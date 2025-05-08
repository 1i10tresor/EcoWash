from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import json

app = Flask(__name__)
CORS(app)

# === Données du solvant initial ===
def solvantInitial(fichier_excel):
    df = pd.read_excel(fichier_excel)
    solvant_initial = {}
    for _, row in df.iterrows():
        solvant_initial[row['Composant']] = {
            "concG": row['concG'],
            "density": row['density'],
            "IR": row['IR']
        }
    return solvant_initial

solvant_initial = solvantInitial('recette\\solvant_initial.xlsx')


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Point d'entrée principal de l'API Flask qui reçoit les données de densité et d'indice de réfraction.
    
    Returns:
        JSON: Un objet JSON contenant soit le résultat du calcul soit un message d'erreur
    """
    try:
        data = request.get_json()
        densite = data.get('densite')
        indice_refraction = data.get('refraction')
        
        # Lancement du processus de calcul
        result = etape_1(indice_refraction, densite, solvant_initial)
        return jsonify({"success": True, "result": result})
        
    except ValueError as e:
        return jsonify({"success": False, "error": "Valeurs numériques invalides"}), 400
    except KeyError as e:
        return jsonify({"success": False, "error": f"Champ manquant: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def etape_1(n, d, sI):
    """
    Étape 1: Résolution du système d'équations pour trouver les concentrations des composants.
    Corrige les valeurs mesurées en soustrayant la contribution de l'éthanol.
    
    Args:
        n (float): Indice de réfraction mesuré
        d (float): Densité mesurée
        sI (dict): Dictionnaire contenant les propriétés du solvant initial
    
    Returns:
        dict: Résultats des calculs avec les concentrations et les additifs nécessaires
    """
    try:
        # Correction pour l'éthanol
        fraction_etoh = sI["ETOH"]["concG"]
        ir_corrige = n - (fraction_etoh * sI["ETOH"]["IR"])
        densite_corrigee = d - (fraction_etoh * sI["ETOH"]["Density"])
        somme_fractions = 1.0 - fraction_etoh

        # Matrice du système d'équations
        A = np.array([
            [sI["ISOL"]["IR"], sI["BZOH"]["IR"], sI["DIPB"]["IR"]],
            [sI["ISOL"]["Density"], sI["BZOH"]["Density"], sI["DIPB"]["Density"]],
            [1.0, 1.0, 1.0]
        ])

        b = np.array([ir_corrige, densite_corrigee, somme_fractions])
        solution = np.linalg.solve(A, b)
        isol, bzoh, dipb = solution

        # Passage à l'étape 2 pour déterminer les excès
        return etape_2(isol, bzoh, dipb, sI)

    except np.linalg.LinAlgError:
        raise Exception("Impossible de résoudre le système d'équations")
    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 1: {str(e)}")

def etape_2(x, y, z, sI):
    """
    Étape 2: Détermine quel composant est en excès en comparant les ratios actuels avec les ratios initiaux.
    
    Args:
        x (float): Concentration de ISOL dans le mélange déséquilibré
        y (float): Concentration de BZOH dans le mélange déséquilibré
        z (float): Concentration de DIPB dans le mélange déséquilibré
        sI (dict): Dictionnaire contenant les propriétés du solvant initial
    
    Returns:
        dict: Résultats avec les concentrations et les quantités d'additifs nécessaires
    """
    try:
        # Calcul des ratios initiaux
        a = sI["ISOL"]["concG"] / sI["BZOH"]["concG"]
        b = sI["DIPB"]["concG"] / sI["BZOH"]["concG"]
        c = sI["DIPB"]["concG"] / sI["ISOL"]["concG"]

        # Calcul des ratios actuels
        a_ = x/y
        b_ = z/y
        c_ = z/x

        # Détermination du composant en excès
        if a_ > a and c_ < c:
            print("ISOL est en excès")
            return etape_3(x, y, z, sI, "1", (a, b, c), (a_, b_, c_))
        elif a_ < a and b_ < b:
            print("BZOH est en excès")
            return etape_3(x, y, z, sI, "2", (a, b, c), (a_, b_, c_))
        elif b_ > b and c_ > c:
            print("DIPB est en excès")
            return etape_3(x, y, z, sI, "3", (a, b, c), (a_, b_, c_))
        else:
            raise Exception("Impossible de déterminer le composant en excès")

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 2: {str(e)}")

def etape_3(x, y, z, sI, ex, ABC, ABC_):
    """
    Étape 3: Calcule les quantités d'additifs nécessaires pour rééquilibrer le solvant.
    
    Args:
        x, y, z (float): Concentrations des composants
        sI (dict): Propriétés du solvant initial
        ex (str): Identifiant du composant en excès ("1"=ISOL, "2"=BZOH, "3"=DIPB)
        ABC (tuple): Ratios initiaux (a, b, c)
        ABC_ (tuple): Ratios actuels (a_, b_, c_)
    
    Returns:
        dict: Dictionnaire contenant les fractions et les quantités d'additifs
    """
    try:
        additives = {"EcoAdd1": 0, "EcoAdd2": 0, "EcoAdd3": 0}
        
        if ex == "1":  # ISOL en excès
            bzoh_cible = x / ABC[0]
            dipb_cible = ABC[2] * x
            delta_bzoh = bzoh_cible - y
            delta_dipb = dipb_cible - z
            additives["EcoAdd2"] = delta_bzoh / 0.81  # 0.81 = concentration de BZOH pur
            additives["EcoAdd3"] = delta_dipb / 0.83   # 0.83 = concentration de DIPB pur
            
        elif ex == "2":  # BZOH en excès
            isol_cible = ABC_[0] * y
            dipb_cible = ABC[1] * y
            delta_isol = isol_cible - x
            delta_dipb = dipb_cible - z
            additives["EcoAdd1"] = delta_isol / 0.852  # 0.852 = concentration de ISOL pur
            additives["EcoAdd3"] = delta_dipb / 0.83
            
        elif ex == "3":  # DIPB en excès
            isol_cible = z / ABC[2]
            bzoh_cible = z / ABC[1]
            delta_isol = isol_cible - x
            delta_bzoh = bzoh_cible - y
            additives["EcoAdd1"] = delta_isol / 0.852
            additives["EcoAdd2"] = delta_bzoh / 0.81

        return {
            "fractions": {
                "ISOL": float(x),
                "BZOH": float(y),
                "DIPB": float(z),
                "ETOH": float(sI["ETOH"]["concG"])
            },
            "additives": additives
        }

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 3: {str(e)}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)