<template>
  <CrudList2
    title="Abris d'urgence"
    modelName="abridurgence"
    apiRouteName="abriDUrgence"
    itemLabel="un abri d'urgence"
    idField="id_abri_urgence"
    :columns="columns"
    :formComponent="AbriDUrgenceForm2"
    :bgColor="'#154889'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudList2 from './CrudList2.vue';
import AbriDUrgenceForm2 from './AbriDUrgenceForm2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "etat", label: "Etat", sortable: true },
];

const searchFields = [
  'description',
  'etat',
];

</script>
