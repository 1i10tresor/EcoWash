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

# Configuration pour le préfixe API
API_PREFIX = '/api'

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

def get_confidence_interval():
    """Récupère la valeur d'intervalle de confiance depuis le fichier Excel"""
    try:
        base_dir = os.path.dirname(__file__)
        confidence_file = os.path.join(base_dir, 'intervalleConfiance.xlsx')
        
        # Vérifier que le fichier existe
        if not os.path.exists(confidence_file):
            print(f"Attention: Le fichier intervalleConfiance.xlsx n'existe pas. Utilisation de la valeur par défaut 0.005")
            print(f"DEBUG: Intervalle de confiance utilisé (défaut): 0.005")
            return 0.005
        
        try:
            # Lire le fichier Excel
            df = pd.read_excel(confidence_file, header=None)
            
            # Récupérer la valeur en A2 (ligne 1, colonne 0 en indexation pandas)
            if len(df) > 1 and len(df.columns) > 0:
                confidence_value = df.iloc[1, 0]  # A2 correspond à ligne 1, colonne 0
                
                # Vérifier que c'est un nombre valide
                if pd.notna(confidence_value) and isinstance(confidence_value, (int, float)):
                    print(f"Intervalle de confiance récupéré: {confidence_value}")
                    print(f"DEBUG: Intervalle de confiance utilisé (fichier Excel): {confidence_value}")
                    return float(confidence_value)
                else:
                    print(f"Attention: Valeur invalide en A2 ({confidence_value}). Utilisation de la valeur par défaut 0.005")
                    print(f"DEBUG: Intervalle de confiance utilisé (défaut après erreur): 0.005")
                    return 0.005
            else:
                print("Attention: Le fichier intervalleConfiance.xlsx ne contient pas assez de données. Utilisation de la valeur par défaut 0.005")
                print(f"DEBUG: Intervalle de confiance utilisé (défaut - données insuffisantes): 0.005")
                return 0.005
                
        except PermissionError:
            print("Attention: Le fichier intervalleConfiance.xlsx est ouvert dans Excel. Utilisation de la valeur par défaut 0.005")
            print(f"DEBUG: Intervalle de confiance utilisé (défaut - permission): 0.005")
            return 0.005
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier intervalleConfiance.xlsx: {str(e)}. Utilisation de la valeur par défaut 0.005")
            print(f"DEBUG: Intervalle de confiance utilisé (défaut - erreur): 0.005")
            return 0.005
            
    except Exception as e:
        print(f"Erreur générale lors de la récupération de l'intervalle de confiance: {str(e)}. Utilisation de la valeur par défaut 0.005")
        print(f"DEBUG: Intervalle de confiance utilisé (défaut - erreur générale): 0.005")
        return 0.005

# Initialize database on startup
init_db()

def dataFrame(fichier_excel):
    """Load Excel file and return DataFrame with error handling for locked files"""
    base_dir = os.path.dirname(__file__)
    recette = os.path.join(base_dir, 'recette', fichier_excel)
    
    # Vérifier que le fichier existe
    if not os.path.exists(recette):
        raise FileNotFoundError(f"Le fichier {fichier_excel} n'existe pas dans le dossier recette")
    
    try:
        # Essayer de lire le fichier Excel
        df = pd.read_excel(recette)
        return df
    except PermissionError as e:
        raise PermissionError(f"Le fichier {fichier_excel} est ouvert dans Excel. Veuillez le fermer et réessayer.")
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier {fichier_excel}: {str(e)}")

def solvant_initial(df):
    """Extract initial solvent composition from DataFrame using dynamic component names"""
    solvant_initial = {}
    for _, row in df.iterrows():
        if pd.notna(row['ComposantsSolvant']):
            component_name = row['ComposantsSolvant']
            # Vérifier que toutes les valeurs nécessaires sont présentes
            if pd.notna(row['concL']) and pd.notna(row['density']) and pd.notna(row['IR']):
                solvant_initial[component_name] = {
                    "concL": row['concL'],
                    "density": row['density'],
                    "IR": row['IR']
                }
            else:
                print(f"Attention: Valeurs manquantes pour le composant {component_name}")
    
    print(f"Composants trouvés: {list(solvant_initial.keys())}")
    return solvant_initial

def EcoAdds(df):
    """Extract EcoAdd additives data from DataFrame"""
    eco_adds_dict = {}
    
    # Vérifier si les colonnes existent
    required_columns = ['ComposantsEcoAdd', 'ecoAddH', 'ecoAddA', 'ecoAddS']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Colonnes EcoAdd manquantes: {missing_columns}")
        return eco_adds_dict
    
    # Filtrer les lignes avec des données EcoAdd valides
    dfEcoAdds = df[required_columns].dropna()
    
    if dfEcoAdds.empty:
        print("Aucune donnée EcoAdd trouvée dans le fichier Excel")
        return eco_adds_dict
    
    dfEcoAdds = dfEcoAdds.set_index('ComposantsEcoAdd')  
    
    for index, row in dfEcoAdds.iterrows():
        eco_adds_dict[index] = {
            'ecoAddH': row['ecoAddH'],
            'ecoAddA': row['ecoAddA'], 
            'ecoAddS': row['ecoAddS']
        }
    
    print(f"EcoAdds trouvés: {list(eco_adds_dict.keys())}")
    return eco_adds_dict

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
        # Vérifier que nous avons au moins 3 composants
        if len(sI) < 3:
            raise Exception(f"Nombre insuffisant de composants: {len(sI)}. Au moins 3 composants requis.")
        
        # Vérifier la présence des composants requis
        required_components = ["compo1", "compo2", "compo3"]
        missing_components = [comp for comp in required_components if comp not in sI]
        
        if missing_components:
            raise Exception(f"Composants manquants: {missing_components}")
        
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
        # Vérifier que les valeurs ne sont pas nulles pour éviter la division par zéro
        if y == 0 or x == 0:
            raise Exception("Division par zéro détectée dans le calcul des ratios")
        
        # Calculate initial ratios
        ratio_compo1_compo2 = sI["compo1"]["concL"] / sI["compo2"]["concL"]
        ratio_compo3_compo2 = sI["compo3"]["concL"] / sI["compo2"]["concL"]
        ratio_compo3_compo1 = sI["compo3"]["concL"] / sI["compo1"]["concL"]

        # Calculate current ratios
        ratio_actuel_compo1_compo2 = x/y
        ratio_actuel_compo3_compo2 = z/y
        ratio_actuel_compo3_compo1 = z/x

        print(f"Ratios initiaux - compo1/compo2: {ratio_compo1_compo2:.5f}, compo3/compo2: {ratio_compo3_compo2:.5f}, compo3/compo1: {ratio_compo3_compo1:.5f}")
        print(f"Ratios actuels - compo1/compo2: {ratio_actuel_compo1_compo2:.5f}, compo3/compo2: {ratio_actuel_compo3_compo2:.5f}, compo3/compo1: {ratio_actuel_compo3_compo1:.5f}")

        # Store ratios in tuples for passing to next step
        ratios_initiaux = (ratio_compo1_compo2, ratio_compo3_compo2, ratio_compo3_compo1)
        ratios_actuels = (ratio_actuel_compo1_compo2, ratio_actuel_compo3_compo2, ratio_actuel_compo3_compo1)

        # Determine excess component
        if ratio_actuel_compo1_compo2 > ratio_compo1_compo2 and ratio_actuel_compo3_compo1 < ratio_compo3_compo1:
            print("compo1 est en excès")
            return etape_3(x, y, z, sI, "1", ratios_initiaux, ratios_actuels, eco_adds)
        elif ratio_actuel_compo1_compo2 < ratio_compo1_compo2 and ratio_actuel_compo3_compo2 < ratio_compo3_compo2:
            print("compo2 est en excès")
            return etape_3(x, y, z, sI, "2", ratios_initiaux, ratios_actuels, eco_adds)
        elif ratio_actuel_compo3_compo2 > ratio_compo3_compo2 and ratio_actuel_compo3_compo1 > ratio_compo3_compo1:
            print("compo3 est en excès")
            return etape_3(x, y, z, sI, "3", ratios_initiaux, ratios_actuels, eco_adds)
        else:
            raise Exception("Impossible de déterminer le composant en excès")

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 2: {str(e)}")

def etape_3(x, y, z, sI, ex, ratios_initiaux, ratios_actuels, eco_adds):
    """
    Step 3: Calculate required additive quantities to rebalance the solvent.
    Updated to use compo1, compo2, compo3 naming and explicit ratio names.
    Uses EcoAdds data from Excel file for additive concentrations.
    """
    print("Etape 3: Calcul des quantités d'additifs")
    try:
        additives = {}
        
        # Vérifier que nous avons des données EcoAdds
        if not eco_adds:
            raise Exception("Aucune donnée EcoAdd trouvée dans le fichier Excel")
        
        # Get EcoAdd concentrations from Excel data avec validation
        eco_add_1_conc = None
        eco_add_2_conc = None
        eco_add_3_conc = None
        
        # Chercher les EcoAdds avec différents noms possibles
        for key, values in eco_adds.items():
            if 'H' in key.upper() or '1' in key:
                eco_add_1_conc = values.get('ecoAddH')
            elif 'A' in key.upper() or '2' in key:
                eco_add_2_conc = values.get('ecoAddA')
            elif 'S' in key.upper() or '3' in key:
                eco_add_3_conc = values.get('ecoAddS')
        
        print(f"Concentrations EcoAdd trouvées - H: {eco_add_1_conc}, A: {eco_add_2_conc}, S: {eco_add_3_conc}")
        
        # Extract individual ratios for clarity
        ratio_compo1_compo2, ratio_compo3_compo2, ratio_compo3_compo1 = ratios_initiaux
        
        if ex == "1":  # compo1 en excès
            print("Calcul pour compo1 en excès")
            compo2_cible = x / ratio_compo1_compo2
            compo3_cible = ratio_compo3_compo1 * x
            delta_compo2 = compo2_cible - y
            delta_compo3 = compo3_cible - z
            
            if delta_compo2 > 0 and eco_add_2_conc is not None and eco_add_2_conc != 0:
                additives["EcoAdd 2"] = delta_compo2 / eco_add_2_conc
            if delta_compo3 > 0 and eco_add_3_conc is not None and eco_add_3_conc != 0:
                additives["EcoAdd 3"] = delta_compo3 / eco_add_3_conc
            
        elif ex == "2":  # compo2 en excès
            print("Calcul pour compo2 en excès")
            compo1_cible = ratio_compo1_compo2 * y
            compo3_cible = ratio_compo3_compo2 * y
            delta_compo1 = compo1_cible - x
            delta_compo3 = compo3_cible - z
            
            if delta_compo1 > 0 and eco_add_1_conc is not None and eco_add_1_conc != 0:
                additives["EcoAdd 1"] = delta_compo1 / eco_add_1_conc
            if delta_compo3 > 0 and eco_add_3_conc is not None and eco_add_3_conc != 0:
                additives["EcoAdd 3"] = delta_compo3 / eco_add_3_conc
            
        elif ex == "3":  # compo3 en excès
            print("Calcul pour compo3 en excès")
            compo1_cible = z / ratio_compo3_compo1
            compo2_cible = z / ratio_compo3_compo2
            delta_compo1 = compo1_cible - x
            delta_compo2 = compo2_cible - y
            
            if delta_compo1 > 0 and eco_add_1_conc is not None and eco_add_1_conc != 0:
                additives["EcoAdd 1"] = delta_compo1 / eco_add_1_conc
            if delta_compo2 > 0 and eco_add_2_conc is not None and eco_add_2_conc != 0:
                additives["EcoAdd 2"] = delta_compo2 / eco_add_2_conc

        # Filter out zero or negative values
        additives = {k: v for k, v in additives.items() if v > 0}
        
        if not additives:
            print("Aucun additif calculé - vérifiez les données EcoAdd dans le fichier Excel")
            return {"additives": {}, "message": "Aucun additif requis ou données EcoAdd manquantes"}
        
        print(f"Additifs calculés: {additives}")
        return {"additives": additives}

    except Exception as e:
        raise Exception(f"Erreur lors de l'étape 3: {str(e)}")

@app.route(f'{API_PREFIX}/calculate', methods=['POST'])
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
        
        # Vérifier que nous avons des données de solvant
        if not initial_solvent:
            return jsonify({"success": False, "error": "Aucune donnée de solvant trouvée dans le fichier Excel"}), 400
        
        print(f"Solvant initial: {initial_solvent}")
        print(f"EcoAdds data: {eco_adds_data}")
        
        # Calculate total theoretical values
        total_density, total_ir = calculate_total_values(initial_solvent)
        
        # Récupérer l'intervalle de confiance depuis le fichier Excel
        confidence_interval = get_confidence_interval()
        
        # DEBUG: Afficher toutes les valeurs utilisées dans la comparaison
        print(f"DEBUG: ===== COMPARAISON DES VALEURS =====")
        print(f"DEBUG: Densité théorique totale: {total_density}")
        print(f"DEBUG: Densité mesurée: {densite}")
        print(f"DEBUG: Différence densité: {abs(total_density - densite)}")
        print(f"DEBUG: IR théorique total: {total_ir}")
        print(f"DEBUG: IR mesuré: {indice_refraction}")
        print(f"DEBUG: Différence IR: {abs(total_ir - indice_refraction)}")
        print(f"DEBUG: Intervalle de confiance: {confidence_interval}")
        print(f"DEBUG: Densité dans tolérance? {abs(total_density - densite) < confidence_interval}")
        print(f"DEBUG: IR dans tolérance? {abs(total_ir - indice_refraction) < confidence_interval}")
        print(f"DEBUG: =====================================")
        
        # Check if rebalancing is necessary
        if (abs(total_density - densite) < confidence_interval and 
            abs(total_ir - indice_refraction) < confidence_interval):
            print(f"DEBUG: Rééquilibrage non nécessaire - toutes les valeurs sont dans la tolérance")
            calculation_id = str(uuid.uuid4())
            return jsonify({
                "success": True,
                "message": f"Le rééquilibrage n'est pas nécessaire (tolérance: ±{confidence_interval})",
                "calculationId": calculation_id
            })

        print(f"DEBUG: Rééquilibrage nécessaire - au moins une valeur dépasse la tolérance")
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
        
    except PermissionError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except ValueError as e:
        return jsonify({"success": False, "error": "Valeurs numériques invalides"}), 400
    except KeyError as e:
        return jsonify({"success": False, "error": f"Champ manquant: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route(f'{API_PREFIX}/recette', methods=['GET'])
def liste_fichiers_recette():
    """Get list of available recipe files, filtering out temporary Excel files"""
    base_dir = os.path.dirname(__file__)
    dossier_recette = os.path.join(base_dir, 'recette')
    
    if not os.path.exists(dossier_recette):
        print(f"Le dossier {dossier_recette} n'existe pas.")
        return jsonify([])
    
    try:
        fichiers = os.listdir(dossier_recette)
        # Filtrer les fichiers temporaires Excel (qui commencent par ~$)
        fichiers_filtres = [f for f in fichiers if not f.startswith('~$') and f.endswith('.xlsx')]
        return jsonify(fichiers_filtres)
    except Exception as e:
        print(f"Erreur lors de la lecture du dossier recette: {str(e)}")
        return jsonify([])

@app.route(f'{API_PREFIX}/send_mail', methods=['POST'])
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