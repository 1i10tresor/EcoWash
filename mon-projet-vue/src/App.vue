<template>
  <div id="main_container">
    <header>
      <div id="logo-container">
        <img src="/logoEcoWash.png" alt="Ecowash Logo" id="header-logo" :class="{ 'logo-large': !hasResults }" />
      </div>
      <div id="language-switcher">
        <div class="language-selector" @click="toggleLanguageMenu" ref="languageSelector">
          <img :src="currentFlag" :alt="currentLanguage" class="current-flag">
          <span class="arrow" :class="{ 'open': showLanguageMenu }">▼</span>
          
          <div v-if="showLanguageMenu" class="language-menu">
            <div 
              v-for="lang in otherLanguages" 
              :key="lang.code"
              @click.stop="changeLanguage(lang.code)"
              class="language-option"
            >
              <img :src="lang.flag" :alt="lang.code" class="flag-option">
              <span>{{ lang.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div id="calculator">
      <CalculatorForm @results-changed="handleResultsChanged" />
    </div>

    <footer>
      <div id="topFooter">
        <div id="logo" class="elements_footer">
          <img src="../src/assets/logo.png" alt="Logo" />
        </div>

        <div id="adresse" class="elements_footer">
          <h2>Spring Coating Systems</h2>
          <p>18 rue de la Fabrique</p>
          <p>68530 BUHL</p>
          <p>{{ translations[currentLanguage].phone }} : 03 89 83 06 82</p>
        </div>
        
        <div id="contact" class="elements_footer">
          <h2>{{ translations[currentLanguage].reportProblem }}</h2>
          <a href="mailto:ecowash@spring-coating.com">ecowash@spring-coating.com</a>
          <p>{{ translations[currentLanguage].phone }} : 07 60 11 07 85</p>
        </div>

        <div id="description" class="elements_footer">
          <a href="https://www.linkedin.com/company/spring-coating-systems/" target="_blank" id="lienIn">
            <img id="linkedin" src="../src/assets/linkedin.png" alt="Logo">
          </a>
          <p>{{ translations[currentLanguage].companyDescriptionShort }}</p>
        </div> 
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, provide, computed, onMounted, onUnmounted } from 'vue';
import CalculatorForm from './components/CalculatorForm.vue';

export default {
  name: 'App',
  components: { CalculatorForm },
  setup() {
    const currentLanguage = ref('en'); // Changed default to English
    const showLanguageMenu = ref(false);
    const languageSelector = ref(null);
    const hasResults = ref(false); // Track if calculator has results
    
    const languages = [
      { code: 'fr', name: 'Français', flag: '/france.png' },
      { code: 'en', name: 'English', flag: '/etats-unis.png' },
      { code: 'de', name: 'Deutsch', flag: '/allemagne.png' }
    ];

    const currentFlag = computed(() => {
      const lang = languages.find(l => l.code === currentLanguage.value);
      return lang ? lang.flag : '/etats-unis.png'; // Changed default flag to US
    });

    const otherLanguages = computed(() => {
      return languages.filter(l => l.code !== currentLanguage.value);
    });

    const translations = ref({
      fr: {
        headerTitle: "Calculateur d'additifs EcoAdd",
        headerTitleMobile: "Calculateur d'additifs",
        title: "Ecowash balancing calculator",
        modelChoice: "Choix du modèle",
        selectVersion: "Sélectionnez une version",
        density: "Densité",
        refraction: "Réfraction",
        calculate: "Calculer",
        result: "Résultat",
        add: "Ajouter",
        of: "d'",
        calculationId: "ID calcul",
        sendByEmail: "Envoyer par mail",
        enterEmail: "Saisir votre adresse email",
        validate: "Valider",
        error: "Erreur",
        success: "Succès",
        sending: "Envoi...",
        dismiss: "Fermer",
        calculationError: "Erreur de calcul, veuillez ressaisir les données",
        serverError: "Erreur de communication avec le serveur",
        connectionError: "Impossible de se connecter au serveur",
        unknownError: "Erreur inconnue",
        emailSent: "Email envoyé avec succès",
        emailError: "Erreur lors de l'envoi de l'email",
        phone: "Tél",
        reportProblem: "Signaler un problème",
        companyDescriptionShort: "Spring Coating Systems est formulateur et fabricant d'encres, vernis, colles, et peintures pour des applications industrielles et l'impression d'emballages. Nos produits sont souvent formulés sur mesure et adaptés à l'activité de nos clients.",
        additionNote: "Addition pour 100 unités (en volume) de solvant à corriger"
      },
      en: {
        headerTitle: "EcoAdd Additives Calculator",
        headerTitleMobile: "Additives Calculator",
        title: "Ecowash balancing calculator",
        modelChoice: "Choose Product",
        selectVersion: "Select a version",
        density: "Density",
        refraction: "Refractive Index",
        calculate: "Calculate",
        result: "Result",
        add: "Add",
        of: "of",
        calculationId: "Calculation ID",
        sendByEmail: "Send by email",
        enterEmail: "Enter your email address",
        validate: "Validate",
        error: "Error",
        success: "Success",
        sending: "Sending...",
        dismiss: "Close",
        calculationError: "Calculation error, please re-enter the data",
        serverError: "Server communication error",
        connectionError: "Unable to connect to server",
        unknownError: "Unknown error",
        emailSent: "Email sent successfully",
        emailError: "Error sending email",
        phone: "Tel",
        reportProblem: "Report a problem",
        companyDescriptionShort: "Spring Coating Systems is a formulator and manufacturer of inks, varnishes, adhesives, and paints for industrial applications and packaging printing. Our products are often custom-formulated and adapted to our customers' activities.",
        additionNote: "Addition for 100 units (by volume) of solvent to be corrected"
      },
      de: {
        headerTitle: "EcoAdd Additive Rechner",
        headerTitleMobile: "Additive Rechner",
        title: "Ecowash balancing calculator",
        modelChoice: "Produkt wählen",
        selectVersion: "Wählen Sie eine Version",
        density: "Dichte",
        refraction: "Brechungsindex",
        calculate: "Berechnen",
        result: "Ergebnis",
        add: "Hinzufügen",
        of: "von",
        calculationId: "Berechnungs-ID",
        sendByEmail: "Per E-Mail senden",
        enterEmail: "Geben Sie Ihre E-Mail-Adresse ein",
        validate: "Bestätigen",
        error: "Fehler",
        success: "Erfolg",
        sending: "Senden...",
        dismiss: "Schließen",
        calculationError: "Berechnungsfehler, bitte geben Sie die Daten erneut ein",
        serverError: "Server-Kommunikationsfehler",
        connectionError: "Verbindung zum Server nicht möglich",
        unknownError: "Unbekannter Fehler",
        emailSent: "E-Mail erfolgreich gesendet",
        emailError: "Fehler beim Senden der E-Mail",
        phone: "Tel",
        reportProblem: "Problem melden",
        companyDescriptionShort: "Spring Coating Systems ist Formulierer und Hersteller von Tinten, Lacken, Klebstoffen und Farben für industrielle Anwendungen und Verpackungsdruck. Unsere Produkte werden oft maßgeschneidert und an die Aktivitäten unserer Kunden angepasst.",
        additionNote: "Zusatz für 100 Einheiten (nach Volumen) des zu korrigierenden Lösungsmittels"
      }
    });

    const changeLanguage = (langCode) => {
      currentLanguage.value = langCode;
      showLanguageMenu.value = false;
    };

    const toggleLanguageMenu = () => {
      showLanguageMenu.value = !showLanguageMenu.value;
    };

    const handleClickOutside = (event) => {
      if (languageSelector.value && !languageSelector.value.contains(event.target)) {
        showLanguageMenu.value = false;
      }
    };

    // Handle results change from calculator
    const handleResultsChanged = (hasResultsValue) => {
      hasResults.value = hasResultsValue;
    };

    onMounted(() => {
      document.addEventListener('click', handleClickOutside);
    });

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside);
    });

    // Provide the reactive values to child components
    provide('currentLanguage', currentLanguage);
    provide('translations', translations);

    return {
      currentLanguage,
      languages,
      translations,
      changeLanguage,
      showLanguageMenu,
      toggleLanguageMenu,
      currentFlag,
      otherLanguages,
      languageSelector,
      hasResults,
      handleResultsChanged
    };
  }
};
</script>

<style scoped>
/* Conteneur principal */
#main_container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: 'Space Mono', monospace;
  color: #333;
  background-image: url('/bg_thin.png');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  background-repeat: no-repeat;
}

/* Header redesigné - Logo centré et sélecteur de langue à droite */
header {
  background-color: transparent; /* Suppression du bandeau */
  padding: 22px 20px; /* Remis aux valeurs précédentes */
  display: flex;
  justify-content: center; /* Centre le logo */
  align-items: center;
  position: relative;
  min-height: 90px; /* Remis aux valeurs précédentes */
  transition: min-height 0.5s ease; /* Transition fluide pour la hauteur */
}

/* Logo container - centré et agrandi */
#logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
}

#header-logo {
  max-height: 120px; /* Taille normale */
  max-width: 400px;
  height: auto;
  width: auto;
  object-fit: contain;
  transition: all 0.5s ease; /* Transition fluide pour toutes les propriétés */
}

/* Logo agrandi quand pas de résultats - 1.5x au lieu de 2x */
#header-logo.logo-large {
  max-height: 180px; /* 1.5 fois plus gros (120 * 1.5) */
  max-width: 600px; /* 1.5 fois plus large (400 * 1.5) */
}

#header-logo:hover {
  transform: scale(1.05);
}

/* Ajustement de la hauteur du header quand le logo est grand */
header:has(.logo-large) {
  min-height: 150px; /* Remis aux valeurs précédentes */
}

/* Language switcher - positionné absolument en haut à droite */
#language-switcher {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.language-selector {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(76, 175, 80, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.language-selector:hover {
  background-color: rgba(255, 255, 255, 1);
  border-color: #4CAF50;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.current-flag {
  width: 28px;
  height: 28px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.arrow {
  font-size: 14px;
  transition: transform 0.3s ease;
  color: #4CAF50;
  font-family: 'Space Mono', monospace;
  font-weight: bold;
}

.arrow.open {
  transform: rotate(180deg);
}

.language-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background-color: #FCFCFC;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  z-index: 1000;
  min-width: 160px;
  border: 1px solid rgba(76, 175, 80, 0.2);
}

.language-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #333;
  font-size: 14px;
  font-family: 'Space Mono', monospace;
}

.language-option:hover {
  background-color: #f0f8f0;
  color: #4CAF50;
}

.flag-option {
  width: 25px;
  height: 25px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* Contenu principal - calculateur rapproché du logo */
#calculator {
  margin: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px; /* Remis à 10px comme demandé */
  width: 100%;
  box-sizing: border-box;
  margin-top: -5px; /* Marge négative de -5px comme demandé */
}

footer {
  height: 100px;
  color: rgb(231, 228, 222);
  box-shadow: 0 -5px 10px -5px rgba(0, 0, 0, 0.3);
}

#topFooter {
  height: 100%;
  border: 1px solid black;
  background-color: rgba(37, 34, 34, 0.95);
  display: flex;
  backdrop-filter: blur(10px);
  align-items: center;
}

.elements_footer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 15px;
  text-align: center;
  transition: all 0.3s ease-in-out;
  font-family: 'Space Mono', monospace;
  background-color: rgba(37, 34, 34, 0.95);
  box-sizing: border-box;
  overflow: hidden;
  height: 100%;
}

.elements_footer h2 {
  margin: 0 0 8px 0;
  font-size: 15px;
}

.elements_footer p {
  margin: 1px 0;
  font-size: 13px;
}

#logo {
  flex: 1;
  min-width: 150px;
}

#logo img {
  max-height: 60px;
  width: auto;
}

#adresse {
  flex: 1;
  min-width: 180px;
}

#adresse p {
  margin: 1px 0;
}

#contact {
  flex: 1;
  min-width: 180px;
}

#description {
  flex: 2;
  min-width: 250px;
  font-size: 10px;
}

a {
  text-decoration: none;
  color: rgb(241, 243, 220);
  font-size: 13px;
}

#linkedin {
  width: 70px;
  background-color: transparent !important;
}

#lienIn {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
  border-bottom: 1px solid rgb(241, 243, 220);
  margin-bottom: 8px;
  transition: all 0.3s ease-in-out;
}

#lienIn:hover, #contact:hover, #adresse:hover, #logo:hover {
  border-radius: 10px;
  transform: scale(1.05);
}

/* Media queries pour une meilleure responsivité */
@media (max-width: 1200px) {
  footer {
    height: 110px;
  }
  
  .elements_footer h2 {
    font-size: 14px;
  }
  
  .elements_footer p {
    font-size: 12px;
  }
  
  #description {
    font-size: 9px;
  }
}

@media (max-width: 1000px) {
  footer {
    height: auto;
  }
  
  #topFooter {
    flex-direction: column;
    height: auto;
    align-items: stretch;
  }
  
  .elements_footer {
    width: 100%;
    min-width: auto;
    border-bottom: 1px solid rgb(66, 65, 65);
    padding: 15px;
    height: auto;
  }
  
  .elements_footer h2 {
    font-size: 16px;
  }
  
  .elements_footer p {
    font-size: 14px;
  }
  
  #description {
    font-size: 12px;
  }
  
  #linkedin {
    width: 70px;
  }
  
  #lienIn {
    height: 45px;
  }
}

@media (max-width: 768px) {
  header {
    padding: 15px;
    min-height: 75px;
  }

  header:has(.logo-large) {
    min-height: 120px;
  }

  #header-logo {
    max-height: 100px;
    max-width: 300px;
  }

  #header-logo.logo-large {
    max-height: 150px;
    max-width: 450px;
  }

  #language-switcher {
    top: 15px;
    right: 15px;
  }

  .language-selector {
    padding: 8px 10px;
  }

  .current-flag {
    width: 24px;
    height: 24px;
  }

  .language-menu {
    right: 0;
    left: auto;
    transform: none;
    min-width: 140px;
  }

  .flag-option {
    width: 22px;
    height: 22px;
  }

  #calculator {
    padding: 20px 10px; /* Valeurs originales pour mobile */
    justify-content: center;
    align-items: center;
    margin-top: 0; /* Pas de marge négative sur mobile */
  }

  footer {
    height: auto;
  }

  #topFooter {
    flex-direction: column;
    height: auto;
    align-items: stretch;
  }

  .elements_footer {
    width: 100%;
    min-width: auto;
    padding: 15px;
    border-bottom: 1px solid rgb(66, 65, 65);
    height: auto;
  }

  .elements_footer:last-child {
    border-bottom: none;
  }

  .elements_footer h2 {
    font-size: 16px;
  }

  .elements_footer p {
    font-size: 14px;
  }

  #description {
    font-size: 12px;
  }

  #main_container {
    overflow-x: hidden;
  }
}

@media (max-width: 480px) {
  header {
    padding: 11px 10px;
    min-height: 60px;
  }

  header:has(.logo-large) {
    min-height: 105px;
  }

  #header-logo {
    max-height: 80px;
    max-width: 250px;
  }

  #header-logo.logo-large {
    max-height: 120px;
    max-width: 375px;
  }

  #language-switcher {
    top: 10px;
    right: 10px;
  }

  .language-selector {
    padding: 6px 8px;
  }

  .current-flag {
    width: 20px;
    height: 20px;
  }

  .flag-option {
    width: 20px;
    height: 20px;
  }

  .elements_footer {
    padding: 12px 10px;
  }
  
  .elements_footer h2 {
    font-size: 15px;
  }
  
  .elements_footer p {
    font-size: 13px;
  }
  
  #description {
    font-size: 11px;
  }
  
  #linkedin {
    width: 50px;
  }
  
  #lienIn {
    height: 40px;
  }

  #calculator {
    padding: 15px 5px; /* Valeurs originales pour très petits écrans */
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 0; /* Pas de marge négative sur mobile */
  }
}
</style>