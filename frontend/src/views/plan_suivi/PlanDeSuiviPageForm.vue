<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <PlanDeSuiviForm
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un suivi"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import PlanDeSuiviForm from "../../features/plan_suivi/PlanDeSuiviForm.vue";
import auth from "@/services/axios";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("plandesuivi", "planSuivi", "id_plan_suivi");
const { pageMode, handleSubmit } = crud;

const itemData = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/planSuivi/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
    } finally {
      isLoading.value = false;
    }
  } else {
    const prefill = {};
    if (route.query.unite_pastorale) prefill.unite_pastorale = Number(route.query.unite_pastorale);
    itemData.value = prefill;
  }
});
</script>

<style scoped>
.form-page {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem 0;
}
</style>
