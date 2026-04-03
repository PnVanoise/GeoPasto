<template>
  <CrudList2
    title="Bergers"
    modelName="berger"
    apiRouteName="berger"
    itemLabel="un berger"
    idField="id_berger"
    :columns="columns"
    :formComponent="BergerForm2"
    :bgColor="'#d4652f'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import BergerForm2 from './BergerForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "nom_berger", label: "Nom", sortable: true },
  { field: "prenom_berger", label: "Prénom", sortable: true },
];

const searchFields = [
  'nom_berger',
  'prenom_bergers',
];

</script>