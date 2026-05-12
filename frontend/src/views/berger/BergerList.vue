<template>
  <CrudListPage
    title="Bergers"
    modelName="berger"
    apiRouteName="berger"
    itemLabel="un berger"
    idField="id_berger"
    :columns="columns"
    :bgColor="'#d4652f'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from "../../components/crud/CrudListPage.vue";

const columns = [
  { field: "nom_berger", label: "Nom", sortable: true },
  { field: "prenom_berger", label: "Prénom", sortable: true },
];

const searchFields = ["nom_berger", "prenom_berger"];
</script>
