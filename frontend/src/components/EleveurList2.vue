<template>
  <CrudList2
    title="Eleveurs"
    modelName="eleveur"
    apiRouteName="eleveur"
    itemLabel="un eleveur"
    idField="id_eleveur"
    :columns="columns"
    :formComponent="EleveurForm2"
    :bgColor="'#d5642f'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import EleveurForm2 from './EleveurForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "nom_eleveur", label: "Nom", sortable: true },
  { field: "prenom_eleveur", label: "Prénom", sortable: true },
];

const searchFields = [
  'nom_eleveur',
  'prenom_eleveur',
];

</script>