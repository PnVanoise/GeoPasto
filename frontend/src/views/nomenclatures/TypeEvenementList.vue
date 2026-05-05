<template>
  <CrudListPage
    title="Types d'événements"
    modelName="typeevenement"
    apiRouteName="typeEvenement"
    itemLabel="un type d'événement"
    idField="id_type_evenement"
    :columns="columns"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns    = [{ field: "description", label: "Description", sortable: true }];
const searchFields = ['description'];
</script>