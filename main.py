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

def dataFrame(fichier_excel):
    base_dir = os.path.dirname(__file__)
    recette = os.path.join(base_dir, 'recette',fichier_excel)
    df = pd.read_excel(recette)
    return df

def solvant_initial(df):
    solvant_initial = {}
    for _, row in df.iterrows():
        solvant_initial[row['ComposantsSolvant']] = {
            "concL": row['concL'],
            "density": row['density'],
            "IR": row['IR']}
    return solvant_initial

def EcoAdds(df):
    dfEcoAdds = df[['ComposantsEcoAdd', 'ecoAddH', 'ecoAddA', 'ecoAddS']].dropna()      
    dfEcoAdds = dfEcoAdds.set_index('ComposantsEcoAdd')  
    EcoAdds = {}
    for col in dfEcoAdds.columns:
        EcoAdds[col] = df[col].to_dict()
    return EcoAdds

def calculate_total_values(solvant_initial):
    total_density = 0
    total_ir = 0
    for component in solvant_initial.values():
        total_density += component['density'] * component['concL']
        total_ir += component['IR'] * component['concL']
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