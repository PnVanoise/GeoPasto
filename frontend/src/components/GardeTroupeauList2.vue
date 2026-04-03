<template>
  <CrudList2
    title="Gardiennage"
    modelName="gardesituation"
    apiRouteName="gardeSituation"
    itemLabel="un gardiennage"
    idField="id_garde_situation"
    :columns="columns"
    :formComponent="GardeTroupeauForm2"
    :bgColor="'#d5642f'"
    :searchFields="searchFields"
  />
</template>
  
<script setup>
import GardeTroupeauForm2 from './GardeTroupeauForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "situation_nom", label: "Situation", sortable: true },
  { field: "berger_nom", label: "Nom berger", sortable: true },
  { field: "berger_prenom", label: "Prénom berger", sortable: true },
];

const searchFields = [
  'situation_nom',
  'berger_nom',
  'berger_prenom',
];

</script>