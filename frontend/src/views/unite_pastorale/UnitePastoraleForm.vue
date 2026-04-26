<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <UnitePastoraleFormFields
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="une unité pastorale"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import UnitePastoraleFormFields from "@/components/UnitePastoraleForm2.vue";
import auth from "@/../auth";
import config from "@/../config";

const route  = useRoute();
const router = useRouter();

const crud = useCrudPage("unitepastorale", "unitePastorale", "id", { geojson: true });

const pageMode = computed(() => {
  if (route.name === "unitepastorale-add")  return "add";
  if (route.name === "unitepastorale-edit") return "change";
  return "view";
});

const itemData  = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/unitePastorale/${route.params.id}/`
      );
      const found = response.data;
      if (found) {
        itemData.value = {
          id:         found.id ?? found.properties?.id_unite_pastorale,
          geometry:   found.geometry ?? null,
          properties: { ...(found.properties ?? found) },
        };
        delete itemData.value.properties.geometry;
      }
    } catch (e) {
      console.error("Erreur lors du chargement de l'UP", e);
    } finally {
      isLoading.value = false;
    }
  }
});

async function handleSubmit(formData) {
  if (pageMode.value === "add") {
    await crud.createItem(formData);  // redirige vers unitepastorale-list
  } else {
    await crud.updateItem(formData);  // idem
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
