<template>
  <div id = "calculator">

    <h1>EcoWash Balancing</h1>

    <div id="main">
      <form id="parametres">


        <div id="EW_version">
          <label for="version">Choix du modèle</label><br>
          <select name="version" id="modele">
            <option value="" disabled selected>-- Séléctionez une version --</option>
            <option value="EcoWash">EcoWash</option>
            <option value="EcoWash 3D">EcoWash 3D</option>
            <option value="EcoWash-4">EcoWash-4</option>
            <option value="EcoWash T-sol">EcoWash T-sol</option>
          </select>
        </div> 

        <div id="choix">
          <div id="IRS">
            <input type="radio" id="IR" name="choix" value="IR">
            <label for="IR">IR</label><br>
          </div>
          <div id="BRIXS">
            <input type="radio" id="BRIX" name="choix" value="BRIX">
            <label for="BRIX">BRIX</label><br>
          </div>
        </div>
      
        <div id="saisie">

          <div class="zone_texte">
            <label for="nb_lots">Nb de lots</label><br>
            <input type="number" id="nb_lots" class="zone_saisie" name="nb_lots" placeholder="Nb lots">
          </div>

          <div class="zone_texte">
            <label for="saisie_dentite">Densité</label><br>
            <input type="number" class="zone_saisie" id="saisie_densite" name="saisie" placeholder="Densité">
          </div>

          <div class="zone_texte">
            <label for="saisie_refraction">Réfraction</label><br>
            <input type="number" class="zone_saisie" id="saisie_refraction" name="saisie" placeholder="Réfraction">
          </div>
        </div>
      </form>
      <div id="resultat">
        <p>Resultat</p>

        <div id="EcoAdd 1">Ajouter x volume d'EcoAdd 1

        </div>

        <div id="EcoAdd 2">Ajouter x volume d'EcoAdd 2

        </div>

        <div id="EcoAdd 3">Ajouter x volume d'EcoAdd 3

        </div>
      </div>
    </div>

    


    <button>Calculer</button>
  </div>
  
</template>
  
<script>
  export default {
    
  }
</script>
  
<style scoped>
  #calculator {
    margin-top:5% ;
    margin-left: auto;
    margin-right: auto;
    width: 500px;
    padding: 10px;
    height: 500px;
    border-radius: 10px;
    background: #ffffff;
    box-shadow: 10px 10px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    border: #000000 solid 1px;
  }

  #saisie {
    margin-top: 30px;
    display: flex;
    flex-direction: ROW;
    align-items: center;
    justify-content: space-around;
    height: 25%;
    width: 75%;
  }
  
  #choix {
    margin-top: 30px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-around;
    height: 20%;
  }

  #IRS, #BRIXS {
    padding : 30px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-around;
  }
  
  .zone_texte {
    display: flex;
    flex-direction: column;
    width: 80px;
  }

  #main {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    flex: 1;
  }

  #parametres {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    width: 100%;
    height: 200px;
  }

  h1{
    font-size: 30px;
    text-align: center;
    border: #000000 solid 1px;
  }
</style>