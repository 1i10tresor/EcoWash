<template>
  <div id="main_container">
    <header>
      <div id="logo-container">
        <img src="/logoEcoWash.png" alt="EcoWash Logo" id="header-logo" />
      </div>
      <div id="title-container">
        <h1>{{ translations[currentLanguage].headerTitle }}</h1>
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
          <p>{{ translations[currentLanguage].companyDescription }}</p>
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
    const currentLanguage = ref('fr');
    const showLanguageMenu = ref(false);
    const languageSelector = ref(null);
    
    const languages = [
      { code: 'fr', name: 'Français', flag: '/france.png' },
      { code: 'en', name: 'English', flag: '/etats-unis.png' },
      { code: 'de', name: 'Deutsch', flag: '/allemagne.png' }
    ];

    const currentFlag = computed(() => {
      const lang = languages.find(l => l.code === currentLanguage.value);
      return lang ? lang.flag : '/france.png';
    });

    const otherLanguages = computed(() => {
      return languages.filter(l => l.code !== currentLanguage.value);
    });

    const translations = ref({
      fr: {
        headerTitle: "Calculateur d'additifs EcoAdd",
        title: "EcoWash Balancing",
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
        calculationError: "Erreur de calcul, veuillez ressaisir les données",
        serverError: "Erreur de communication avec le serveur",
        connectionError: "Impossible de se connecter au serveur",
        unknownError: "Erreur inconnue",
        emailSent: "Email envoyé avec succès",
        emailError: "Erreur lors de l'envoi de l'email",
        phone: "Tél",
        reportProblem: "Signaler un problème",
        companyDescription: "Spring Coating Systems est formulateur et fabricant d'encres, vernis, colles, et peintures pour des applications industrielles et l'impression d'emballages. Nos produits sont souvent formulés sur mesure et adaptés à l'activité de nos clients. Les principaux produits de Spring Coating pour l'impression d'emballage sont : l'encre UV, l'encre pour contact alimentaire direct, les encres à l'eau et des encres de spécialité comme des encres « grattables », etc."
      },
      en: {
        headerTitle: "EcoAdd Additives Calculator",
        title: "EcoWash Balancing",
        modelChoice: "Model Selection",
        selectVersion: "Select a version",
        density: "Density",
        refraction: "Refraction",
        calculate: "Calculate",
        result: "Result",
        add: "Add",
        of: "of",
        calculationId: "Calculation ID",
        sendByEmail: "Send by email",
        enterEmail: "Enter your email address",
        validate: "Validate",
        error: "Error",
        calculationError: "Calculation error, please re-enter the data",
        serverError: "Server communication error",
        connectionError: "Unable to connect to server",
        unknownError: "Unknown error",
        emailSent: "Email sent successfully",
        emailError: "Error sending email",
        phone: "Tel",
        reportProblem: "Report a problem",
        companyDescription: "Spring Coating Systems is a formulator and manufacturer of inks, varnishes, adhesives, and paints for industrial applications and packaging printing. Our products are often custom-formulated and adapted to our customers' activities. Spring Coating's main products for packaging printing are: UV ink, direct food contact ink, water-based inks and specialty inks such as 'scratchable' inks, etc."
      },
      de: {
        headerTitle: "EcoAdd Additive Rechner",
        title: "EcoWash Balancing",
        modelChoice: "Modellauswahl",
        selectVersion: "Wählen Sie eine Version",
        density: "Dichte",
        refraction: "Brechung",
        calculate: "Berechnen",
        result: "Ergebnis",
        add: "Hinzufügen",
        of: "von",
        calculationId: "Berechnungs-ID",
        sendByEmail: "Per E-Mail senden",
        enterEmail: "Geben Sie Ihre E-Mail-Adresse ein",
        validate: "Bestätigen",
        error: "Fehler",
        calculationError: "Berechnungsfehler, bitte geben Sie die Daten erneut ein",
        serverError: "Server-Kommunikationsfehler",
        connectionError: "Verbindung zum Server nicht möglich",
        unknownError: "Unbekannter Fehler",
        emailSent: "E-Mail erfolgreich gesendet",
        emailError: "Fehler beim Senden der E-Mail",
        phone: "Tel",
        reportProblem: "Problem melden",
        companyDescription: "Spring Coating Systems ist Formulierer und Hersteller von Tinten, Lacken, Klebstoffen und Farben für industrielle Anwendungen und Verpackungsdruck. Unsere Produkte werden oft maßgeschneidert und an die Aktivitäten unserer Kunden angepasst. Die Hauptprodukte von Spring Coating für den Verpackungsdruck sind: UV-Tinte, Tinte für direkten Lebensmittelkontakt, wasserbasierte Tinten und Spezialtinten wie 'kratzbare' Tinten, etc."
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
}

footer {
  height: 120px;
  color: rgb(231, 228, 222);
  box-shadow: 0 -5px 10px -5px rgba(0, 0, 0, 0.3);
}

#topFooter {
  height: 100%;
  border: 1px solid black;
  background-color: rgba(37, 34, 34, 0.95);
  display: flex;
  backdrop-filter: blur(10px);
}

#logo {
  width: 20%;
  padding: 20px;
  display: flex;
  justify-content: center;
  transition: all 0.3s ease-in-out;
}

#adresse {
  width: 20%;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease-in-out;
  font-family: 'Space Mono', monospace;
}

#contact {
  width: 20%;
  display: flex;
  justify-content: center;
  align-items: center;  
  flex-direction: column;
  transition: all 0.3s ease-in-out;
  font-family: 'Space Mono', monospace;
}

#description {
  width: 40%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-justify: justify;
  align-items: center;
  font-size: xx-small;
  font-family: 'Space Mono', monospace;
}

a {
  text-decoration: none;
  color: rgb(241, 243, 220);
}

#linkedin {
  width: 100px;
  background-color: transparent !important;
}

#lienIn {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
  border-bottom: 1px solid rgb(241, 243, 220);
  margin-bottom: 10px;
  transition: all 0.3s ease-in-out;
}

#lienIn:hover, #contact:hover, #adresse:hover, #logo:hover {
  border-radius: 10px;
  transform: scale(1.05);
}

@media (max-width: 768px) {
  header {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }

  #logo-container {
    flex: none;
    width: 100%;
    justify-content: center;
    margin-bottom: 10px;
  }

  #title-container {
    position: static;
    transform: none;
    width: 100%;
  }

  #title-container h1 {
    text-align: center;
    font-size: 24px;
    white-space: normal;
  }

  #language-switcher {
    flex: none;
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .language-menu {
    right: auto;
    left: 50%;
    transform: translateX(-50%);
  }

  #topFooter {
    flex-wrap: wrap;
    height: auto;
    align-items: center;
    justify-content: center;
  }

  #contact, #adresse, #logo, #description {
    width: 50%;
    padding: 10px;
    text-align: center;
  }

  #main_container {
    overflow-x: hidden;
  }

  .elements_footer {
    border-bottom: 2px solid rgb(66, 65, 65);
  }
}
</style>