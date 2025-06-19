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

        <div id="saisie">
          <div class="zone_texte">
            <label for="saisie_densite">{{ translations[currentLanguage].density }}</label>
            <input type="number" class="zone_saisie" step="any" lang="en" id="saisie_densite" v-model="donnees.densite" name="saisie" :placeholder="translations[currentLanguage].density" @input="resetCalculation">
          </div>

          <div class="zone_texte">
            <label for="saisie_refraction">{{ translations[currentLanguage].refraction }}</label>
            <input type="number" class="zone_saisie" step="any" lang="en" id="saisie_refraction" v-model="donnees.refraction" name="saisie" :placeholder="translations[currentLanguage].refraction" @input="resetCalculation">
          </div>
        </div>

        <button type="submit" :disabled="!isFormValid">{{ translations[currentLanguage].calculate }}</button>
        
        <!-- Error display -->
        <div v-if="erreur" class="error-message">
          <div class="error-header">
            <span class="error-icon">⚠️</span>
            <strong>{{ translations[currentLanguage].error }}</strong>
          </div>
          <div class="error-content">
            {{ erreur }}
          </div>
          <div class="error-actions">
            <button type="button" @click="clearError" class="clear-error-btn">
              {{ translations[currentLanguage].dismiss }}
            </button>
          </div>
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
              {{ translations[currentLanguage].add }} {{ value.toFixed(5) }} {{ translations[currentLanguage].of }} {{ key }}
            </li>
            <p class="addition-note">{{ translations[currentLanguage].additionNote }}</p>
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
            :disabled="!isValidEmail || !email || isEmailSending"
            class="email-send-btn"
          >
            <span v-if="isEmailSending" class="loading-spinner">⏳</span>
            {{ isEmailSending ? translations[currentLanguage].sending : translations[currentLanguage].validate }}
          </button>
        </div>

        <!-- Email success/error messages -->
        <div v-if="emailStatus" class="email-status" :class="emailStatus.type">
          <div class="status-header">
            <span class="status-icon">{{ emailStatus.type === 'success' ? '✅' : '❌' }}</span>
            <strong>{{ emailStatus.type === 'success' ? translations[currentLanguage].success : translations[currentLanguage].error }}</strong>
          </div>
          <div class="status-content">
            {{ emailStatus.message }}
          </div>
          <div class="status-actions">
            <button type="button" @click="clearEmailStatus" class="clear-status-btn">
              {{ translations[currentLanguage].dismiss }}
            </button>
          </div>
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
  emits: ['results-changed'], // Declare the emit
  setup(props, { emit }) {
    const currentLanguage = inject('currentLanguage');
    const translations = inject('translations');

    const donnees = reactive({
      modele: '',
      densite: 0,
      refraction: 0
    });

    const resultat = ref(null);
    const erreur = ref(null);
    const liste_recettes = ref([]);
    const showEmailForm = ref(false);
    const email = ref('');
    const calculationId = ref(null);
    const emailStatus = ref(null);
    const isEmailSending = ref(false);
    
    const liste_recettes_corrigee = computed(() =>
      liste_recettes.value.map(nom =>
        nom.replace(/\.[^.]+$/, '')
      )
    );
    
    const resultat_corrige = computed(() => {
      if (!resultat.value?.result?.additives) return {};
      const adds = resultat.value.result.additives;
      // Multiply by 100 and rename EcoAdd components
      const renamedAdds = {};
      Object.entries(adds).forEach(([key, value]) => {
        let newKey = key;
        if (key === 'EcoAdd 1') newKey = 'Eco Add H';
        else if (key === 'EcoAdd 2') newKey = 'Eco Add A';
        else if (key === 'EcoAdd 3') newKey = 'Eco Add S';
        
        renamedAdds[newKey] = value * 100; // Multiply by 100
      });
      
      return Object.fromEntries(
        Object.entries(renamedAdds).filter(([, qty]) => qty !== 0)
      );
    });

    const isValidEmail = computed(() => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email.value);
    });

    const isFormValid = computed(() => {
      return donnees.modele !== '' && 
             donnees.densite !== 0 && 
             donnees.refraction !== 0;
    });

    // Watch for results changes and emit to parent
    watch(resultat, (newValue) => {
      const hasResults = !!(newValue && (
        newValue.message || 
        (newValue.result?.additives && Object.keys(newValue.result.additives).length > 0)
      ));
      emit('results-changed', hasResults);
    }, { immediate: true });

    // Clear error message
    const clearError = () => {
      erreur.value = null;
    };

    // Clear email status
    const clearEmailStatus = () => {
      emailStatus.value = null;
    };

    // Reset calculation when form values change
    const resetCalculation = () => {
      resultat.value = null;
      calculationId.value = null;
      showEmailForm.value = false;
      email.value = '';
      erreur.value = null;
      emailStatus.value = null;
      isEmailSending.value = false;
    };

    // Watch for changes in form values
    watch(() => donnees.modele, resetCalculation);

    const recup_liste_recettes = async () => {
      try {
        const response = await axios.get('/api/recette');
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
        let choix = 'IR'; // Default choice
        
        // Automatic detection based on value
        if (donnees.refraction > 2) {
          choix = 'BRIX';
          refractionValue = (donnees.refraction / 476.21) + 1.3215;
        }

        const response = await axios.post('/api/calculate', {
          densite: donnees.densite,
          refraction: refractionValue,
          fichier_excel: donnees.modele,
          choix: choix
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
      if (!isValidEmail.value || isEmailSending.value) return;
      
      try {
        isEmailSending.value = true;
        emailStatus.value = null;
        
        const response = await axios.post('/api/send_mail', {
          email: email.value,
          resultats: resultat_corrige.value,
          donnees: {
            densite: donnees.densite,
            refraction: donnees.refraction,
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
        let errorMessage = translations.value[currentLanguage.value].emailError;
        
        if (err.response && err.response.data && err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
          errorMessage = translations.value[currentLanguage.value].connectionError;
        }
        
        emailStatus.value = {
          type: 'error',
          message: errorMessage
        };
      } finally {
        isEmailSending.value = false;
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
      emailStatus,
      isEmailSending,
      clearError,
      clearEmailStatus
    };
  },
};
</script>

<style scoped>
/* Conteneur principal */
#calculator {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  border-radius: 10px;
  background: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid #ddd;
  font-family: 'Space Mono', monospace;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Titre */
h1 {
  font-size: 24px;
  text-align: center;
  color: #4CAF50;
  margin-bottom: 20px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
}

/* Formulaire */
#parametres {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

/* Zone de saisie - Alignement parfait */
#saisie {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 20px;
  align-items: flex-end; /* Aligne les inputs en bas pour compenser les différences de hauteur des labels */
}

.zone_texte {
  display: flex;
  flex-direction: column;
  width: 150px;
  min-height: 60px; /* Hauteur minimale fixe pour uniformiser */
}

.zone_texte label {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  margin-bottom: 8px; /* Marge fixe pour tous les labels */
  text-align: left;
  height: 20px; /* Hauteur fixe pour les labels */
  display: flex;
  align-items: center; /* Centre le texte verticalement dans la hauteur fixe */
  line-height: 1.2;
}

.zone_saisie {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
  font-family: 'Space Mono', monospace;
  height: 40px; /* Hauteur fixe pour tous les inputs */
  box-sizing: border-box;
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
  font-family: 'Space Mono', monospace;
}

#resultat p {
  font-weight: bold;
  color: #333;
}

.addition-note {
  font-style: italic;
  color: #666;
  font-size: 12px;
  margin-top: 10px;
  font-weight: normal !important;
}

/* Messages d'erreur améliorés */
.error-message {
  margin-top: 15px;
  border-radius: 8px;
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  border: 1px solid #fc8181;
  box-shadow: 0 4px 12px rgba(252, 129, 129, 0.15);
  font-family: 'Space Mono', monospace;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

.error-header {
  background: #fed7d7;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #fc8181;
}

.error-icon {
  font-size: 18px;
}

.error-content {
  padding: 16px;
  color: #742a2a;
  line-height: 1.5;
}

.error-actions {
  padding: 12px 16px;
  background: #fff5f5;
  border-top: 1px solid #fed7d7;
  display: flex;
  justify-content: flex-end;
}

.clear-error-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-family: 'Space Mono', monospace;
}

.clear-error-btn:hover {
  background: #c53030;
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
  font-family: 'Space Mono', monospace;
}

.email-form input.invalid {
  border-color: #ff0000;
  background-color: #fff0f0;
}

.email-send-btn {
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 5px;
}

.email-send-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.email-send-btn:not(:disabled):hover {
  background-color: #45a049;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  font-family: 'Space Mono', monospace;
  font-weight: 700;
}

.email-button:hover {
  background-color: #45a049;
}

/* Messages de statut email améliorés */
.email-status {
  margin-top: 15px;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.email-status.success {
  background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
  border: 1px solid #68d391;
}

.email-status.error {
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  border: 1px solid #fc8181;
}

.status-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
}

.email-status.success .status-header {
  background: #c6f6d5;
  color: #22543d;
  border-bottom: 1px solid #68d391;
}

.email-status.error .status-header {
  background: #fed7d7;
  color: #742a2a;
  border-bottom: 1px solid #fc8181;
}

.status-icon {
  font-size: 18px;
}

.status-content {
  padding: 16px;
  line-height: 1.5;
}

.email-status.success .status-content {
  color: #22543d;
}

.email-status.error .status-content {
  color: #742a2a;
}

.status-actions {
  padding: 12px 16px;
  display: flex;
  justify-content: flex-end;
}

.email-status.success .status-actions {
  background: #f0fff4;
  border-top: 1px solid #c6f6d5;
}

.email-status.error .status-actions {
  background: #fff5f5;
  border-top: 1px solid #fed7d7;
}

.clear-status-btn {
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-family: 'Space Mono', monospace;
  color: white;
}

.email-status.success .clear-status-btn {
  background: #38a169;
}

.email-status.success .clear-status-btn:hover {
  background: #2f855a;
}

.email-status.error .clear-status-btn {
  background: #e53e3e;
}

.email-status.error .clear-status-btn:hover {
  background: #c53030;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  font-family: 'Space Mono', monospace;
  font-weight: 700;
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

#EW_version label {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  margin-bottom: 10px;
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
  font-family: 'Space Mono', monospace;
}

select:hover, select:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
  outline: none;
}

select option {
  padding: 8px;
  transition: background-color 0.3s ease;
  font-family: 'Space Mono', monospace;
}

select option:hover {
  background-color: #f0f0f0;
}

/* Responsive design pour mobile */
@media (max-width: 768px) {
  #calculator {
    width: 100%;
    max-width: 350px;
    padding: 15px;
    margin: 0 auto;
  }

  h1 {
    font-size: 20px;
  }

  #saisie {
    flex-direction: column;
    gap: 15px;
    align-items: stretch; /* Étire les éléments sur toute la largeur en mode mobile */
  }

  .zone_texte {
    width: 100%;
    min-height: auto; /* Supprime la hauteur minimale en mobile */
  }

  select {
    width: 100%;
    max-width: 250px;
  }
}

@media (max-width: 480px) {
  #calculator {
    padding: 10px;
    max-width: 320px;
  }

  h1 {
    font-size: 18px;
  }

  select {
    max-width: 200px;
  }
}
</style>