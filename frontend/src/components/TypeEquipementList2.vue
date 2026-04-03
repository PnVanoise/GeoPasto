<template>
  <CrudList2
    title="Types d'équipements"
    modelName="typeequipement"
    apiRouteName="typeEquipement"
    itemLabel="un type d'équipement"
    idField="id_type_equipement"
    :columns="columns"
    :formComponent="TypeEquipementForm2"
    :bgColor="'#808080'"
  />
</template>

<script setup>
import TypeEquipementForm2 from './TypeEquipementForm2.vue';
import CrudList2 from './CrudList2.vue';

const columns = [
  { field: "description", label: "Description", sortable: true },
  { field: "categorie", label: "Catégorie", sortable: true },
];
</script>
