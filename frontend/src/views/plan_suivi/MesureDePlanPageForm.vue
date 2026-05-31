<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <MesureDePlanForm2
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="une mesure de plan"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import MesureDePlanForm2 from "../../features/plan_suivi/MesureDePlanForm2.vue";
import auth from "@/services/axios";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const { pageMode, handleSubmit } = useCrudPage("mesuredeplan", "mesurePlan", "id_mesure_plan", {
  geojson: true,
});

const itemData = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/mesurePlan/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
    } finally {
      isLoading.value = false;
    }
  } else {
    const prefill = {};
    if (route.query.plan_suivi) prefill.plan_suivi = Number(route.query.plan_suivi);
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
