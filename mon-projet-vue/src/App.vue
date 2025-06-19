<template>
  <div id="main_container">
    <header>
      <div id="logo-container">
        <img src="/logoEcoWash.png" alt="Ecowash Logo" id="header-logo" />
      </div>
      <div id="title-container">
        <h1 class="desktop-title">{{ translations[currentLanguage].headerTitle }}</h1>
        <h1 class="mobile-title">{{ translations[currentLanguage].headerTitleMobile }}</h1>
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
      <CalculatorForm />
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
      languageSelector
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

/* Header */
header {
  background-color: #FCFCFC;
  color: #45a049;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  backdrop-filter: blur(10px);
}

/* Logo container - occupe 75% de l'espace */
#logo-container {
  flex: 0 0 75%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

#header-logo {
  max-height: 60px;
  max-width: 100%;
  height: auto;
  object-fit: contain;
}

/* Conteneur du titre - centré absolument */
#title-container {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

#title-container h1 {
  margin: 0;
  font-size: 28px;
  text-align: center;
  white-space: nowrap;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
}

/* Titres desktop et mobile */
.desktop-title {
  display: block;
}

.mobile-title {
  display: none;
}

/* Language switcher */
#language-switcher {
  flex: 0 0 auto;
  z-index: 2;
}

.language-selector {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 8px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.language-selector:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.current-flag {
  width: 25px;
  height: 25px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.arrow {
  font-size: 12px;
  transition: transform 0.3s ease;
  color: #45a049;
  font-family: 'Space Mono', monospace;
}

.arrow.open {
  transform: rotate(180deg);
}

.language-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background-color: #FCFCFC;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 1000;
  min-width: 140px;
}

.language-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: #333;
  font-size: 14px;
  font-family: 'Space Mono', monospace;
}

.language-option:hover {
  background-color: #f5f5f5;
}

.flag-option {
  width: 25px;
  height: 25px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Contenu principal */
#calculator {
  margin: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

footer {
  height: 100px; /* Hauteur augmentée de 80px à 100px */
  color: rgb(231, 228, 222);
  box-shadow: 0 -5px 10px -5px rgba(0, 0, 0, 0.3);
}

#topFooter {
  height: 100%;
  border: 1px solid black;
  background-color: rgba(37, 34, 34, 0.95);
  display: flex;
  backdrop-filter: blur(10px);
  align-items: center; /* Centrage vertical pour aligner les titres */
}

.elements_footer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 15px; /* Padding légèrement augmenté */
  text-align: center;
  transition: all 0.3s ease-in-out;
  font-family: 'Space Mono', monospace;
  background-color: rgba(37, 34, 34, 0.95);
  box-sizing: border-box;
  overflow: hidden;
  height: 100%;
}

.elements_footer h2 {
  margin: 0 0 8px 0; /* Marge légèrement augmentée */
  font-size: 15px; /* Taille de police légèrement augmentée */
}

.elements_footer p {
  margin: 1px 0; /* Marge réduite pour l'adresse */
  font-size: 13px; /* Taille de police légèrement augmentée */
}

#logo {
  flex: 1;
  min-width: 150px;
}

#logo img {
  max-height: 60px; /* Hauteur du logo légèrement augmentée */
  width: auto;
}

#adresse {
  flex: 1;
  min-width: 180px;
}

#adresse p {
  margin: 1px 0; /* Espacement réduit spécifiquement pour l'adresse */
}

#contact {
  flex: 1;
  min-width: 180px;
}

#description {
  flex: 2;
  min-width: 250px;
  font-size: 10px; /* Taille de police réduite pour voir le logo LinkedIn */
}

a {
  text-decoration: none;
  color: rgb(241, 243, 220);
  font-size: 13px; /* Taille de police légèrement augmentée */
}

#linkedin {
  width: 70px; /* Taille légèrement augmentée */
  background-color: transparent !important;
}

#lienIn {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px; /* Hauteur légèrement augmentée */
  border-bottom: 1px solid rgb(241, 243, 220);
  margin-bottom: 8px; /* Marge légèrement augmentée */
  transition: all 0.3s ease-in-out;
}

#lienIn:hover, #contact:hover, #adresse:hover, #logo:hover {
  border-radius: 10px;
  transform: scale(1.05);
}

/* Media queries pour une meilleure responsivité */
@media (max-width: 1200px) {
  footer {
    height: 110px; /* Hauteur légèrement augmentée pour écrans moyens */
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
    /* Garde la disposition flex horizontale mais avec positionnement relatif */
    position: relative;
  }

  /* Le logo est maintenant centré absolument par rapport à toute la largeur */
  #logo-container {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 1;
  }

  #header-logo {
    max-height: 55px; /* Logo un peu plus gros */
  }

  /* Le titre disparaît complètement sur mobile */
  #title-container {
    display: none;
  }

  /* Le sélecteur de langue reste à droite */
  #language-switcher {
    position: relative;
    z-index: 2;
    margin-left: auto;
  }

  .language-selector {
    padding: 6px;
  }

  .current-flag {
    width: 20px;
    height: 20px;
  }

  .language-menu {
    right: 0;
    left: auto;
    transform: none;
    min-width: 120px;
  }

  .flag-option {
    width: 20px;
    height: 20px;
  }

  /* Centrage du calculateur sur mobile */
  #calculator {
    padding: 20px 10px;
    justify-content: center;
    align-items: center;
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
    padding: 10px;
  }

  #header-logo {
    max-height: 50px; /* Logo un peu plus gros même sur très petits écrans */
  }

  .language-selector {
    padding: 5px;
  }

  .current-flag {
    width: 18px;
    height: 18px;
  }

  .flag-option {
    width: 18px;
    height: 18px;
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

  /* Centrage renforcé pour très petits écrans */
  #calculator {
    padding: 15px 5px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
</style>