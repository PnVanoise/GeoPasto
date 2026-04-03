<template>
  <CrudList2
    title="Types d'événements"
    modelName="typeevenement"
    apiRouteName="typeEvenement"
    itemLabel="un type d'événement"
    idField="id_type_evenement"
    :columns="columns"
    :formComponent="TypeEvenementForm2"
    :bgColor="'#808080'"
  />
</template>

<script setup>
import TypeEvenementForm2 from './TypeEvenementForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
];

</script>
