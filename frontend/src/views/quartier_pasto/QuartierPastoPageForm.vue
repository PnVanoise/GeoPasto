<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <template v-else>
      <QuartierPastoForm
        :initialForm="itemData"
        :mode="pageMode"
        :isEdit="pageMode !== 'add'"
        itemLabel="un quartier pastoral"
        :onSubmit="handleSubmit"
        :onClose="() => router.back()"
        :onSplitSuccess="onSplitSuccess"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import QuartierPastoForm from "../../features/quartier_pasto/QuartierPastoForm.vue";
import auth from "@/services/axios";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("quartierpasto", "quartierPasto", "id_quartier", { geojson: true });
const { pageMode, handleSubmit } = crud;

const onSplitSuccess = (newId) => {
  if (newId) {
    router.push({ name: "quartierpasto-edit", params: { id: newId } });
  } else {
    router.push({ name: "quartierpasto-list" });
  }
};

const itemData = ref(null);
const isLoading = ref(!!route.params.id);

const loadItem = async (id) => {
  if (id) {
    isLoading.value = true;
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/quartierPasto/${id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
    } finally {
      isLoading.value = false;
    }
  } else {
    itemData.value = {
      properties: {
        ...(route.query.situation ? { situation_exploitation: Number(route.query.situation) } : {}),
        ...(route.query.up ? { unite_pastorale: Number(route.query.up) } : {}),
      },
    };
  }
};

onMounted(() => loadItem(route.params.id));

watch(
  () => route.params.id,
  (newId) => loadItem(newId)
);
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
