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

def init_db():
    """Initialize the SQLite database for storing calculations"""
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

def dataFrame(fichier_excel):
    """Load Excel file and return DataFrame"""
    base_dir = os.path.dirname(__file__)
    recette = os.path.join(base_dir, 'recette', fichier_excel)
    df = pd.read_excel(recette)
    return df

def solvant_initial(df):
    """Extract initial solvent composition from DataFrame"""
    solvant_initial = {}
    for _, row in df.iterrows():
        if pd.notna(row['ComposantsSolvant']):
            solvant_initial[row['ComposantsSolvant']] = {
                "concL": row['concL'],
                "density": row['density'],
                "IR": row['IR']
            }
    return solvant_initial

def EcoAdds(df):
    """Extract EcoAdd additives data from DataFrame"""
    dfEcoAdds = df[['ComposantsEcoAdd', 'ecoAddH', 'ecoAddA', 'ecoAddS']].dropna()      
    dfEcoAdds = dfEcoAdds.set_index('ComposantsEcoAdd')  
    EcoAdds_dict = {}
    for index, row in dfEcoAdds.iterrows():
        EcoAdds_dict[index] = {
            'ecoAddH': row['ecoAddH'],
            'ecoAddA': row['ecoAddA'], 
            'ecoAddS': row['ecoAddS']
        }
    return EcoAdds_dict

def calculate_total_values(solvant_initial):
    """Calculate total theoretical density and IR values"""
    total_density = 0
    total_ir = 0
    for component in solvant_initial.values():
        total_density += component['density'] * component['concL']
        total_ir += component['IR'] * component['concL']
    print(f"Densité totale: {total_density:.5f}")
    print(f"IR total: {total_ir:.5f}")
    return total_density, total_ir

def etape_1(n, d, sI, eco_adds):
    """
    Step 1: Solve system of equations to find component concentrations.
    Handles both 3-component (without ETOH) and 4-component systems.
    """
    print("Etape 1: Résolution du système d'équations")
    try:
        # Check if ETOH is present in the solvent
        has_etoh = "ETOH" in sI
        
        if has_etoh:
            # 4-component system: correct for ethanol contribution
            print("Système à 4 composants avec ETOH")
            fraction_etoh = sI["ETOH"]["concL"]
            ir_corrige = n - (fraction_etoh * sI["ETOH"]["IR"])
            densite_corrigee = d - (fraction_etoh * sI["ETOH"]["density"])
            somme_fractions = 1.0 - fraction_etoh
            
            # Matrix for 3 remaining components
            A = np.array([
                [sI["ISOL"]["IR"], sI["BZOH"]["IR"], sI["DIPB"]["IR"]],
                [sI["ISOL"]["density"], sI["BZOH"]["density"], sI["DIPB"]["density"]],
                [1.0, 1.0, 1.0]
            ])
            
            b = np.array([ir_corrige, densite_corrigee, somme_fractions])
            
        else:
            # 3-component system: direct calculation
            print("Système à 3 composants sans ETOH")
            A = np.array([
                [sI["ISOL"]["IR"], sI["BZOH"]["IR"], sI["DIPB"]["IR"]],
                [sI["ISOL"]["density"], sI["BZOH"]["density"], sI["DIPB"]["density"]],
                [1.0, 1.0, 1.0]
            ])
            
            b = np.array([n, d, 1.0])
        
        # Solve the system
        solution = np.linalg.solve(A, b)
        isol, bzoh, dipb = solution
        
        print(f"Concentrations calculées - ISOL: {isol:.5f}, BZOH: {bzoh:.5f}, DIPB: {dipb:.5f}")
        
        # Proceed to step 2
        return etape_2(isol, bzoh, dipb, sI, eco_adds)

    except np.linalg.LinAlgError:
        raise Exception("Impossible de résoudre le système d'équations")
    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 1: {str(e)}")

def etape_2(x, y, z, sI, eco_adds):
    """
    Step 2: Determine which component is in excess by comparing current ratios with initial ratios.
    """
    print("Etape 2: Détermination du composant en excès")
    try:
        # Calculate initial ratios
        a = sI["ISOL"]["concL"] / sI["BZOH"]["concL"]
        b = sI["DIPB"]["concL"] / sI["BZOH"]["concL"]
        c = sI["DIPB"]["concL"] / sI["ISOL"]["concL"]

        # Calculate current ratios
        a_ = x/y
        b_ = z/y
        c_ = z/x

        print(f"Ratios initiaux - a: {a:.5f}, b: {b:.5f}, c: {c:.5f}")
        print(f"Ratios actuels - a': {a_:.5f}, b': {b_:.5f}, c': {c_:.5f}")

        # Determine excess component
        if a_ > a and c_ < c:
            print("ISOL est en excès")
            return etape_3(x, y, z, sI, "1", (a, b, c), (a_, b_, c_), eco_adds)
        elif a_ < a and b_ < b:
            print("BZOH est en excès")
            return etape_3(x, y, z, sI, "2", (a, b, c), (a_, b_, c_), eco_adds)
        elif b_ > b and c_ > c:
            print("DIPB est en excès")
            return etape_3(x, y, z, sI, "3", (a, b, c), (a_, b_, c_), eco_adds)
        else:
            raise Exception("Impossible de déterminer le composant en excès")

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 2: {str(e)}")

def etape_3(x, y, z, sI, ex, ABC, ABC_, eco_adds):
    """
    Step 3: Calculate required additive quantities to rebalance the solvent.
    Uses EcoAdds data from Excel file for additive concentrations.
    """
    print("Etape 3: Calcul des quantités d'additifs")
    try:
        additives = {}
        
        # Get EcoAdd concentrations from Excel data
        eco_add_1_conc = eco_adds.get('EcoAdd 1', {}).get('ecoAddH', 0.852)
        eco_add_2_conc = eco_adds.get('EcoAdd 2', {}).get('ecoAddA', 0.81)
        eco_add_3_conc = eco_adds.get('EcoAdd 3', {}).get('ecoAddS', 0.83)
        
        if ex == "1":  # ISOL en excès
            print("Calcul pour ISOL en excès")
            bzoh_cible = x / ABC[0]
            dipb_cible = ABC[2] * x
            delta_bzoh = bzoh_cible - y
            delta_dipb = dipb_cible - z
            
            if delta_bzoh > 0:
                additives["EcoAdd 2"] = delta_bzoh / eco_add_2_conc
            if delta_dipb > 0:
                additives["EcoAdd 3"] = delta_dipb / eco_add_3_conc
            
        elif ex == "2":  # BZOH en excès
            print("Calcul pour BZOH en excès")
            isol_cible = ABC[0] * y
            dipb_cible = ABC[1] * y
            delta_isol = isol_cible - x
            delta_dipb = dipb_cible - z
            
            if delta_isol > 0:
                additives["EcoAdd 1"] = delta_isol / eco_add_1_conc
            if delta_dipb > 0:
                additives["EcoAdd 3"] = delta_dipb / eco_add_3_conc
            
        elif ex == "3":  # DIPB en excès
            print("Calcul pour DIPB en excès")
            isol_cible = z / ABC[2]
            bzoh_cible = z / ABC[1]
            delta_isol = isol_cible - x
            delta_bzoh = bzoh_cible - y
            
            if delta_isol > 0:
                additives["EcoAdd 1"] = delta_isol / eco_add_1_conc
            if delta_bzoh > 0:
                additives["EcoAdd 2"] = delta_bzoh / eco_add_2_conc

        # Filter out zero or negative values
        additives = {k: v for k, v in additives.items() if v > 0}
        
        print(f"Additifs calculés: {additives}")
        return {"additives": additives}

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 3: {str(e)}")

@app.route('/calculate', methods=['POST'])
def calculate():
    """Main calculation endpoint"""
    try:
        data = request.get_json()
        densite = float(data['densite'])
        indice_refraction = float(data['refraction'])
        fichier_excel = str(data['fichier_excel'] + '.xlsx')

        # Load Excel data
        df = dataFrame(fichier_excel)
        
        # Get initial solvent data and EcoAdds data
        initial_solvent = solvant_initial(df)
        eco_adds_data = EcoAdds(df)
        
        print(f"Solvant initial: {initial_solvent}")
        print(f"EcoAdds data: {eco_adds_data}")
        
        # Calculate total theoretical values
        total_density, total_ir = calculate_total_values(initial_solvent)
        
        # Check if rebalancing is necessary
        if (abs(total_density - densite) < 0.005 and 
            abs(total_ir - indice_refraction) < 0.005):
            calculation_id = str(uuid.uuid4())
            return jsonify({
                "success": True,
                "message": "Le rééquilibrage n'est pas nécessaire",
                "calculationId": calculation_id
            })

        # Calculate result if rebalancing is needed
        result = etape_1(indice_refraction, densite, initial_solvent, eco_adds_data)

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

@app.route('/recette', methods=['GET'])
def liste_fichiers_recette():
    """Get list of available recipe files"""
    base_dir = os.path.dirname(__file__)
    dossier_recette = os.path.join(base_dir, 'recette')
    
    if not os.path.exists(dossier_recette):
        print(f"Le dossier {dossier_recette} n'existe pas.")
        return jsonify([])
    
    fichiers = os.listdir(dossier_recette)
    return jsonify(fichiers)

@app.route('/send_mail', methods=['POST'])
def send_mail():
    """Send calculation results via email"""
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)