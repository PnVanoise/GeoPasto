<template>
  <CrudList2
    title="Espèces"
    modelName="espece"
    apiRouteName="espece"
    itemLabel="une espèce"
    idField="id_espece"
    :columns="columns"
    :formComponent="EspeceForm2"
    :bgColor="'#808080'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import EspeceForm2 from './EspeceForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

const searchFields = [
  'description',
];

</script>