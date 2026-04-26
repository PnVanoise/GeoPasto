<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
      <CrudListPage
        title="Unités pastorales"
        modelName="unitepastorale"
        apiRouteName="unitePastorale"
        :geojsonMode="true"
        itemLabel="une unité pastorale"
        idField="id"
        :columns="columns"
        :filters="upFilters"
        :bgColor="'#808080'"
      />
    </div>
    <div class="main-item">
      <h2>Où les trouve-t-on ?</h2>
      <div class="maps-stack">
        <section class="map-section">
          <OpenLayersGeoJsonMap
            :layers="openLayersLayers"
            @open-popup-item="onMapPopupItem"
          />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { usePermissions } from "@/composables/usePermissions";

import OpenLayersGeoJsonMap from "@/components/ListMap/OpenLayersGeoJsonMap.vue";
import CrudListPage from "@/components/CrudListPage.vue";

import config from "@/../config";
import auth from "@/../auth";

const columns = [
  { field: "nom_up",        label: "UP",    sortable: true },
  { field: "annee_version", label: "Année", sortable: true },
];

const upFilters = ref([
  {
    key: "annee_courante",
    type: "checkbox",
    label: `${new Date().getFullYear()}`,
    default: true,
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

const isLoading = ref(true);
const router = useRouter();
const { can } = usePermissions("unitepastorale");

// ── Données carte ─────────────────────────────────────────────────────────────
const unitepastorales = ref([]);

const layerStyle = {
  color: "#008000",
  weight: 2,
  fillOpacity: 0.3,
};

const openLayersLayers = computed(() => [
  {
    id: "unitepastorale",
    visible: true,
    data: unitepastorales.value,
    style: {
      strokeColor: layerStyle.color,
      strokeWidth: layerStyle.weight,
      fillOpacity: layerStyle.fillOpacity,
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

const fetchUnitePastorales = () => {
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      unitepastorales.value = response.data;
    })
    .catch((error) => {
      console.error("Erreur fetchUnitePastorales:", error);
    })
    .finally(() => {
      isLoading.value = false;
    });
};

// ── Popup carte → navigation (remplace les CustomEvents crud-open-*) ──────────
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

// ── Cycle de vie ──────────────────────────────────────────────────────────────
onMounted(fetchUnitePastorales);

const onGeoDataChanged = (e) => {
  try {
    const model = e?.detail?.modelName;
    if (!model || model === "unitepastorale") fetchUnitePastorales();
  } catch {
    fetchUnitePastorales();
  }
};

window.addEventListener("geo-data-changed", onGeoDataChanged);

onBeforeUnmount(() => {
  window.removeEventListener("geo-data-changed", onGeoDataChanged);
});
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
