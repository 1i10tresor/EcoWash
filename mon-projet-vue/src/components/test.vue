<template>
    <div>
      <p>Formulaire EcoAdd chargé 🎉</p>
      <button @click="onClick">Cliquez-moi</button>
    </div>
</template>
  
<script>
export default {
name: 'CalculatorForm',
setup() {
    function onClick() { alert('OK') }
    return { onClick }
}
}
</script>

<style scoped>
</style>