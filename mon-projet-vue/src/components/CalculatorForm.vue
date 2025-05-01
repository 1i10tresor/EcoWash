<template>
    <div class="app-container">
      <!-- Bandeau Haut -->
      <header class="header-banner">
        <h1>Eco Wash Balancing System</h1>
      </header>
  
      <!-- Contenu Principal -->
      <main class="calculator">
        <h2>Calculateur d'additifs</h2>
        <form @submit.prevent="calculate">
          <div class="form-group">
            <label>Densité mesurée :</label>
            <input v-model.number="density" type="number" step="0.0001" required>
          </div>
          <div class="form-group">
            <label>Indice de réfraction :</label>
            <input v-model.number="refractionIndex" type="number" step="0.0001" required>
          </div>
          <button type="submit">Calculer</button>
        </form>
  
        <div v-if="result" class="result">
  <h3>Résultats :</h3>
  
  <div class="result-section">
    <h4>Fractions :</h4>
    <ul>
      <li><strong>ISOL</strong> : {{ result.fractions.ISOL.toFixed(4) }}</li>
      <li><strong>BZOH</strong> : {{ result.fractions.BZOH.toFixed(4) }}</li>
      <li><strong>DIPB</strong> : {{ result.fractions.DIPB.toFixed(4) }}</li>
      <li><strong>ETOH</strong> : {{ result.fractions.ETOH.toFixed(4) }}</li>
    </ul>
  </div>

  <div class="result-section">
    <h4>Additifs à ajouter (mL) :</h4>
    <ul>
      <li v-if="result.additives.EcoAdd1 > 0">
        <strong>EcoAdd1 (ISOL)</strong> : {{ result.additives.EcoAdd1.toFixed(2) }}
      </li>
      <li v-if="result.additives.EcoAdd2 > 0">
        <strong>EcoAdd2 (BZOH)</strong> : {{ result.additives.EcoAdd2.toFixed(2) }}
      </li>
      <li v-if="result.additives.EcoAdd3 > 0">
        <strong>EcoAdd3 (DIPB)</strong> : {{ result.additives.EcoAdd3.toFixed(2) }}
      </li>
      <li v-if="Object.values(result.additives).every(v => v <= 0)">
        Aucun additif nécessaire
      </li>
    </ul>
  </div>
</div>
  
        <div v-if="error" class="error">
          {{ error }}
        </div>
      </main>
  
      <!-- Bandeau Bas -->
      <footer class="footer-banner">
        <div class="footer-content">
          <img :src="logoUrl" alt="Spring Coating Systems Logo" class="logo">
          <div class="copyright">
            <p>Copyright © 2025 Spring Coating Systems. All rights reserved.</p>
            <a href="https://spring-coating.com" target="_blank">https://spring-coating.com</a>
          </div>
        </div>
      </footer>
    </div>
  </template>
  
  <script>
import logo from '../assets/logo.png';

export default {
  data() {
    return {
      logoUrl: logo,
      density: null,
      refractionIndex: null,
      result: null,
      error: null,
      apiUrl: process.env.NODE_ENV === 'development' 
        ? '/api/calculate'  // Utilise le proxy en développement
        : '/calculate'      // En production
    }
  },
  methods: {
    async calculate() {
  try {
    this.error = null;
    this.result = null;
    
    // Conversion explicite en nombres
    const density = parseFloat(this.density);
    const refractionIndex = parseFloat(this.refractionIndex);

    if (isNaN(density) || isNaN(refractionIndex)) {
      throw new Error("Veuillez entrer des valeurs numériques valides");
    }

    const response = await fetch(this.apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        density: density,
        refractionIndex: refractionIndex
      })
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || "Erreur du serveur");
    }

    // Debug: affiche la réponse dans la console
    console.log("Réponse API:", data);
    
    // Formatage des résultats
    this.result = {
      fractions: {
        ISOL: data.result.fractions.ISOL,
        BZOH: data.result.fractions.BZOH,
        DIPB: data.result.fractions.DIPB,
        ETOH: data.result.fractions.ETOH
      },
      additives: {
        EcoAdd1: data.result.additives.EcoAdd1 || 0,
        EcoAdd2: data.result.additives.EcoAdd2 || 0,
        EcoAdd3: data.result.additives.EcoAdd3 || 0
      }
    };

  } catch (err) {
    this.error = err.message || "Erreur lors du calcul";
    console.error("Détails de l'erreur:", err);
  }

    }
  }
}
</script>
  
  <style scoped>
  * {
    margin: 0;
    padding: 0;
  }
  .app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  .header-banner {
    background-color: #42b983;
    color: white;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .calculator {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    flex: 1;
  }
  
  .footer-banner {
    background-color: #000;
    color: white;
    padding: 1.5rem 0;
    margin: 0;
    width: 100%;
  }
  
  .footer-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
  }
  
  .logo {
    height: 40px;
    width: auto;
  }
  
  .copyright {
    text-align: center;
  }
  
  .copyright p {
    margin: 0.3rem 0;
    font-size: 0.9rem;
  }
  
  .copyright a {
    color: #42b983;
    text-decoration: none;
    font-size: 0.9rem;
  }
  
  .copyright a:hover {
    text-decoration: underline;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  button {
    background-color: #42b983;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
  }
  
  button:hover {
    background-color: #3aa876;
  }
  
  .result {
    margin-top: 2rem;
    padding: 1rem;
    background: white;
    border-radius: 4px;
  }
  
  .error {
    color: #e74c3c;
    margin-top: 1rem;
    padding: 0.5rem;
    background: #fdecea;
    border-radius: 4px;
  }
  
  ul {
    list-style-type: none;
    padding: 0;
  }
  
  li {
    padding: 0.25rem 0;
  }
  
  @media (max-width: 768px) {
    .footer-content {
      flex-direction: column;
      gap: 1rem;
    }
    
    .logo {
      height: 30px;
    }
  }
  </style>