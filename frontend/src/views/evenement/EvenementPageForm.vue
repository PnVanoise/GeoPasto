<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <EventForm2
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un événement"
      :contextIds="contextIds"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrud } from "@/composables/useCrud";
import EventForm2 from "../../features/evenement/EventForm2.vue";
import auth from "@/services/axios";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrud("evenement", "evenement", "id_evenement", { geojson: true });

const pageMode = computed(() => {
  if (route.name === "evenement-add") return "add";
  if (route.name === "evenement-edit") return "change";
  return "view";
});

const contextIds = computed(() => ({
  idSituation: route.query.context_id_situation ? Number(route.query.context_id_situation) : null,
}));

const itemData = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/evenement/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
    } finally {
      isLoading.value = false;
    }
  } else if (route.query.situation) {
    itemData.value = { situation: Number(route.query.situation) };
  }
});

async function handleSubmit(formData) {
  if (pageMode.value === "add") {
    await crud.createItem(formData);
  } else {
    await crud.updateItem({ ...formData, id_evenement: Number(route.params.id) });
  }
  router.back();
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
