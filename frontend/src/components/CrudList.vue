<template>
  <div>
    <h2 class="w3-center">{{ title }}</h2>

    <div class="header-actions">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Recherche..."
      />

      <button
        class="w3-button add-btn"
        v-if="crud.can('add')"
        @click="crud.openAdd"
      >
        <font-awesome-icon icon="plus" /> Ajouter
      </button>
    </div>

    <Grid2
      :data="filteredData"
      :columns="columns"
      :columnLabels="columnLabels"
      :actions="crud.actions"
      :idField="idField"
      :bgColor="bgColor"
      @view="crud.openView"
      @edit="crud.openEdit"
      @delete="crud.deleteItem"
    />

    <Modal :show="crud.showModal.value">
      <component
        :is="formComponent"
        :initialForm="crud.selectedItem.value"
        :itemLabel="title"
        :mode="crud.mode.value"
        :onClose="crud.closeModal"
        :onSubmit="handleSubmit"
      />
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import Grid2 from "./Grid2.vue";
import Modal from "./Modal.vue";

const currentItem = ref(null);

const props = defineProps({
  modelName: String,
  apiRouteName: String,
  title: String,
  columns: Array,
  columnLabels: Object,
  idField: { type: String, default: "id" },
  formComponent: Object,
  bgColor: { type: String, default: "#42b983" },
});

import { useCrud } from "../composables/useCrud";
const crud = useCrud(props.modelName, props.apiRouteName, props.idField);

const searchQuery = ref("");

const filteredData = computed(() => {
  const items = crud.items.value;
  if (!searchQuery.value) return items;

  const q = searchQuery.value.toLowerCase();
  return items.filter(item =>
    JSON.stringify(item).toLowerCase().includes(q)
  );
});

onMounted(crud.fetchAll);

const handleSubmit = async (formData) => {
  if (crud.mode.value === "add") {
    await crud.createItem(formData);
  } else if (crud.mode.value === "edit" || crud.mode.value === "change") {
    await crud.updateItem(formData);
  }
  crud.closeModal();
};
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}
</style>
