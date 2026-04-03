<template>
  <h2>This is an about page</h2>
  <p>Dessiner des polygones, génère un multipolygone</p>
  <button @click="goToHome">Go to homepage</button>
  <div id="map-container">
    <div id="map"></div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

import "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";

let map;

const router = useRouter();

const ignscan25 = L.tileLayer(
  "https://data.geopf.fr/private/wmts?" +
    "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0" +
    "&FORMAT=image/jpeg" +
    "&STYLE=normal" +
    "&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR" +
    "&TILEMATRIXSET=PM" +
    "&TILEMATRIX={z}" +
    "&TILEROW={y}" +
    "&TILECOL={x}" +
    "&apikey=ign_scan_ws",
  {
    attribution: "osm",
  }
);
const ignorthophoto = L.tileLayer(
  "https://data.geopf.fr/wmts?" +
    "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
    "&STYLE=normal" +
    "&TILEMATRIXSET=PM" +
    "&FORMAT=image/jpeg" +
    "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS" +
    "&TILEMATRIX={z}" +
    "&TILEROW={y}" +
    "&TILECOL={x}",
  {
    attribution: "ign",
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

function goToHome() {
  router.push(`/`);
}

onMounted(() => {
  try {
    map = L.map("map", {
      center: [45.4, 7.0],
      zoom: 11,
      // center: window.config.leaflet_centrage_initial,
      // zoom: window.config.leaflet_zoom_initial,
      zoomControl: false,
      zoomAnimation: false,
      layers: [osmplan],
    });

    // Gestionnaire de couches, outil zoom et échelle
    L.control.layers(baseMaps).addTo(map);
    L.control.zoom({ position: "topright" }).addTo(map);
    L.control.scale({ imperial: false, position: "bottomright" }).addTo(map);

    // Implémentation de leaflet-draw pour dessiner des polygones
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
      edit: {
        featureGroup: drawnItems,
      },
      draw: {
        polygon: true,
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false,
      },
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, (event) => {
      const layer = event.layer;
      drawnItems.addLayer(layer);
      savePolygons();
    });

    function savePolygons() {
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
    }
  } catch (error) {
    console.log("Erreur lors de l'initialisation de la carte : ", error);
  }
});
</script>

<style scoped>
#mapContainer {
  width: 80vw;
  height: 100vh;
}
</style>
