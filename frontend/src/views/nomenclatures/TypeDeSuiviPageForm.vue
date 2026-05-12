<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <TypeDeSuiviForm2
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un type de suivi"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import TypeDeSuiviForm2 from "../../features/nomenclatures/TypeDeSuiviForm2.vue";
import auth from "@/services/axios";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("typedesuivi", "typeSuivi", "id_type_suivi");
const { pageMode, handleSubmit } = crud;

const itemData = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/typeSuivi/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
    } finally {
      isLoading.value = false;
    }
  }
});
</script>

<style scoped>
.form-page {
  max-width: 860px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem 0;
}
</style>
