<template>
  <CrudList2
    title="Logements"
    modelName="logement"
    apiRouteName="logement"
    :geojsonMode="true"
    itemLabel="un logement"
    idField="id"
    :columns="columns"
    :formComponent="LogementForm2"
    :bgColor="'#2e7d32'"
  />
</template>

<script setup>
import LogementForm2 from './LogementForm2.vue';
import CrudList2 from '../../components/crud/CrudList2.vue';

const columns = [
  { field: "logement_code", label: "Code", sortable: true },
  { field: "nom_logement", label: "Nom", sortable: true },
  { field: "unite_pastorale_detail.nom_up", label: "UP", sortable: true },
  { field: "statut", label: "Statut", sortable: true },
];
</script>
