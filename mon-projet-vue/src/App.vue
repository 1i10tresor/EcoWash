<template>
  <div class="main_container">
    <header>
      <h1>Calculateur d'additifs EcoAdd</h1>
    </header>

    <div id="calculator">
      <CalculatorForm />
    </div>

    <footer>

      <div id="mainFooter">
        <a href="https://spring-coating.com" target="_blank">https://spring-coating.com</a>
      </div>

      <div id="lowFooter">
        <p>Copyright © 2025 Spring Coating Systems. Tous droits réservés.</p>
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

/* Footer */
footer {
  text-align: center;
  color: white;
  background-color: #333;
  padding: 20px 10px;
  font-size: 14px;
  display: flex;
  flex-direction: column;
}

footer a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: bold;
}

footer a:hover {
  text-decoration: underline;
}
</style>