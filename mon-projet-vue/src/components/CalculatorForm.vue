<template>
  <div id="calculator">
    <h1>{{ translations[currentLanguage].title }}</h1>
    <div id="main">
      <form id="parametres" @submit.prevent="handleSubmit">
        <div id="EW_version">
          <label for="version">{{ translations[currentLanguage].modelChoice }}</label><br>
          <select name="version" id="modele" v-model="donnees.modele">
            <option value="" disabled>{{ translations[currentLanguage].selectVersion }}</option>
            <option v-for="(recette, index) in liste_recettes_corrigee" :key="index" :value="recette">
              {{ recette }}
            </option>
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
            <label for="saisie_densite">{{ translations[currentLanguage].density }}</label><br>
            <input type="number" class="zone_saisie" step="any" lang="en" id="saisie_densite" v-model="donnees.densite" name="saisie" :placeholder="translations[currentLanguage].density" @input="resetCalculation">
          </div>

          <div class="zone_texte">
            <label for="saisie_refraction">{{ donnees.choix === 'BRIX' ? 'BRIX' : 'I.R' }}</label><br>
            <input type="number" class="zone_saisie" step="any" lang="en" id="saisie_refraction" v-model="donnees.refraction" name="saisie" :placeholder="donnees.choix === 'BRIX' ? 'BRIX' : translations[currentLanguage].refraction" @input="resetCalculation">
          </div>
        </div>

        <button type="submit" :disabled="!isFormValid">{{ translations[currentLanguage].calculate }}</button>
        
        <!-- Error display -->
        <div v-if="erreur" class="error-message">
          <p>{{ translations[currentLanguage].error }}: {{ erreur }}</p>
        </div>
        
        <div id="resultat" v-if="resultat">
          <div v-if="resultat.message">
            <p>{{ resultat.message }}</p>
            <p> - - - - - - - -  </p>
            <p>{{ translations[currentLanguage].calculationId }} : {{ calculationId }}</p>
          </div>
          <div v-else-if="resultat_corrige && Object.keys(resultat_corrige).length >= 1">
            <p>{{ translations[currentLanguage].result }} :</p>
            <li v-for="(value, key) in resultat_corrige" :key="key">
              {{ translations[currentLanguage].add }} {{ value.toFixed(7) }} {{ translations[currentLanguage].of }} {{ key }}
            </li>
            <p> - - - - - - - -  </p>
            <p>{{ translations[currentLanguage].calculationId }} : {{ calculationId }}</p>
            <button type="button" @click="showEmailForm = true" class="email-button">{{ translations[currentLanguage].sendByEmail }}</button>
          </div>
          <div v-else>
            <p class="error-message">{{ translations[currentLanguage].calculationError }}</p>
          </div>
        </div>

        <div v-if="showEmailForm" class="email-form">
          <input 
            type="email" 
            v-model="email" 
            :placeholder="translations[currentLanguage].enterEmail"
            :class="{ 'invalid': !isValidEmail && email !== '' }"
          >
          <button 
            type="button" 
            @click="sendEmail" 
            :disabled="!isValidEmail || !email"
          >
            {{ translations[currentLanguage].validate }}
          </button>
        </div>

        <!-- Email success/error messages -->
        <div v-if="emailStatus" class="email-status" :class="emailStatus.type">
          <p>{{ emailStatus.message }}</p>
        </div>
      </form>  
    </div>
  </div>
</template>

<script>
import { computed, reactive, ref, watch, inject } from 'vue';
import axios from 'axios';

export default {
  name: 'CalculatorForm',
  setup() {
    const currentLanguage = inject('currentLanguage');
    const translations = inject('translations');

    const donnees = reactive({
      modele: '',
      choix: '',
      densite: 0,
      refraction: 0,
    });

    const resultat = ref(null);
    const erreur = ref(null);
    const liste_recettes = ref([]);
    const showEmailForm = ref(false);
    const email = ref('');
    const calculationId = ref(null);
    const emailStatus = ref(null);
    
    const liste_recettes_corrigee = computed(() =>
      liste_recettes.value.map(nom =>
        nom.replace(/\.[^.]+$/, '')
      )
    );
    
    const resultat_corrige = computed(() => {
      if (!resultat.value?.result?.additives) return {};
      const adds = resultat.value.result.additives;
      return Object.fromEntries(
        Object.entries(adds).filter(([, qty]) => qty !== 0));
    });

    const isValidEmail = computed(() => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email.value);
    });

    const isFormValid = computed(() => {
      return donnees.modele !== '' && 
             donnees.choix !== '' && 
             donnees.densite !== 0 && 
             donnees.refraction !== 0;
    });

    // Reset calculation when form values change
    const resetCalculation = () => {
      resultat.value = null;
      calculationId.value = null;
      showEmailForm.value = false;
      email.value = '';
      erreur.value = null;
      emailStatus.value = null;
    };

    // Watch for changes in form values
    watch(() => donnees.modele, resetCalculation);
    watch(() => donnees.choix, resetCalculation);

    const recup_liste_recettes = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/recette');
        liste_recettes.value = response.data;
        erreur.value = null;
      } catch (err) {
        console.error('Erreur lors de la requête :', err);
        erreur.value = translations.value[currentLanguage.value].serverError;
      }
    };

    const handleSubmit = async () => {
      if (!isFormValid.value) {
        return;
      }
      await calculate();
    };

    const calculate = async () => {
      try {
        erreur.value = null;
        let refractionValue = donnees.refraction;
        if (donnees.choix === 'BRIX') {
          refractionValue = (refractionValue / 476.21) + 1.3215;
        }

        const response = await axios.post('http://127.0.0.1:5000/calculate', {
          densite: donnees.densite,
          refraction: refractionValue,
          fichier_excel: donnees.modele,
          choix: donnees.choix
        });
        
        if (response.data.success) {
          resultat.value = response.data;
          calculationId.value = response.data.calculationId;
        } else {
          erreur.value = response.data.error || translations.value[currentLanguage.value].unknownError;
        }
      } catch (err) {
        console.error('Erreur lors de la requête :', err);
        if (err.response && err.response.data && err.response.data.error) {
          erreur.value = err.response.data.error;
        } else if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
          erreur.value = translations.value[currentLanguage.value].connectionError;
        } else {
          erreur.value = translations.value[currentLanguage.value].calculationError;
        }
      }
    };

    const sendEmail = async () => {
      if (!isValidEmail.value) return;
      
      try {
        emailStatus.value = null;
        const response = await axios.post('http://127.0.0.1:5000/send_mail', {
          email: email.value,
          resultats: resultat_corrige.value,
          donnees: {
            densite: donnees.densite,
            refraction: donnees.refraction,
            choix: donnees.choix,
            modele: donnees.modele
          },
          calculationId: calculationId.value
        });

        if (response.data.success) {
          emailStatus.value = {
            type: 'success',
            message: translations.value[currentLanguage.value].emailSent
          };
          showEmailForm.value = false;
          email.value = '';
        } else {
          emailStatus.value = {
            type: 'error',
            message: response.data.error || translations.value[currentLanguage.value].emailError
          };
        }
      } catch (err) {
        console.error('Erreur lors de l\'envoi du mail :', err);
        emailStatus.value = {
          type: 'error',
          message: translations.value[currentLanguage.value].emailError
        };
      }
    };

    recup_liste_recettes();

    return {
      donnees,
      resultat,
      erreur,
      liste_recettes,
      calculate,
      recup_liste_recettes,
      liste_recettes_corrigee,
      resultat_corrige,
      isFormValid,
      handleSubmit,
      showEmailForm,
      email,
      isValidEmail,
      sendEmail,
      calculationId,
      resetCalculation,
      currentLanguage,
      translations,
      emailStatus
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
  width: 150px;
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
  background-color: #f9fff9;
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

.error-message {
  color: #ff0000;
  font-weight: bold;
  margin-top: 15px;
  padding: 10px;
  background-color: #fff0f0;
  border: 1px solid #ffcccc;
  border-radius: 5px;
}

/* Email form */
.email-form {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.email-form input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  transition: all 0.3s ease;
}

.email-form input.invalid {
  border-color: #ff0000;
  background-color: #fff0f0;
}

.email-form button {
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.email-form button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.email-button {
  margin-top: 15px;
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.email-button:hover {
  background-color: #45a049;
}

/* Email status messages */
.email-status {
  margin-top: 15px;
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}

.email-status.success {
  background-color: #f0fff0;
  color: #4CAF50;
  border: 1px solid #ccffcc;
}

.email-status.error {
  background-color: #fff0f0;
  color: #ff0000;
  border: 1px solid #ffcccc;
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

button:not(:disabled):hover {
  background-color: #45a049;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Section Choix du modèle */
#EW_version {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 20px;
}

/* Style du select avec transition */
select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: white;
  cursor: pointer;
  width: 200px;
  font-size: 14px;
  transition: all 0.3s ease;
  appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, #4CAF50 50%),
                    linear-gradient(135deg, #4CAF50 50%, transparent 50%);
  background-position: calc(100% - 20px) calc(1em + 2px),
                       calc(100% - 15px) calc(1em + 2px);
  background-size: 5px 5px,
                  5px 5px;
  background-repeat: no-repeat;
}

select:hover, select:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
  outline: none;
}

select option {
  padding: 8px;
  transition: background-color 0.3s ease;
}

select option:hover {
  background-color: #f0f0f0;
}

/* Boutons radio personnalisés */
.custom-radio {
  display: none;
}

.custom-radio + label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: 2px solid #000000;
  border-radius: 3px;
  background-color: white;
  cursor: pointer;
  position: relative;
  margin-right: 10px;
  transition: all 0.3s ease;
}

.custom-radio:checked + label {
  background-color: #4CAF50;
  border-color: #000000;
  transform: scale(1.1);
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
  transition: all 0.3s ease;
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
  transition: all 0.3s ease;
}

/* Alignement des labels de texte */
#choix div {
  display: flex;
  align-items: center;
  gap: 10px;
}

#choix label {
  margin: 0;
  font-size: 16px;
  color: #333;
  cursor: pointer;
}
</style>