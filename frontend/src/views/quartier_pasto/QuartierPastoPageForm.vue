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
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import QuartierPastoForm from "@/components/QuartierPastoForm.vue";
import auth from '@/services/axios';
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("quartierpasto", "quartierPasto", "id_quartier", { geojson: true });

const pageMode = computed(() => {
  if (route.name === "quartierpasto-add")  return "add";
  if (route.name === "quartierpasto-edit") return "change";
  return "view";
});

const itemData  = ref(null);
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/quartierPasto/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
      console.error("Erreur lors du chargement du quartier", e);
    } finally {
      isLoading.value = false;
    }
  } else {
    itemData.value = {
      properties: {
        ...(route.query.situation ? { situation_exploitation: Number(route.query.situation) } : {}),
        ...(route.query.up        ? { unite_pastorale:       Number(route.query.up)        } : {}),
      },
    };
  }
});

async function handleSubmit(formData) {
  if (pageMode.value === "add") {
    await crud.createItem(formData);
  } else {
    await crud.updateItem(formData);
  }
}
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
