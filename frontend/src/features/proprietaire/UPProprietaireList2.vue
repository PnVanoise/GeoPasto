<template>
  <CrudList2
    title="UP / Propriétaires"
    modelName="upproprietaire"
    apiRouteName="proprietaireUP"
    itemLabel="un lien UP / Propriétaire"
    idField="id_proprietaire_up"
    :columns="columns"
    :formComponent="UPProprietaireForm2"
    :bgColor="'#f7ba0b'"
  />
</template>

<script setup>
import UPProprietaireForm2 from './UPProprietaireForm2.vue';
import CrudList2 from '../../components/crud/CrudList2.vue';

const columns = [
  { field: "up_nom", label: "Unité pastorale", sortable: true },
  { field: "proprietaire_nom", label: "Propriétaire", sortable: true },
];
</script>
