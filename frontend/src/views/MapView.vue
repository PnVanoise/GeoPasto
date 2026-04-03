<template>
  <h2>MapView</h2>
  <button @click="goToHome">Home</button>
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

import config from "../../config";

const router = useRouter();

// On met en place la carte, son fond, ses contrôles
let map;
let datajson;

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

async function fetchGeoJSON() {
  try {
    console.log(config.API_BASE_URL);
    const response = await fetch(`${config.API_BASE_URL}/api/quartierUP/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const datajson = await response.json();
    return datajson;
  } catch (error) {
    console.error("Error fetching GeoJSON:", error);
    return null;
  }
}

function goToAlpage(id) {
  router.push(`/alpageview/${id}`);
}

function onEachFeature(feature, layer) {
  if (feature.properties && feature.properties.quartier_nom) {
    const link = document.createElement("a");
    link.href = "#";
    link.innerHTML = `${feature.properties.id} - ${feature.properties.up_nom_1} - ${feature.properties.quartier_nom}`;
    link.onclick = () => {
      goToAlpage(feature.id);
    };
    layer.bindPopup(link);
  }
}

function style(feature) {
  return {
    fillColor: getColor(feature.id), // Remplacez someProperty par la propriété pertinente
    weight: 2,
    // opacity: 1,
    color: getColor(feature.id),
    dashArray: "3",
    fillOpacity: 0.3,
  };
}

function getColor(intval) {
  return intval % 2 === 0 ? "orange" : "blue";
}

onMounted(async () => {
  try {
    map = L.map("map", {
      center: [45.3874, 6.7949],
      zoom: 10,
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

    datajson = await fetchGeoJSON();

    if (datajson) {
      L.geoJSON(datajson, {
        style: style,
        onEachFeature: onEachFeature,
      }).addTo(map);
    }
  } catch (error) {
    console.log("Erreur lors de l'initialisation de la carte : ", error);
  }
});
</script>

<style>
#map {
  width: 100%;
  height: 600px;
}
</style>
