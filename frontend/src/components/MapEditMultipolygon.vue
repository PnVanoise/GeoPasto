<template>
  <h1>Composant : MapEditMultipolygon</h1>
  <h2 v-if="quartierUP">Nom du quartier : {{ quartierUP.properties.quartier_nom }}</h2>
  <button @click="toggleEditMode">{{ editingMode ? "Annuler" : "Éditer" }}</button>
  <button v-if="editingMode" @click="savePolygons(true)">Valider</button>
  <div id="map-container">
    <div id="map"></div>
  </div>
</template>

<script setup>
// Imports
import { onMounted, ref } from "vue";

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

const props = defineProps(["quartierUP"]);
// const props = defineProps({
//   modelValue: {
//     type: Object,
//     default: () => ({ type: "MultiPolygon", coordinates: [] }),
//   },
// });

const emit = defineEmits(["update:quartierUPgeom"]);

let map; // la carte
let drawControl; // contrôles d'édition
let drawnItems; // items dessinés (à sauvegarder)
const editingMode = ref(false); // indicateur encours d'édition ou non
let originalData = ref([]); // items au chargement du composant
const transformedPolygons = ref([]); // polygones transformés depuis geojson

onMounted(() => {
  // Création de la map
  map = L.map("map", {
    zoomControl: false,
    zoomAnimation: true,
    layers: [osmplan],
  });

  // Contrôle fonds de carte
  L.control.layers(baseMaps).addTo(map);

  // Données en entrée
  console.log("onmounted: ", props.quartierUP); //.properties.quartier_nom);
  //console.log("geometry.coordinates: ", props.modelValue);

  // items originaux - Symbo : contour
  originalData = new L.FeatureGroup().addTo(map);
  // items actuellement dessinés - Symbo : remplissage
  drawnItems = new L.FeatureGroup().addTo(map);
  // items de base

  // pour chacun des polygones du tableau transformé
  displayOriginalData();

  // on ajuste la carte aux éléments à afficher
  const bounds = originalData.getBounds();
  if (bounds.isValid()) {
    map.fitBounds(bounds);
  }

  drawControl = new L.Control.Draw({
    edit: {
      featureGroup: drawnItems,
      edit: {
        selectedPathOptions: {
          maintainColor: true,
          opacity: 0.3,
        },
      },
    },
    draw: {
      marker: false,
      polyline: false,
      rectangle: false,
      circle: false,
      circlemarker: false,
      polygon: {
        icon: new L.DivIcon({
          iconSize: new L.Point(7, 7),
          className: "leaflet-div-icon leaflet-editing-icon",
        }),
        shapeOptions: {
          color: "#F16E60",
          opacity: 0.3,
          fillOpacity: 0.5,
          weight: 5,
        },
        showArea: false,
      },
    },
  });

  map.on(L.Draw.Event.CREATED, function (event) {
    const layer = event.layer;
    // newPolygonLayers.value.push(layer);
    drawnItems.addLayer(layer);
    console.log("CREATED, drawnitems.length: ", drawnItems.getLayers().length);
    savePolygons();
  });

  map.on(L.Draw.Event.EDITED, function (event) {
    console.log("EDITED: ", event);

    savePolygons();
  });

  map.on(L.Draw.Event.DELETED, function (event) {
    savePolygons();
  });

  originalData.value = drawnItems.getLayers();
});

function displayOriginalData() {
  // L'objet quartierUP est au format geojson --> coords : [ lat, lng ]
  // On va générer des polygones --> coords : [ lng, lat ]
  // Conversion
  transformCoordinates();
  console.log("transformedPolygons: ", transformedPolygons.value);

  transformedPolygons.value.forEach((element) => {
    // Ajout des polygones sur la couche actuellement dessinée
    var polygon = L.polygon(element, {
      title: "test",
      fillColor: "#F16E60",
      fillOpacity: 0.5,
      weight: 2,
      color: "#F16E60",
      opacity: 0.5,
      fill: true,
    }).addTo(drawnItems);

    // Ajout des bordures sur la couche d'items originaux
    var polygonBorder = L.polygon(element, {
      color: "red",
      weight: "2",
      opacity: 0.7,
      fill: false,
      dashArray: "3",
    }).addTo(originalData);
  });
}

function resetToOriginal() {
  originalData.clearLayers();
  drawnItems.clearLayers();
  displayOriginalData();
}

function transformCoordinates() {
  if (props.quartierUP.geometry.type === "MultiPolygon") {
    transformedPolygons.value = props.quartierUP.geometry.coordinates.map((polygon) => {
      return polygon.map((ring) => {
        return ring.map((coordinate) => {
          return [coordinate[1], coordinate[0]]; // Invert lat/lng to lng/lat
        });
      });
    });
  }
}

function savePolygons(ttt = false) {
  const multipolygon = {
    type: "MultiPolygon",
    coordinates: [],
  };
  drawnItems.eachLayer((layer) => {
    if (layer instanceof L.Polygon) {
      const latLngs = layer.getLatLngs();
      const coordinates = latLngs.map((polygon) =>
        polygon.map((latlng) => [latlng.lng, latlng.lat])
      );
      multipolygon.coordinates.push(coordinates);
    }
  });

  console.log(JSON.stringify(multipolygon));

  if (ttt) {
    emit("update:quartierUPgeom", multipolygon);
    toggleEditMode();
    props.quartierUP.geometry.coordinates = multipolygon.coordinates;
    originalData.clearLayers();
    drawnItems.clearLayers();
    displayOriginalData();
  }
}

// bascule mode edition / affichage
function toggleEditMode() {
  editingMode.value = !editingMode.value;
  if (editingMode.value) {
    map.addControl(drawControl);
  } else {
    map.removeControl(drawControl);
    resetToOriginal();
  }
  console.log(`out editingmode: ${editingMode.value}`);
}
</script>

<style scoped>
#mapContainer {
  width: 80vw;
  height: 100%;
}
</style>
