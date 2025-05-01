from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

# === Données du solvant initial ===
solvant_initial = {
    "ISOL": {"concG": 0.3836, "Density": 0.7674, "IR": 1.4274},
    "BZOH": {"concG": 0.1885, "Density": 1.0450, "IR": 1.5384},
    "DIPB": {"concG": 0.4186, "Density": 0.8570, "IR": 1.4890},
    "ETOH": {"concG": 0.0092, "Density": 0.8330, "IR": 1.4310}
}

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        densite = float(data['density'])
        indice_refraction = float(data['refractionIndex'])
        
        result = process_data(indice_refraction, densite)
        return jsonify({"success": True, "result": result})
        
    except ValueError as e:
        return jsonify({"success": False, "error": "Valeurs numériques invalides"}), 400
    except KeyError as e:
        return jsonify({"success": False, "error": f"Champ manquant: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def process_data(indice_r_mesure, densite_mesuree):
    try:
        # === Étape 1 : Résolution du système ===
        fraction_etoh = 0.0092
        ir_etoh = solvant_initial["ETOH"]["IR"]
        densite_etoh = solvant_initial["ETOH"]["Density"]

        ir_corrige = indice_r_mesure - (fraction_etoh * ir_etoh)
        densite_corrigee = densite_mesuree - (fraction_etoh * densite_etoh)
        somme_fractions = 1.0 - fraction_etoh

        matrice_A = np.array([
            [solvant_initial["ISOL"]["IR"], solvant_initial["BZOH"]["IR"], solvant_initial["DIPB"]["IR"]],
            [solvant_initial["ISOL"]["Density"], solvant_initial["BZOH"]["Density"], solvant_initial["DIPB"]["Density"]],
            [1.0, 1.0, 1.0]
        ])

        vecteur_b = np.array([ir_corrige, densite_corrigee, somme_fractions])
        solution = np.linalg.solve(matrice_A, vecteur_b)
        isol, bzoh, dipb = solution

        # === Calcul des additifs ===
        ratios_init = (
            solvant_initial["ISOL"]["concG"] / solvant_initial["BZOH"]["concG"],
            solvant_initial["DIPB"]["concG"] / solvant_initial["BZOH"]["concG"],
            solvant_initial["DIPB"]["concG"] / solvant_initial["ISOL"]["concG"]
        )

        r_isol_bzoh = isol / bzoh
        r_dipb_isol = dipb / isol

        if r_isol_bzoh > ratios_init[0] and r_dipb_isol < ratios_init[2]:
            bzoh_cible = isol / ratios_init[0]
            dipb_cible = ratios_init[2] * isol
            delta_bzoh = bzoh_cible - bzoh
            delta_dipb = dipb_cible - dipb
            additives = {
                "EcoAdd1": 0,
                "EcoAdd2": delta_bzoh / 0.81,
                "EcoAdd3": delta_dipb / 0.83
            }
        elif r_isol_bzoh < ratios_init[0] and (dipb / bzoh) < ratios_init[1]:
            isol_cible = ratios_init[0] * bzoh
            dipb_cible = ratios_init[1] * bzoh
            delta_isol = isol_cible - isol
            delta_dipb = dipb_cible - dipb
            additives = {
                "EcoAdd1": delta_isol / 0.852,
                "EcoAdd2": 0,
                "EcoAdd3": delta_dipb / 0.83
            }
        else:
            isol_cible = dipb / ratios_init[2]
            bzoh_cible = dipb / ratios_init[1]
            delta_isol = isol_cible - isol
            delta_bzoh = bzoh_cible - bzoh
            additives = {
                "EcoAdd1": delta_isol / 0.852,
                "EcoAdd2": delta_bzoh / 0.81,
                "EcoAdd3": 0
            }

        return {
            "fractions": {
                "ISOL": float(isol),
                "BZOH": float(bzoh),
                "DIPB": float(dipb),
                "ETOH": float(fraction_etoh)
            },
            "additives": additives
        }

    except np.linalg.LinAlgError:
        raise Exception("Impossible de résoudre le système d'équations")
    except Exception as e:
        raise Exception(f"Erreur de calcul: {str(e)}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)