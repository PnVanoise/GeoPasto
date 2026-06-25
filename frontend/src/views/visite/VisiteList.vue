<template>
  <CrudListPage
    title="Visites"
    modelName="visite"
    apiRouteName="visite"
    itemLabel="une visite"
    idField="id_visite"
    :columns="columns"
    :bgColor="'#154889'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from "../../components/crud/CrudListPage.vue";

const columns = [
  { field: "date_visite", label: "Date", sortable: true },
  { field: "description", label: "Description", sortable: true },
];
const searchFields = ["description"];
</script>
