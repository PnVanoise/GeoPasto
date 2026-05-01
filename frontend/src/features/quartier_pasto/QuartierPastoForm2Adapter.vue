<template>
  <QuartierPastoForm
    :initialForm="adaptedInitialForm"
    :isEdit="props.mode !== 'add'"
    :onSubmit="forwardSubmit"
  />
</template>

<script setup>
import { computed } from "vue";
import QuartierPastoForm from "./QuartierPastoForm.vue";

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: "view" },
  onSubmit: Function,
  onClose: Function,
});

const adaptedInitialForm = computed(() => {
  const src = props.initialForm || {};
  const srcProps = src.properties || {};
  const quartierId = src.id_quartier ?? src.id ?? srcProps.id_quartier ?? srcProps.id ?? null;
  const codeQuartier = src.code_quartier ?? srcProps.code_quartier ?? "";
  const nomQuartier = src.nom_quartier ?? srcProps.nom_quartier ?? "";
  const unitePastorale = src.unite_pastorale ?? srcProps.unite_pastorale ?? null;
  const situationId =
    src.situation_exploitation ??
    srcProps.situation_exploitation ??
    null;

  return {
    ...src,
    id: src.id ?? quartierId,
    id_quartier: quartierId,
    context_quartiers_geojson: src.context_quartiers_geojson ?? null,
    properties: {
      ...srcProps,
      id_quartier: quartierId,
      code_quartier: codeQuartier,
      nom_quartier: nomQuartier,
      unite_pastorale: unitePastorale,
      situation_exploitation: situationId,
    },
  };
});

const forwardSubmit = async (payload) => {
  if (!props.onSubmit) return;

  const data = JSON.parse(JSON.stringify(payload || {}));
  if (!data.properties) data.properties = {};

  const situationId =
    data.situation_exploitation ??
    data.properties.situation_exploitation ??
    props.initialForm?.situation_exploitation ??
    props.initialForm?.properties?.situation_exploitation ??
    null;

  if (situationId != null) {
    data.situation_exploitation = situationId;
    data.properties.situation_exploitation = situationId;
  }

  await props.onSubmit(data);
  props.onClose?.();
};
</script>
