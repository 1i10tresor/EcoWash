from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import json
import os
import yagmail
from datetime import datetime
import sqlite3
import uuid

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id TEXT PRIMARY KEY,
            model TEXT,
            measurement_type TEXT,
            lot_number INTEGER,
            density REAL,
            refraction REAL,
            result TEXT,
            calculation_date TIMESTAMP,
            email TEXT,
            sent_email BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# === Données du solvant initial ===
def solvantInitial(fichier_excel):
    print("Lancement de la fonction solvantInitial")
    base_dir = os.path.dirname(__file__)
    print(base_dir)
    recette = os.path.join(base_dir, 'recette',fichier_excel)
    df = pd.read_excel(recette)
    solvant_initial = {}
    print("middle")
    for _, row in df.iterrows():
        solvant_initial[row['Composant']] = {
            "concL": row['concL'],
            "density": row['density'],
            "IR": row['IR']
        }
    return solvant_initial

def calculate_total_values(solvant_initial):
    total_density = 0
    total_ir = 0
    
    for component in solvant_initial.values():
        total_density += component['density'] * component['concL']
        total_ir += component['IR'] * component['concL']
    
    print(f"Valeurs totales du mélange initial:")
    print(f"Densité totale: {total_density:.5f}")
    print(f"IR total: {total_ir:.5f}")
    
    return total_density, total_ir

@app.route('/send_mail', methods=['POST'])
def send_mail():
    try:
        data = request.get_json()
        recipient_email = data['email']
        form_data = data['donnees']
        results = data['resultats']
        calc_id = data.get('calculationId')
        
        # Format the email body
        today = datetime.now().strftime("%d/%m/%Y")
        body = f"""
        Calcul ID: {calc_id}

        Données du formulaire:
        - Modèle: {form_data['modele']}
        - Type de mesure: {form_data['choix']}
        - Nombre de lots: {form_data['nb_lots']}
        - Densité: {form_data['densite']}
        - Réfraction: {form_data['refraction']}
        
        Résultats:
        """
        for product, value in results.items():
            body += f"- Ajouter {value:.7f} d'{product}\n"

        # Initialize yagmail
        yag = yagmail.SMTP('test.prog.recup@gmail.com', 'bageklcszxvknxdh')
        
        # Send email
        subject = f"Résultat correction EcoWash du {today}"
        yag.send(to=recipient_email, subject=subject, contents=body)

        # Update database with email information
        if calc_id:
            conn = sqlite3.connect('calculations.db')
            c = conn.cursor()
            c.execute('''
                UPDATE calculations 
                SET email = ?, sent_email = TRUE 
                WHERE id = ?
            ''', (recipient_email, calc_id))
            conn.commit()
            conn.close()
        
        return jsonify({"success": True, "message": "Email sent successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        densite = float(data['densite'])
        indice_refraction = float(data['refraction'])
        fichier_excel = str(data['fichier_excel']+'.xlsx')

        # Get initial solvent data
        initial_solvent = solvantInitial(fichier_excel)
        
        # Calculate total theoretical values
        total_density, total_ir = calculate_total_values(initial_solvent)
        
        # Check if rebalancing is necessary
        if (abs(total_density - densite) < 0.005 and 
            abs(total_ir - indice_refraction) < 0.005):
            return jsonify({
                "success": True,
                "message": "Le rééquilibrage n'est pas nécessaire",
                "calculationId": str(uuid.uuid4())
            })

        # Calculate result if rebalancing is needed
        result = etape_1(indice_refraction, densite, initial_solvent)

        # Generate unique ID
        calculation_id = str(uuid.uuid4())

        # Store calculation in database
        conn = sqlite3.connect('calculations.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO calculations (
                id, model, measurement_type, lot_number, density, 
                refraction, result, calculation_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            calculation_id,
            data['fichier_excel'],
            data.get('choix', ''),
            data.get('nb_lots', 0),
            densite,
            indice_refraction,
            json.dumps(result),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "result": result,
            "calculationId": calculation_id
        })
        
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
    """
    print("Etape 1 done")
    try:
        print("Correction des valeurs mesurées")
        # Correction pour l'éthanol
        fraction_etoh = sI["ETOH"]["concL"]
        ir_corrige = n - (fraction_etoh * sI["ETOH"]["IR"])
        densite_corrigee = d - (fraction_etoh * sI["ETOH"]["density"])
        somme_fractions = 1.0 - fraction_etoh

        # Matrice du système d'équations
        A = np.array([
            [sI["ISOL"]["IR"], sI["BZOH"]["IR"], sI["DIPB"]["IR"]],
            [sI["ISOL"]["density"], sI["BZOH"]["density"], sI["DIPB"]["density"]],
            [1.0, 1.0, 1.0]
        ])

        b = np.array([ir_corrige, densite_corrigee, somme_fractions])
        solution = np.linalg.solve(A, b)
        isol, bzoh, dipb = solution

        print("système d'équations résolu")

        # Passage à l'étape 2 pour déterminer les excès
        return etape_2(isol, bzoh, dipb, sI)

    except np.linalg.LinAlgError:
        raise Exception("Impossible de résoudre le système d'équations")
    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 1: {str(e)}")

def etape_2(x, y, z, sI):
    """
    Étape 2: Détermine quel composant est en excès en comparant les ratios actuels avec les ratios initiaux.
    """
    print("Etape 2 done")
    try:
        # Calcul des ratios initiaux
        a = sI["ISOL"]["concL"] / sI["BZOH"]["concL"]
        b = sI["DIPB"]["concL"] / sI["BZOH"]["concL"]
        c = sI["DIPB"]["concL"] / sI["ISOL"]["concL"]

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
    """
    print("Etape 3 done")
    try:
        additives = {"EcoAdd1": 0, "EcoAdd2": 0, "EcoAdd3": 0}
        
        if ex == "1":  # ISOL en excès
            bzoh_cible = x / ABC[0]
            dipb_cible = ABC[2] * x
            delta_bzoh = bzoh_cible - y
            delta_dipb = dipb_cible - z
            additives["EcoAdd 2"] = delta_bzoh / 0.81
            additives["EcoAdd 3"] = delta_dipb / 0.83
            
        elif ex == "2":  # BZOH en excès
            isol_cible = ABC_[0] * y
            dipb_cible = ABC[1] * y
            delta_isol = isol_cible - x
            delta_dipb = dipb_cible - z
            additives["EcoAdd 1"] = delta_isol / 0.852
            additives["EcoAdd 3"] = delta_dipb / 0.83
            
        elif ex == "3":  # DIPB en excès
            isol_cible = z / ABC[2]
            bzoh_cible = z / ABC[1]
            delta_isol = isol_cible - x
            delta_bzoh = bzoh_cible - y
            additives["EcoAdd 1"] = delta_isol / 0.852
            additives["EcoAdd 2"] = delta_bzoh / 0.81

        return {
            "additives": additives
        }

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 3: {str(e)}")
    
@app.route('/recette', methods=['GET'])
def liste_fichiers_recette():
    base_dir = os.path.dirname(__file__)
    dossier_recette = os.path.join(base_dir, 'recette')
    
    if not os.path.exists(dossier_recette):
        print(f"Le dossier {dossier_recette} n'existe pas.")
        return []
    
    fichiers = os.listdir(dossier_recette)
    return fichiers

if __name__ == '__main__':
    app.run(port=5000, debug=True)