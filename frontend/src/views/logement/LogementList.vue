<template>
  <CrudListPage
    title="Logements"
    modelName="logement"
    apiRouteName="logement"
    :geojsonMode="true"
    itemLabel="un logement"
    idField="id"
    :columns="columns"
    :bgColor="'#2e7d32'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from "../../components/crud/CrudListPage.vue";

const columns = [
  { field: "logement_code", label: "Code", sortable: true },
  { field: "nom_logement", label: "Nom", sortable: true },
  { field: "unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "statut", label: "Statut", sortable: true },
];
const searchFields = ["logement_code", "nom_logement"];
</script>
