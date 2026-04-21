<template>
  <div v-if="isLoading" class="w3-center">
    <img src="/spinner_2.gif" alt="Chargement événements" />
  </div>
  <div v-else class="main-container">
    <div class="main-item">
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
    </div>

    <div class="main-item">
      <h2>Carte des événements</h2>
      <div class="map-layer-controls">
        <label class="map-layer-toggle">
          <input type="checkbox" v-model="showUpLayer" />
          UP de référence
        </label>
        <label class="map-layer-toggle">
          <input type="checkbox" v-model="showEvenementsLayer" />
          Evénements
        </label>
      </div>

      <OpenLayersGeoJsonMap
        :layers="mapLayers"
        @open-popup-item="onMapPopupItem"
      />

      <div class="map-legend" aria-label="Légende de la carte">
        <div class="map-legend-item" v-if="showUpLayer">
          <span class="map-legend-swatch map-legend-swatch--up" aria-hidden="true"></span>
          Unités pastorales
        </div>
        <div class="map-legend-item" v-if="showEvenementsLayer">
          <span class="map-legend-swatch map-legend-swatch--evenement" aria-hidden="true"></span>
          Evénements ({{ mapEventCount }})
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import auth from "../../auth";
import config from "../../config";
import EventForm2 from "./EventForm2.vue";
import CrudList2 from "./CrudList2.vue";
import OpenLayersGeoJsonMap from "./ListMap/OpenLayersGeoJsonMap.vue";

const columns = [
  { field: "date_evenement", label: "Date évènement", sortable: true },
  { field: "observateur", label: "Observateur", sortable: true },
  { field: "date_observation", label: "Date observation", sortable: true },
  { field: "source", label: "Source", sortable: true },
  { field: "description", label: "Description", sortable: false },
];

const isLoading = ref(true);
const showUpLayer = ref(true);
const showEvenementsLayer = ref(true);
const unitePastoralesGeoData = ref(null);
const evenementsGeoData = ref(null);

const toFeatureCollection = (payload) => {
  if (!payload) return null;

  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
    return payload;
  }

  if (payload.type === "Feature") {
    return { type: "FeatureCollection", features: [payload] };
  }

  if (Array.isArray(payload)) {
    const features = payload
      .map((item) => {
        if (!item) return null;
        if (item.type === "Feature") return item;
        if (!item.geometry) return null;
        return {
          type: "Feature",
          id: item.id ?? item.properties?.id,
          geometry: item.geometry,
          properties: item.properties ?? item,
        };
      })
      .filter(Boolean);

    return { type: "FeatureCollection", features };
  }

  if (payload.geometry) {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          id: payload.id,
          geometry: payload.geometry,
          properties: payload.properties ?? payload,
        },
      ],
    };
  }

  return null;
};

const normalizeUpData = (payload) => {
  const featureCollection = toFeatureCollection(payload);
  if (!featureCollection) return null;

  return {
    type: "FeatureCollection",
    features: (featureCollection.features || [])
      .filter((feature) => feature?.geometry)
      .map((feature) => {
        const rawId = feature?.id ?? feature?.properties?.id_unite_pastorale ?? feature?.properties?.id;
        return {
          ...feature,
          id: rawId != null ? `up:${rawId}` : undefined,
          properties: {
            ...(feature?.properties || {}),
            id_unite_pastorale: rawId ?? feature?.properties?.id_unite_pastorale,
          },
        };
      }),
  };
};

const normalizeEvenementsData = (payload) => {
  const featureCollection = toFeatureCollection(payload);
  if (!featureCollection) return null;

  return {
    type: "FeatureCollection",
    features: (featureCollection.features || [])
      .filter((feature) => feature?.geometry)
      .map((feature) => {
        const rawId =
          feature?.id
          ?? feature?.properties?.event_id
          ?? feature?.properties?.id_evenement
          ?? feature?.properties?.id;
        return {
          ...feature,
          id: rawId != null ? `evenement:${rawId}` : undefined,
          properties: {
            ...(feature?.properties || {}),
            event_id: rawId ?? feature?.properties?.event_id,
            id_evenement: rawId ?? feature?.properties?.id_evenement,
          },
        };
      }),
  };
};

const mapLayers = computed(() => [
  {
    id: "up_outline",
    visible: showUpLayer.value,
    data: unitePastoralesGeoData.value,
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
      route: "",
    },
  },
  {
    id: "evenement",
    visible: showEvenementsLayer.value,
    data: evenementsGeoData.value,
    style: {
      strokeColor: "#dc2626",
      strokeWidth: 2,
      fillOpacity: 0.14,
      pointRadius: 6.5,
      pointShape: "triangle",
      pointStrokeColor: "#ffffff",
      pointStrokeWidth: 1,
      zIndex: 15,
    },
    popup: {
      typeLabel: "Événement",
      attribute: "description",
      idAttribute: "event_id",
      route: "/Evenement/edit",
      contentType: "eventCompact",
    },
  },
]);

const mapEventCount = computed(() => {
  const features = evenementsGeoData.value?.features || [];
  const eventIds = new Set(
    features
      .map((feature) => feature?.properties?.event_id ?? feature?.properties?.id_evenement)
      .filter((id) => id != null)
      .map((id) => String(id))
  );
  return eventIds.size;
});

const fetchUpReferences = async () => {
  const response = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/`);
  unitePastoralesGeoData.value = normalizeUpData(response.data);
};

const fetchEvenements = async () => {
  const response = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/evenement/`);
  evenementsGeoData.value = normalizeEvenementsData(response.data);
};

const refreshMapData = async () => {
  isLoading.value = true;
  try {
    await Promise.all([fetchUpReferences(), fetchEvenements()]);
  } catch (error) {
    console.error("Erreur lors du chargement de la carte des événements", error);
    unitePastoralesGeoData.value = null;
    evenementsGeoData.value = null;
  } finally {
    isLoading.value = false;
  }
};

const onMapPopupItem = (payload) => {
  const id = payload?.id;
  const action = payload?.action || "view";
  if (!id) return;

  const eventId = String(id).includes(":") ? String(id).split(":").pop() : String(id);
  if (!eventId) return;

  try {
    if (action === "edit") {
      window.dispatchEvent(new CustomEvent("crud-open-edit", {
        detail: {
          modelName: "evenement",
          id: eventId,
        },
      }));
      return;
    }

    window.dispatchEvent(new CustomEvent("crud-open-view", {
      detail: {
        modelName: "evenement",
        id: eventId,
      },
    }));
  } catch (error) {
    console.warn("Impossible d'ouvrir la fiche événement depuis la carte", error);
  }
};

const onGeoDataChanged = (event) => {
  const modelName = event?.detail?.modelName;
  if (!modelName || modelName === "evenement" || modelName === "unitepastorale") {
    refreshMapData();
  }
};

onMounted(() => {
  refreshMapData();
  window.addEventListener("geo-data-changed", onGeoDataChanged);
});

onBeforeUnmount(() => {
  window.removeEventListener("geo-data-changed", onGeoDataChanged);
});
</script>

<style scoped>
.main-container {
  display: grid;
  grid-template-columns: 50% 50%;
}

.main-item {
  padding: 20px;
  margin: 10px;
  text-align: center;
}

.map-layer-controls {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.map-layer-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
}

.map-legend {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 0.82rem;
}

.map-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.map-legend-swatch {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid rgba(15, 23, 42, 0.3);
  display: inline-block;
}

.map-legend-swatch--up {
  background: rgba(0, 128, 0, 0.3);
  border-color: #008000;
}

.map-legend-swatch--evenement {
  background: rgba(220, 38, 38, 0.18);
  border-color: #dc2626;
}

@media (max-width: 1100px) {
  .main-container {
    grid-template-columns: 1fr;
  }
}
</style>
