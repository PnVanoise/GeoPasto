<template>
  <CrudListPage
    title="Suivis"
    modelName="plandesuivi"
    apiRouteName="planSuivi"
    itemLabel="un suivi"
    idField="id_plan_suivi"
    :columns="columns"
    :bgColor="'#f7ba0b'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from "../../components/crud/CrudListPage.vue";

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "date_debut", label: "Début", sortable: true },
  { field: "date_fin", label: "Fin", sortable: true },
];
const searchFields = ["description"];
</script>
