<template>
  <div class="form-page">
    <TypeCheptelForm2
      :initialForm="itemData"
      :mode="pageMode"
      itemLabel="un type de cheptel"
      :onSubmit="handleSubmit"
      :onClose="() => router.back()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import TypeCheptelForm2 from "@/components/TypeCheptelForm2.vue";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("type_cheptel", "type_cheptel", "id_type_cheptel");

/**
 * Mode déduit depuis le nom de la route :
 *   type_cheptel-add  → "add"
 *   type_cheptel-edit → "change"
 *   type_cheptel-view → "view"
 */
const pageMode = computed(() => {
  if (route.name === "type_cheptel-add")  return "add";
  if (route.name === "type_cheptel-edit") return "change";
  return "view";
});

const itemData = ref({});

onMounted(async () => {
  if (route.params.id) {
    await crud.fetchAll();
    const found = crud.items.value.find(
      (i) => String(i.id_type_cheptel ?? i.id) === String(route.params.id)
    );
    itemData.value = found ?? {};
  }
});

async function handleSubmit(formData) {
  if (pageMode.value === "add") {
    await crud.createItem(formData);  // redirige automatiquement vers type_cheptel-list
  } else {
    await crud.updateItem(formData);  // idem
  }
}
</script>

<style scoped>
.form-page {
  max-width: 860px;
  margin: 2rem auto;
  padding: 0 1rem;
}
</style>
