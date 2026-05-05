<template>
  <CrudListPage
    title="Commodités"
    modelName="commodite"
    apiRouteName="commodite"
    itemLabel="une commodité"
    idField="id_commodite"
    :columns="columns"
    :bgColor="'#154889'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];
const searchFields = ['description'];
</script>
