<template>
  <div class="main-container">
    <div class="main-item">
      <CrudListPage
        ref="listRef"
        title="Unités pastorales"
        modelName="unitepastorale"
        apiRouteName="unitePastorale"
        :geojsonMode="true"
        itemLabel="une unité pastorale"
        idField="id"
        :columns="columns"
        :filters="upFilters"
        :bgColor="'#808080'"
        :selectedId="selectedId"
        @update:filtered-items="onFilteredItems"
        @row-hover="onRowHover"
        @row-click="onRowClick"
      />
    </div>
    <div class="main-item">
      <h2>Où les trouve-t-on ?</h2>
      <div class="maps-stack">
        <section class="map-section">
          <OpenLayersGeoJsonMap
            ref="mapRef"
            :layers="openLayersLayers"
            :highlightedId="hoveredId"
            :selectedId="selectedId"
            @open-popup-item="onMapPopupItem"
            @feature-click="onMapFeatureClick"
          />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, toRaw, markRaw } from "vue";
import { useRouter } from "vue-router";
import { usePermissions } from "@/composables/usePermissions";

import OpenLayersGeoJsonMap from "../../components/map/OpenLayersGeoJsonMap.vue";
import CrudListPage from "../../components/crud/CrudListPage.vue";

const columns = [
  { field: "nom_up",        label: "UP",    sortable: true },
  { field: "annee_version", label: "Année", sortable: true },
];

const upFilters = ref([
  {
    key: "annee_courante",
    type: "checkbox",
    label: `${new Date().getFullYear()}`,
    default: false,
    apply: (rows, value) =>
      !value ? rows : rows.filter((r) => r.annee_version === new Date().getFullYear()),
  },
  {
    key: "version_active",
    type: "checkbox",
    label: "Act ?",
    default: false,
    apply: (rows, value) => (!value ? rows : rows.filter((r) => r.version_active === value)),
  },
]);

const router = useRouter();
const { can } = usePermissions("unitepastorale");

// ── Données carte (alimentées par CrudListPage) ───────────────────────────────
const listRef = ref(null);
const mapRef = ref(null);
const mapItems = ref([]);
const hoveredId = ref(null);
const selectedId = ref(null);

const mapFeatureCollection = computed(() => {
  const features = mapItems.value
    .filter(item => item.geometry)
    .map(item => {
      const { geometry, id, ...properties } = toRaw(item);
      return { type: "Feature", id, geometry: toRaw(geometry), properties };
    });
  return markRaw({ type: "FeatureCollection", features });
});

const openLayersLayers = computed(() => [
  {
    id: "unitepastorale",
    visible: true,
    data: mapFeatureCollection.value,
    style: {
      strokeColor: "#008000",
      strokeWidth: 2,
      fillOpacity: 0.3,
      zIndex: 10,
    },
    popup: {
      typeLabel: "UP",
      attribute: "nom_up",
      idAttribute: "id_unite_pastorale",
      route: "/unite-pastorale/edit",
      viewRoute: "/unite-pastorale/view",
      canEdit: can("change"),
    },
  },
]);

const onFilteredItems = (items) => { mapItems.value = items; };
const onMapFeatureClick = ({ id }) => {
  selectedId.value = selectedId.value === id ? null : id;
  if (selectedId.value != null) listRef.value?.scrollToId(id);
};
const onRowHover = (item) => { hoveredId.value = item?.id ?? null; };
const onRowClick = (item) => {
  const id = item?.id ?? null;
  selectedId.value = selectedId.value === id ? null : id;
  if (selectedId.value != null) {
    mapRef.value?.zoomToId(selectedId.value);
    mapRef.value?.showPopupForId(selectedId.value);
  }
};

// ── Popup carte → navigation ──────────────────────────────────────────────────
const onMapPopupItem = (payload) => {
  const id     = payload?.id;
  const action = payload?.action || "view";
  if (!id) return;

  if (action === "edit" && can("change")) {
    router.push({ name: "unitepastorale-edit", params: { id } });
  } else {
    router.push({ name: "unitepastorale-view", params: { id } });
  }
};
</script>

<style scoped>
.main-container {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  width: 100%;
}

.main-item {
  padding: 20px;
  text-align: center;
  min-width: 0;
}

.maps-stack {
  display: grid;
  gap: 24px;
}

@media (max-width: 1024px) {
  .main-container {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .main-item {
    padding: 10px;
    margin: 0;
  }

  .map-section {
    min-height: 400px;
    margin-top: 20px;
  }
}

@media (max-width: 600px) {
  .main-item {
    padding: 5px;
  }

  h2 {
    font-size: 1.2rem;
  }
}
</style>
