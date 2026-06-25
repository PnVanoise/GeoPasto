<template>
  <CrudListPage
    title="Cheptels"
    modelName="cheptel"
    apiRouteName="cheptel"
    itemLabel="un cheptel"
    idField="id_cheptel"
    :columns="columns"
    :bgColor="'#317f43'"
    :searchFields="searchFields"
    :filters="cheptelFilters"
  />
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import CrudListPage from "../../components/crud/CrudListPage.vue";
import auth from "@/services/axios";

const columns = [
  { field: "proprietaire_label", label: "Propriétaire", sortable: true },
  { field: "situation_detail.unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "annee", label: "Année", sortable: true },
  { field: "description", label: "Description", sortable: true },
  { field: "nombre_animaux", label: "Nombre d'animaux", sortable: true },
];

const searchFields = [
  "proprietaire_label",
  "situation_detail.unite_pastorale_detail.nom_up",
  "description",
  "nombre_animaux",
  "annee",
];

const upOptions = ref([]);

const cheptelFilters = ref([
  {
    key: "annee_courante",
    type: "checkbox",
    label: `Année courante (${new Date().getFullYear()})`,
    default: false,
    apply: (rows, value) =>
      !value ? rows : rows.filter((r) => r.annee === new Date().getFullYear()),
  },
  {
    key: "up",
    type: "select",
    label: "Unité pastorale",
    options: upOptions,
    default: "",
    apply: (rows, value) =>
      !value
        ? rows
        : rows.filter(
            (r) => r.situation_detail?.unite_pastorale_detail?.id_unite_pastorale == Number(value)
          ),
  },
]);

onMounted(async () => {
  const r = await auth.axiosInstance.get("/unitePastorale/light/");
  upOptions.value = r.data.map((f) => ({ label: f.nom_up, value: f.id_unite_pastorale }));
});
</script>
