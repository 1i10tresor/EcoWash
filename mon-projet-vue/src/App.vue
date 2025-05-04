<template>
  <div class="main_container">
    <header>
      <h1>Calculateur d'additifs EcoAdd</h1>
    </header>
    <div id="app">
      <CalculatorForm />
    </div>
    <footer>
      <p>Copyright © 2025 Spring Coating Systems. All rights reserved.</p>
      <a href="https://spring-coating.com" target="_blank">https://spring-coating.com</a>
    </footer>
  </div>
</template>




<script>
import CalculatorForm from './components/CalculatorForm.vue'

export default {
  name: 'App',
  components: { CalculatorForm }
}
</script>

<style scoped>

  .main_container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    color: #000000;
    padding: 10px;
    text-align: center;
  }

  h1 {
    margin: 0;
  }
  #app {
    flex: 1;
    background-color: rgb(231, 231, 231);
  }
  footer {
    text-align: center;
    color: #fff;
    margin-bottom: 0;
    background-color: black;
    height: 100px;
  }

  a{
    color: #fff;
  }


</style>