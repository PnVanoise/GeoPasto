<template>
  <form @submit.prevent="login">
    <v-text-field variant="underlined"
      density="compact" v-model="userCredentials.username" label="Nom d'utilisateur" required />
    <v-text-field variant="underlined"
      density="compact" v-model="userCredentials.password" label="Mot de passe" type="password" required />
    <v-btn
      class="submit-btn" density="compact" type="submit" color="info">Connexion</v-btn>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useMainStore } from "../store";
import auth from "../../auth";

const router = useRouter();
const mainStore = useMainStore();

const userCredentials = ref({
  username: "",
  password: "",
});

const login = async () => {
  try {
    const response = await auth.axiosInstance.post("token/", {
      username: userCredentials.value.username,
      password: userCredentials.value.password,
    });

    const userData = {
      access: response.data.access,
      refresh: response.data.refresh,
      username: userCredentials.value.username,
    };

    // ⚡ Met à jour le store ET localStorage
    mainStore.setUser(userData);

    // ⚡ Configure Axios globalement
    auth.axiosInstance.defaults.headers.common["Authorization"] = `Bearer ${response.data.access}`;

    router.push("/"); // redirection automatique vers la home

  } catch (error) {
    if (error.response?.status === 401) {
      alert("Nom d’utilisateur ou mot de passe incorrect !");
    } else {
      console.error("Erreur lors de la connexion :", error);
      mainStore.setErrorMessage("Erreur lors de la connexion.");
    }
  }
};
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: 0.2em;
  margin: 5px;
}
.submit-btn {
  align-self: flex-start;
  margin-top: 0;
}
</style>
<style scoped>


</style>