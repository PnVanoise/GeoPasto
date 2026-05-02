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
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCrudPage } from "@/composables/useCrudPage";
import TypeCheptelForm2 from "../../features/nomenclatures/TypeCheptelForm2.vue";

const route = useRoute();
const router = useRouter();

const crud = useCrudPage("typecheptel", "type_cheptel", "id_type_cheptel");
const { pageMode, handleSubmit } = crud;

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

</script>

<style scoped>
.form-page {
  max-width: 860px;
  margin: 2rem auto;
  padding: 0 1rem;
}
</style>
