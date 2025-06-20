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
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

def init_db():
    """Initialize the SQLite database for storing calculations"""
    db_path = os.getenv('DATABASE_PATH', 'calculations.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id TEXT PRIMARY KEY,
            model TEXT,
            measurement_type TEXT,
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
    """Extract initial solvent composition from DataFrame using dynamic component names"""
    solvant_initial = {}
    for _, row in df.iterrows():
        if pd.notna(row['ComposantsSolvant']):
            component_name = row['ComposantsSolvant']
            solvant_initial[component_name] = {
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
    Handles both 3-component and 4-component systems with exact formulas.
    """
    print("Etape 1: Résolution du système d'équations")
    try:
        # Check if compo4 is present in the solvent
        has_compo4 = "compo4" in sI
        
        if has_compo4:
            # 4-component system with fixed compo4 concentration
            print("Système à 4 composants avec compo4")
            fixed_compo4_conc = 0.0092
            
            # Get compo4 properties
            d4 = sI["compo4"]["density"]
            n4 = sI["compo4"]["IR"]
            
            # Calculate corrected values
            # d = d1*x1 + d2*x2 + d3*x3 + d4*0.0092
            # n = n1*x1 + n2*x2 + n3*x3 + n4*0.0092
            # 1 = x1 + x2 + x3 + 0.0092
            densite_corrigee = d - (d4 * fixed_compo4_conc)
            ir_corrige = n - (n4 * fixed_compo4_conc)
            somme_fractions_corrigee = 1.0 - fixed_compo4_conc
            
            # Matrix for 3 remaining components (compo1, compo2, compo3)
            A = np.array([
                [sI["compo1"]["IR"], sI["compo2"]["IR"], sI["compo3"]["IR"]],
                [sI["compo1"]["density"], sI["compo2"]["density"], sI["compo3"]["density"]],
                [1.0, 1.0, 1.0]
            ])
            
            b = np.array([ir_corrige, densite_corrigee, somme_fractions_corrigee])
            
        else:
            # 3-component system: direct calculation
            print("Système à 3 composants sans compo4")
            # d = d1*x1 + d2*x2 + d3*x3
            # n = n1*x1 + n2*x2 + n3*x3
            # 1 = x1 + x2 + x3
            A = np.array([
                [sI["compo1"]["IR"], sI["compo2"]["IR"], sI["compo3"]["IR"]],
                [sI["compo1"]["density"], sI["compo2"]["density"], sI["compo3"]["density"]],
                [1.0, 1.0, 1.0]
            ])
            
            b = np.array([n, d, 1.0])
        
        # Solve the system
        solution = np.linalg.solve(A, b)
        compo1, compo2, compo3 = solution
        
        print(f"Concentrations calculées - compo1: {compo1:.6f}, compo2: {compo2:.6f}, compo3: {compo3:.6f}")
        
        # Proceed to step 2
        return etape_2(compo1, compo2, compo3, sI, eco_adds)

    except np.linalg.LinAlgError:
        raise Exception("Impossible de résoudre le système d'équations")
    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 1: {str(e)}")

def etape_2(x, y, z, sI, eco_adds):
    """
    Step 2: Determine which component is in excess by comparing current ratios with initial ratios.
    Updated to use compo1, compo2, compo3 naming.
    """
    print("Etape 2: Détermination du composant en excès")
    try:
        # Calculate initial ratios
        a = sI["compo1"]["concL"] / sI["compo2"]["concL"]
        b = sI["compo3"]["concL"] / sI["compo2"]["concL"]
        c = sI["compo3"]["concL"] / sI["compo1"]["concL"]

        # Calculate current ratios
        a_ = x/y
        b_ = z/y
        c_ = z/x

        print(f"Ratios initiaux - a: {a:.5f}, b: {b:.5f}, c: {c:.5f}")
        print(f"Ratios actuels - a': {a_:.5f}, b': {b_:.5f}, c': {c_:.5f}")

        # Determine excess component
        if a_ > a and c_ < c:
            print("compo1 est en excès")
            return etape_3(x, y, z, sI, "1", (a, b, c), (a_, b_, c_), eco_adds)
        elif a_ < a and b_ < b:
            print("compo2 est en excès")
            return etape_3(x, y, z, sI, "2", (a, b, c), (a_, b_, c_), eco_adds)
        elif b_ > b and c_ > c:
            print("compo3 est en excès")
            return etape_3(x, y, z, sI, "3", (a, b, c), (a_, b_, c_), eco_adds)
        else:
            raise Exception("Impossible de déterminer le composant en excès")

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 2: {str(e)}")

def etape_3(x, y, z, sI, ex, ABC, ABC_, eco_adds):
    """
    Step 3: Calculate required additive quantities to rebalance the solvent.
    Updated to use compo1, compo2, compo3 naming.
    Uses EcoAdds data from Excel file for additive concentrations.
    """
    print("Etape 3: Calcul des quantités d'additifs")
    try:
        additives = {}
        
        # Get EcoAdd concentrations from Excel data
        eco_add_1_conc = eco_adds.get('EcoAdd 1', {}).get('ecoAddH', 0.852)
        eco_add_2_conc = eco_adds.get('EcoAdd 2', {}).get('ecoAddA', 0.81)
        eco_add_3_conc = eco_adds.get('EcoAdd 3', {}).get('ecoAddS', 0.83)
        
        if ex == "1":  # compo1 en excès
            print("Calcul pour compo1 en excès")
            compo2_cible = x / ABC[0]
            compo3_cible = ABC[2] * x
            delta_compo2 = compo2_cible - y
            delta_compo3 = compo3_cible - z
            
            if delta_compo2 > 0:
                additives["EcoAdd 2"] = delta_compo2 / eco_add_2_conc
            if delta_compo3 > 0:
                additives["EcoAdd 3"] = delta_compo3 / eco_add_3_conc
            
        elif ex == "2":  # compo2 en excès
            print("Calcul pour compo2 en excès")
            compo1_cible = ABC[0] * y
            compo3_cible = ABC[1] * y
            delta_compo1 = compo1_cible - x
            delta_compo3 = compo3_cible - z
            
            if delta_compo1 > 0:
                additives["EcoAdd 1"] = delta_compo1 / eco_add_1_conc
            if delta_compo3 > 0:
                additives["EcoAdd 3"] = delta_compo3 / eco_add_3_conc
            
        elif ex == "3":  # compo3 en excès
            print("Calcul pour compo3 en excès")
            compo1_cible = z / ABC[2]
            compo2_cible = z / ABC[1]
            delta_compo1 = compo1_cible - x
            delta_compo2 = compo2_cible - y
            
            if delta_compo1 > 0:
                additives["EcoAdd 1"] = delta_compo1 / eco_add_1_conc
            if delta_compo2 > 0:
                additives["EcoAdd 2"] = delta_compo2 / eco_add_2_conc

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
        db_path = os.getenv('DATABASE_PATH', 'calculations.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO calculations (
                id, model, measurement_type, density, 
                refraction, result, calculation_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            calculation_id,
            data['fichier_excel'],
            data.get('choix', ''),
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
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Aucune donnée reçue"}), 400
        
        # Check required fields
        required_fields = ['email', 'donnees', 'resultats']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Champ manquant: {field}"}), 400
        
        recipient_email = data['email']
        form_data = data['donnees']
        results = data['resultats']
        calc_id = data.get('calculationId', 'N/A')
        
        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, recipient_email):
            return jsonify({"success": False, "error": "Format d'email invalide"}), 400
        
        # Validate that we have results to send
        if not results or len(results) == 0:
            return jsonify({"success": False, "error": "Aucun résultat à envoyer"}), 400
        
        # Format the email body
        today = datetime.now().strftime("%d/%m/%Y à %H:%M")
        body = f"""Bonjour,

Voici les résultats de votre calcul Ecowash effectué le {today}.

ID du calcul: {calc_id}

Données saisies:
- Modèle: {form_data.get('modele', 'N/A')}
- Densité: {form_data.get('densite', 'N/A')}
- Réfraction: {form_data.get('refraction', 'N/A')}

Résultats - Additifs à ajouter:
"""
        
        for product, value in results.items():
            body += f"- {value:.5f} de {product}\n"

        body += f"""

Addition for 100 units (by volume) of solvent to be corrected.

Cordialement,
L'équipe Spring Coating Systems

---
Ce message a été généré automatiquement par le système Ecowash.
Pour toute question, contactez-nous à ecowash@spring-coating.com
"""

        # Get email credentials from environment variables
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_user or not email_password:
            print("Erreur: Variables d'environnement EMAIL_USER ou EMAIL_PASSWORD manquantes")
            return jsonify({"success": False, "error": "Configuration email manquante"}), 500

        # Initialize yagmail with error handling
        try:
            yag = yagmail.SMTP(email_user, email_password)
        except Exception as e:
            print(f"Erreur de connexion SMTP: {str(e)}")
            return jsonify({"success": False, "error": "Erreur de configuration email"}), 500
        
        # Send email
        try:
            subject = f"Résultat correction Ecowash du {today.split(' à ')[0]}"
            yag.send(to=recipient_email, subject=subject, contents=body)
            yag.close()
        except Exception as e:
            print(f"Erreur d'envoi email: {str(e)}")
            return jsonify({"success": False, "error": f"Erreur d'envoi: {str(e)}"}), 500

        # Update database with email information
        if calc_id and calc_id != 'N/A':
            try:
                db_path = os.getenv('DATABASE_PATH', 'calculations.db')
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute('''
                    UPDATE calculations 
                    SET email = ?, sent_email = TRUE 
                    WHERE id = ?
                ''', (recipient_email, calc_id))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Erreur de mise à jour base de données: {str(e)}")
                # Don't fail the request if database update fails
        
        return jsonify({"success": True, "message": "Email envoyé avec succès"})
        
    except Exception as e:
        print(f"Erreur générale dans send_mail: {str(e)}")
        return jsonify({"success": False, "error": f"Erreur interne: {str(e)}"}), 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)