<!-- src/views/Unauthorized.vue -->
<template>
    <div class="unauthorized">
        <h1>403 — Accès refusé</h1>
        <p>Vous n'avez pas les permissions nécessaires pour voir cette page.</p>
        <router-link to="/">Retour à l'accueil</router-link>
    </div>
</template>

<script setup>
</script>

<style scoped>
.unauthorized {
    padding: 2rem;
    text-align: center;
}
</style>