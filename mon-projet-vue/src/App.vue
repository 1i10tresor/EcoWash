<template>
  <div class="main_container">
    <header>
      <h1>Calculateur d'additifs EcoAdd</h1>
    </header>

    <div id="calculator">
      <CalculatorForm />
    </div>

    <footer>

        <div id="topFooter">

            <div id="logo">
                <img src="../src/assets/logo.png" alt="Logo" />
            </div>

            <div id="adresse">
                <h2>Spring Coating Systems</h2>
                <p>18 rue de la Fabrique</p>
                <p>68530 BUHL</p>
                <p>Tél : 03 89 83 06 82</p>
            </div>
            <div id="contact">
                <h2>Contact</h2>
                <a href="mailto:contact@spring-coating.com">contact@spring-coating.com</a>
                
                <p>Tél : 03 89 83 06 82</p>
            </div>

            <div id="description">
                <a href="https://www.linkedin.com/company/spring-coating-systems/" target="_blank" id="lienIn"><img id="linkedin" src="../src/assets/linkedin.png" alt="Logo"></a>
                <p>Spring Coating Systems est formulateur et fabricant d’encres, vernis, colles, et peintures pour des applications industrielles et l’impression d'emballages. Nos produits sont souvent formulés sur mesure et adaptés à l’activité de nos clients. Les principaux produits de Spring Coating pour l'impression d'emballage sont : l’encre UV, l’encre pour contact alimentaire direct, les encres à l'eau et des encres de spécialité comme des encres « grattables », etc.</p>
            </div> 

        </div>

        <div id="botFooter">
            <h3>Copyright 2025 Spring Coating Systems. All rights reserved</h3>
        </div>
    </footer>
  </div>
</template>

<script>
import { CanceledError } from 'axios';
import CalculatorForm from './components/CalculatorForm.vue';

export default {
  name: 'App',
  components: { CalculatorForm },
};
</script>

<style scoped>
/* Conteneur principal */
.main_container {
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
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  font-size: 28px;
}

/* Contenu principal */
#calculator {
  margin: auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

footer{
        height: 120px;
        color: rgb(231, 228, 222);
    }
    #topFooter{
        height: 90%;
        border: 1px solid black;
        background-color: rgb(48, 42, 42);
        display: flex;
    }
    #botFooter{
        height: 10%;
        border: 1px solid black;
        background-color: rgb(48, 42, 42);
        border-top: 0.5px solid rgb(241, 243, 220);
        font-size: x-small;
    }

    #logo{
        width: 20%;
        padding: 20px;
        display: flex;
        justify-content: center;
        transition: all 0.3s ease-in-out;
    }
    #adresse{
        width: 20%;
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        transition: all 0.3s ease-in-out;
    }
    #contact{
        width: 20%;
        display: flex;
        justify-content: center;
        align-items :center;  
        flex-direction: column;
        transition: all 0.3s ease-in-out;
    }
    #description{
        width: 40%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-justify: justify;
        align-items: center;
        font-size: xx-small;
    }
    a{
        text-decoration: none;
        color: rgb(241, 243, 220);

    }
    #linkedin{
        width: 100px;
        background-color: transparent !important;
    }
    /* #linkedin:hover{
        border-radius: 10px;
        border: 1px solid rgb(241, 243, 220);
    } */

    #lienIn{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 50px;
        border-bottom: 1px solid rgb(241, 243, 220);
        margin-bottom: 10px;
        transition: all 0.3s ease-in-out;
    }

    #lienIn:hover, #contact:hover, #adresse:hover, #logo:hover{
        border-radius: 10px;
        transform: scale(1.05);
    }

    @media (max-width:768px) {
        #topFooter {
            flex-direction: column;
            height: auto;
            align-items: center;
            justify-content: center;

        }
    }
</style>