<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <EquipementAlpageForm2
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un équipement alpage"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrud } from "@/composables/useCrud";
import EquipementAlpageForm2 from "../../features/equipement/EquipementAlpageForm2.vue";
import auth from "@/services/axios";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrud("equipementalpage", "equipementAlpage", "id_equipement_alpage", {
  geojson: true,
});

const pageMode = computed(() => {
  if (route.name === "equipementalpage-add") return "add";
  if (route.name === "equipementalpage-edit") return "change";
  return "view";
});

const itemData = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/equipementAlpage/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
      console.error("Erreur lors du chargement de l'équipement alpage", e);
    } finally {
      isLoading.value = false;
    }
  } else if (route.query.unite_pastorale) {
    itemData.value = { unite_pastorale: Number(route.query.unite_pastorale) };
  }
});

async function handleSubmit(formData) {
  if (pageMode.value === "add") {
    await crud.createItem(formData);
  } else {
    await crud.updateItem({ ...formData, id_equipement_alpage: Number(route.params.id) });
  }
  router.back();
}
</script>

<style scoped>
.form-page {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem 0;
}
</style>
