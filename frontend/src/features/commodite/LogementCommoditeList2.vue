<template>
  <CrudList2
    title="Logements / Commodités"
    modelName="logementcommodite"
    apiRouteName="logementCommodite"
    itemLabel="un lien logement/commodité"
    idField="id_logement_commodite"
    :columns="columns"
    :formComponent="LogementCommoditeForm2"
    :bgColor="'#f7ba0b'"
  />
</template>

<script setup>
import LogementCommoditeForm2 from './LogementCommoditeForm2.vue';
import CrudList2 from '../../components/crud/CrudList2.vue';

const columns = [
  { field: "logement_code", label: "Logement", sortable: true },
  { field: "commodite_desc", label: "Commodité", sortable: true },
  { field: "etat", label: "État", sortable: true },
  { field: "quantite", label: "Quantité", sortable: true },
];
</script>
