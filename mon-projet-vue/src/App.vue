<template>
  <div id="main_container">
    <header>
      <h1>{{ translations[currentLanguage].headerTitle }}</h1>
      <div id="language-switcher">
        <button 
          v-for="lang in languages" 
          :key="lang.code"
          @click="changeLanguage(lang.code)"
          :class="{ active: currentLanguage === lang.code }"
          class="lang-btn"
        >
          {{ lang.flag }} {{ lang.name }}
        </button>
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
          <a href="mailto:ecowash.balancing@spring-coating.com">ecowash.balancing@spring-coating.com</a>
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
import { ref, provide } from 'vue';
import CalculatorForm from './components/CalculatorForm.vue';

export default {
  name: 'App',
  components: { CalculatorForm },
  setup() {
    const currentLanguage = ref('fr');
    
    const languages = [
      { code: 'fr', name: 'FR', flag: '🇫🇷' },
      { code: 'en', name: 'EN', flag: '🇬🇧' },
      { code: 'de', name: 'DE', flag: '🇩🇪' }
    ];

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
    };

    // Provide the reactive values to child components
    provide('currentLanguage', currentLanguage);
    provide('translations', translations);

    return {
      currentLanguage,
      languages,
      translations,
      changeLanguage
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
  font-family: 'Roboto', sans-serif;
  color: #333;
}

/* Header */
header {
  background-color: #4CAF50;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

header h1 {
  margin: 0;
  font-size: 28px;
  flex: 1;
  text-align: center;
}

/* Language switcher */
#language-switcher {
  display: flex;
  gap: 5px;
  position: absolute;
  top: 20px;
  right: 20px;
}

.lang-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.lang-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.lang-btn.active {
  background-color: rgba(255, 255, 255, 0.9);
  color: #4CAF50;
  font-weight: bold;
}

/* Contenu principal */
#calculator {
  margin: auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

footer {
  height: 120px;
  color: rgb(231, 228, 222);
  box-shadow: 0 -5px 10px -5px rgba(0, 0, 0, 0.3);
}

#topFooter {
  height: 100%;
  border: 1px solid black;
  background-color: rgb(37, 34, 34);
  display: flex;
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
}

#contact {
  width: 20%;
  display: flex;
  justify-content: center;
  align-items: center;  
  flex-direction: column;
  transition: all 0.3s ease-in-out;
}

#description {
  width: 40%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-justify: justify;
  align-items: center;
  font-size: xx-small;
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

  #language-switcher {
    position: static;
    justify-content: center;
  }

  header h1 {
    text-align: center;
    font-size: 24px;
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