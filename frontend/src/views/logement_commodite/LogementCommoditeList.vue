<template>
  <CrudListPage
    title="Logements / Commodités"
    modelName="logementcommodite"
    apiRouteName="logementCommodite"
    itemLabel="un lien logement/commodité"
    idField="id_logement_commodite"
    :columns="columns"
    :bgColor="'#f7ba0b'"
    :searchFields="searchFields"
  />
</template>

<script setup>
import CrudListPage from '../../components/crud/CrudListPage.vue';

const columns = [
  { field: "logement_code",  label: "Logement",  sortable: true },
  { field: "commodite_desc", label: "Commodité", sortable: true },
  { field: "etat",           label: "État",      sortable: true },
  { field: "quantite",       label: "Quantité",  sortable: true },
];
const searchFields = ['logement_code', 'commodite_desc'];
</script>
