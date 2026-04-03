<template>
  <h2>Bienvenue</h2>
  <!-- <button @click="goToAbout">Go to about</button>
  Params : {{ $route.params }} -->
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

function goToAbout() {
  router.push("/about");
}
</script>
