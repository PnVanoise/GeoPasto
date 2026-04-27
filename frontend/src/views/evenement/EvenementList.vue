<template>
  <CrudListPage
    title="Événements"
    modelName="evenement"
    apiRouteName="evenement"
    itemLabel="un événement"
    idField="id_evenement"
    :geojsonMode="true"
    :columns="columns"
    :bgColor="'#9b2423'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '@/components/CrudListPage.vue';

const columns = [
  { field: "date_evenement", label: "Date",        sortable: true },
  { field: "description",    label: "Description", sortable: false },
  { field: "observateur",    label: "Observateur", sortable: true },
];

const searchFields = ['date_evenement', 'description', 'observateur'];
</script>
