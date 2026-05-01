<template>
  <!-- <h4>Composant : MapEditPoint</h4> -->
  <div v-if="modelValue">
    <div id="map-container">
      <div id="map"></div>
    </div>

    <button type="button" @click="toggleEditMode">
      {{ editingMode ? "Annuler" : "Éditer" }}
    </button>
    <button type="button" v-if="editingMode" @click="savePoint">Valider</button>
    <!-- <input v-model="jsonCoordinates" readonly /> -->
  </div>
  <div v-else>
    <p>Aucune donnée disponible.</p>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";

// Fonds de carte
const ignscan25 = L.tileLayer(
  "https://data.geopf.fr/private/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0" +
    "&FORMAT=image/jpeg&STYLE=normal&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR" +
    "&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&apikey=ign_scan_ws",
  {
    attribution: "IGN-F/Geoportail",
  }
);

const ignorthophoto = L.tileLayer(
  "https://data.geopf.fr/wmts?&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
    "&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=ORTHOIMAGERY.ORTHOPHOTOS" +
    "&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}",
  {
    attribution: "IGN-F/Geoportail",
  }
);

const osmplan = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
});

const baseMaps = {
  "IGN Scan25": ignscan25,
  "Orthophoto IGN": ignorthophoto,
  OpenStreetMap: osmplan,
};

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update:modelValue"]);

let map;
let drawControl;
let drawnItem;
let originalData;
const editingMode = ref(false);
const jsonCoordinates = ref("");

onMounted(() => {
  // Initialisation de la carte
  map = L.map("map", {
    zoomControl: false,
    layers: [osmplan],
  });

  // Contrôle fonds de carte
  L.control.layers(baseMaps).addTo(map);

  // Initialisation des groupes des polygones
  // items originaux - Symbo : contour
  originalData = new L.FeatureGroup().addTo(map);
  // items actuellement dessinés - Symbo : remplissage
  drawnItem = new L.FeatureGroup().addTo(map);

  // Initialisation du controle de dessin
  drawControl = new L.Control.Draw({
    edit: {
      featureGroup: drawnItem,
    },
    draw: {
      marker: {
        shapeOptions: {
          color: "#F16E60",
        },
      },
      polyline: false,
      rectangle: false,
      circle: false,
      circlemarker: false,
      polygon: false,
    },
  });

  // Centrer la carte sur les polygones
  const bounds = drawnItem.getBounds();
  if (bounds.isValid()) {
    map.fitBounds(bounds);
  }

  // Evenements
  map.on(L.Draw.Event.CREATED, function (event) {
    const layer = event.layer;
    drawnItem.addLayer(layer);
    updatePoint();
  });

  map.on(L.Draw.Event.EDITED, updatePoint);
  map.on(L.Draw.Event.DELETED, updatePoint);

  console.log("MapEditPoint - props.modelValue", props.modelValue);

  // Chargement du point
  if (props.modelValue && props.modelValue.coordinates) {
    displayOriginalData();
  }
});

watch(
  () => props.modelValue,
  () => {
    displayOriginalData();
  },
  { deep: true, immediate: true }
);

function displayOriginalData() {
  if (drawnItem && originalData) {
    drawnItem.clearLayers();
    originalData.clearLayers();
    // console.log("displayOriginalData - props.modelValue", props.modelValue);

    if (props.modelValue && props.modelValue.type === "Point") {
      if (props.modelValue.coordinates.length > 0) {
        const point = props.modelValue.coordinates;
        console.log("displayOriginaldata - Point", point);

        const icon = L.divIcon({
          className: "custom-div-icon",
          html:
            "<div style='background-color:#A02128;' class='marker-pin'></div><i class='fa fa-home awesome'>",
          iconSize: [30, 42],
          iconAnchor: [15, 42],
        });

        const marker = L.marker([point[1], point[0]], {
          icon: icon,
        }).addTo(map);

        map.setView([point[1], point[0]], 10);
      } else {
        map.setView([45.3405, 6.7533], 10);
      }
    }
  }
}

function updatePoint() {
  const geojson = {
    type: "Point",
    coordinates: [],
  };

  drawnItem.eachLayer((layer) => {
    if (layer instanceof L.Polygon) {
      const latlngs = layer.getLatLngs()[0].map((latlng) => [latlng.lng, latlng.lat]);
      geojson.coordinates.push([latlngs]);
    }
  });

  jsonCoordinates.value = JSON.stringify(geojson.coordinates);
}

function savePoint() {
  const geojson = {
    type: "Point",
    coordinates: [],
  };

  drawnItem.eachLayer((layer) => {
    if (layer instanceof L.Polygon) {
      const latlngs = layer.getLatLngs()[0].map((latlng) => [latlng.lng, latlng.lat]);

      // Fermer l'anneau si nécessaire
      if (
        latlngs.length > 2 &&
        (latlngs[0][0] !== latlngs[latlngs.length - 1][0] ||
          latlngs[0][1] !== latlngs[latlngs.length - 1][1])
      ) {
        latlngs.push(latlngs[0]);
      }
      geojson.coordinates.push([latlngs]);
    }
  });

  jsonCoordinates.value = JSON.stringify(geojson.coordinates);
  // emit("update:modelValue", geojson);
}

function toggleEditMode() {
  editingMode.value = !editingMode.value;
  if (editingMode.value) {
    map.addControl(drawControl);
  } else {
    map.removeControl(drawControl);
    displayOriginalData();
  }
}
</script>

<style scoped>
#map {
  width: 100%;
  height: 400px;
}

.marker-pin {
  width: 30px;
  height: 30px;
  border-radius: 50% 50% 50% 0;
  background: #a02128;
  position: absolute;
  transform: rotate(-45deg);
  left: 50%;
  top: 50%;
  margin: -15px 0 0 -15px;
}

.marker-pin::after {
  content: "";
  width: 24px;
  height: 24px;
  margin: 3px 0 0 3px;
  background: #fff;
  position: absolute;
  border-radius: 50%;
}

.custom-div-icon i {
  position: absolute;
  width: 22px;
  font-size: 22px;
  left: 0;
  right: 0;
  margin: 10px auto;
  text-align: center;
}

.custom-div-icon i.awesome {
  margin: 12px auto;
  font-size: 17px;
}
</style>
