<template>
  <div class="form-page">
    <div v-if="isLoading" class="loading-state">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <CheptelForm2
      v-else
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un cheptel"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrud } from "@/composables/useCrud";
import CheptelForm2 from "@/components/CheptelForm2.vue";
import auth from "@/../auth";
import config from "@/../config";

const route = useRoute();
const router = useRouter();

const crud = useCrud("cheptel", "cheptel", "id_cheptel");

const pageMode = computed(() => {
  if (route.name === "cheptel-add")  return "add";
  if (route.name === "cheptel-edit") return "change";
  return "view";
});

const itemData  = ref({});
const isLoading = ref(!!route.params.id);

onMounted(async () => {
  if (route.params.id) {
    try {
      const response = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/cheptel/${route.params.id}/`
      );
      itemData.value = response.data ?? {};
    } catch (e) {
      console.error("Erreur lors du chargement du cheptel", e);
    } finally {
      isLoading.value = false;
    }
  } else if (route.query.situation) {
    itemData.value = {
      situation_exploitation: Number(route.query.situation),
      ...(route.query.exploitant ? { exploitant: Number(route.query.exploitant) } : {}),
    };
  }
});

async function handleSubmit(formData) {
  if (pageMode.value === "add") {
    await crud.createItem(formData);
  } else {
    await crud.updateItem(formData);
  }
  router.back();
}
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
