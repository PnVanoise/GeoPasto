<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <GardeSituationForm2
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un gardiennage"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import GardeSituationForm2 from "../../features/garde_situation/GardeSituationForm2.vue";
import auth from '@/services/axios';
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("gardesituation", "gardeSituation", "id_garde_situation");
const { pageMode, handleSubmit } = crud;

const itemData  = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/gardeSituation/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
      console.error("Erreur lors du chargement du gardiennage", e);
    } finally {
      isLoading.value = false;
    }
  } else if (route.query.situation) {
    itemData.value = { situation_exploitation: Number(route.query.situation) };
  }
});
</script>

<style scoped>
.form-page { max-width: 860px; margin: 2rem auto; padding: 0 1rem; }
.loading-state { display: flex; justify-content: center; padding: 4rem 0; }
</style>
