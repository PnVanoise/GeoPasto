<template>
  <CrudList2
    title="Evénements"
    modelName="evenement"
    apiRouteName="evenement"
    itemLabel="un événement"
    idField="id_evenement"
    :columns="columns"
    :formComponent="EventForm2"
    :bgColor="'#9b2423'"
  />
</template>

<script setup>
import EventForm2 from './EventForm2.vue'
import CrudList2 from './CrudList2.vue'

const columns = [
  { field: 'date_evenement', label: "Date évènement", sortable: true },
  { field: 'observateur', label: "Observateur", sortable: true },
  { field: 'date_observation', label: "Date observation", sortable: true },
  { field: 'source', label: "Source", sortable: true },
  { field: 'description', label: "Description", sortable: false },
]
</script>
