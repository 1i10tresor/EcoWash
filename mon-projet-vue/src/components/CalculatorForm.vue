<template>
  <div id="calculator">
    <h1>EcoWash Balancing</h1>

    <div id="main">
      <form id="parametres" @submit.prevent="calculate">
        <div id="EW_version">
          <label for="version">Choix du modèle</label><br>
          <select name="version" id="modele" v-model="donnees.modele">
            <option value="" disabled>-- Sélectionnez une version --</option>
            <option value="EcoWash">EcoWash</option>
            <option value="EcoWash 3D">EcoWash 3D</option>
            <option value="EcoWash-4">EcoWash-4</option>
            <option value="EcoWash T-sol">EcoWash T-sol</option>
          </select>
        </div>

        <div id="choix">
          <div id="IRS">
            <input type="radio" id="IR" name="choix" value="IR" v-model="donnees.choix" class="custom-radio">
            <label for="IR"></label>
            <span>IR</span>
          </div>
          <div id="BRIXS">
            <input type="radio" id="BRIX" name="choix" value="BRIX" v-model="donnees.choix" class="custom-radio">
            <label for="BRIX"></label>
            <span>BRIX</span>
          </div>
        </div>

        <div id="saisie">
          <div class="zone_texte">
            <label for="nb_lots">Nb de lots</label><br>
            <input type="number" id="nb_lots" lang="en" step="any" class="zone_saisie" v-model="donnees.nb_lots" name="nb_lots" placeholder="Nb lots">
          </div>

          <div class="zone_texte">
            <label for="saisie_densite">Densité</label><br>
            <input type="number" class="zone_saisie" step="any" lang="en" id="saisie_densite" v-model="donnees.densite" name="saisie" placeholder="Densité">
          </div>

          <div class="zone_texte">
            <label for="saisie_refraction">Réfraction</label><br>
            <input type="number" class="zone_saisie" step="any" lang="en" id="saisie_refraction" v-model="donnees.refraction" name="saisie" placeholder="Réfraction">
          </div>
        </div>

        <button type="submit">Calculer</button>
        <div id="resultat" v-if="resultat">
          <p>Résultat : {{ resultat }}</p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from 'vue';
import axios from 'axios';

export default {
  name: 'CalculatorForm',
  setup() {
    const donnees = reactive({
      modele: '',
      choix: '',
      nb_lots: 0,
      densite: 0,
      refraction: 0,
    });
    const resultat = ref(null);
    const erreur = ref(null);

    const calculate = async () => {
      console.log('Données soumises :', donnees);

      try {
        const response = await axios.post('http://127.0.0.1:5000/calculate', {
          densite: donnees.densite,
          refraction: donnees.refraction,
        });
        resultat.value = response.data;
        console.log('Réponse du backend :', response.data);
      } catch (err) {
        console.error('Erreur lors de la requête :', err);
        erreur.value = 'Une erreur est survenue lors de la communication avec le serveur.';
      }
    };

    return {
      donnees,
      resultat,
      erreur,
      calculate,
    };
  },
};
</script>



<style scoped>
/* Conteneur principal */
#calculator {
  width: 400px;
  padding: 20px;
  border-radius: 10px;
  background: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid #ddd;
}

/* Titre */
h1 {
  font-size: 24px;
  text-align: center;
  color: #4CAF50;
  margin-bottom: 20px;
}

/* Formulaire */
#parametres {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

/* Section des choix */
#choix {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

#IRS, #BRIXS {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Zone de saisie */
#saisie {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 20px;
}

.zone_texte {
  display: flex;
  flex-direction: column;
  width: 100px;
}

.zone_saisie {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
}

.zone_saisie:hover {
  border-color: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
  background-color: #f9fff9; /* Légère teinte verte */
}

.zone_saisie:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
}

/* Résultat */
#resultat {
  margin-top: 20px;
  padding: 15px;
  background: #ffffff;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#resultat p {
  font-weight: bold;
  color: #333;
}

/* Bouton */
button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
}

button:hover {
  background-color: #45a049;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
/* Section Choix du modèle */
#EW_version {
  display: flex;
  flex-direction: column;
  align-items: center; /* Centre horizontalement */
  text-align: center; /* Centre le texte */
  margin-bottom: 20px; /* Ajoute un espacement en bas */
}

/* Boutons radio personnalisés */
.custom-radio {
  display: none; /* Masque l'input radio natif */
}

.custom-radio + label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: 2px solid #000000;
  border-radius: 3px; /* Carré avec des coins légèrement arrondis */
  background-color: white;
  cursor: pointer;
  position: relative;
  margin-right: 10px;
}

.custom-radio:checked + label {
  background-color: #4CAF50;
  border-color: #000000;
}

.custom-radio:checked + label::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 2px;
  background-color: black;
  transform: rotate(45deg);
  top: 50%;
  left: 50%;
  transform-origin: center;
  transform: translate(-50%, -50%) rotate(45deg);
}

.custom-radio:checked + label::before {
  content: '';
  position: absolute;
  width: 10px;
  height: 2px;
  background-color: black;
  transform: rotate(-45deg);
  top: 50%;
  left: 50%;
  transform-origin: center;
  transform: translate(-50%, -50%) rotate(-45deg);
}

/* Alignement des labels de texte */
#choix div {
  display: flex;
  align-items: center;
  gap: 10px; /* Espacement entre le bouton et le texte */
}

#choix label {
  margin: 0;
  font-size: 16px;
  color: #333;
  cursor: pointer;
}
</style>