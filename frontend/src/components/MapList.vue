<template>
  <h2>Où les trouve-t-on ?</h2>
  <!-- <MapPage></MapPage> -->
  <div id="map-container">
    <div id="map"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

// import axios from "axios";
import axios from "../services/axios";

import config from "../../config";
// import MapPage from "./ListMap/MapPage.vue";

const props = defineProps({
  // Define props here
  geoObjectName: String,
  style: Object,
  popupRoute: String,
  geomType: String,
  legendInnerHtml: String,
});

const map = ref(null);

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

const otmplan = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenTopoMap contributors",
});

const baseMaps = {
  "IGN Scan25": ignscan25,
  "Orthophoto IGN": ignorthophoto,
  OpenStreetMap: osmplan,
  OpenTopoMap: otmplan,
};

onMounted(async () => {
  map.value = L.map("map", {
    zoom: 10,
    zoomControl: false,
    zoomAnimation: false,
    layers: [osmplan],
  });

  // Gestionnaire de couches, outil zoom et échelle
  L.control.layers(baseMaps).addTo(map.value);
  L.control.zoom({ position: "topright" }).addTo(map.value);
  L.control.scale({ imperial: false, position: "bottomright" }).addTo(map.value);

  // map.value.on("baselayerchange", (event) => {
  //   event.layer.getPane().style.transition = "opacity 0.5s ease-in-out";
  //   event.layer.getPane().style.opacity = 0;
  //   setTimeout(() => {
  //     event.layer.getPane().style.opacity = 1;
  //   }, 2000);
  // });

  const geoData = await fetchGeoData(props.geoObjectName);
  let geoJsonLayer = null;
  if (props.geomType === "Point") {
    // console.log(geoData);

    geoJsonLayer = L.geoJSON(geoData, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, props.style);
      },
      onEachFeature: (feature, layer) => {
        // console.log('feat: ', feature);
        if (feature.properties && feature.id) {
          // console.log(feature.properties);
          layer.bindPopup(
            `<a href="${props.popupRoute}/edit/${feature.id}">${feature.id}</a>`
          );
        }
      },
    }).addTo(map.value);
  } else {
    geoJsonLayer = L.geoJSON(geoData, {
      style: props.style,
      onEachFeature: (feature, layer) => {
        // console.log("feat: ", feature);
        layer.on({
          mouseover: (e) => {
            const layer = e.target;
            layer.setStyle({
              weight: 5,
              color: "#666",
              dashArray: "",
              fillOpacity: 0.6,
            });

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
              layer.bringToFront();
            }

            infoctrl.update(layer.feature.properties);
          },
          mouseout: (e) => {
            geoJsonLayer.resetStyle(e.target);
            infoctrl.update();
          },
          click: (e) => {
            map.value.fitBounds(e.target.getBounds());
          },
        });
        if (feature.properties && feature.id) {
          // console.log(feature.properties.quartier_code);
          layer.bindPopup(`<a href="${props.popupRoute}/edit/${feature.id}">Détails</a>`);
        }
      },
    }).addTo(map.value);
  }

  const bounds = geoJsonLayer.getBounds();
  if (bounds.isValid()) {
    map.value.fitBounds(bounds);
  }

  /*Legend specific*/

  console.log(props.legendInnerHtml);
  var legend = L.control({ position: "bottomleft" });

  legend.onAdd = function (map) {
    var div = L.DomUtil.create("div", "legend");
    div.innerHTML += props.legendInnerHtml;

    return div;
  };

  legend.addTo(map.value);

  /* Expe zone info */
  var infoctrl = L.control({ position: "topleft" });

  infoctrl.onAdd = function (map) {
    var div = L.DomUtil.create("div", "legend");
    div.innerHTML += props.legendInnerHtml;

    return div;
  };

  infoctrl.onAdd = function () {
    this._div = L.DomUtil.create("div", "legend"); // créer une div avec la classe "legend"
    this.update();
    return this._div;
  };

  infoctrl.update = function (props) {
    this._div.innerHTML =
      "<h4>UP sélectionnée</h4>" +
      (props
        ? "<b>" + props.code_up + "</b><br />" + props.nom_up
        : "Survolez un polygone");
    console.log("infoctrl.update");
    console.log(props);
  };

  infoctrl.addTo(map.value);
});

// async function fetchGeoData(geoObjectName) {
//   try {
//     const response = await axios.get(`/api/${geoObjectName}`);
//     return response.data; // Axios renvoie directement les données dans la propriété `data`
//   } catch (error) {
//     // Gérer les erreurs et les afficher dans la console
//     console.error("Erreur lors de la récupération des données géospatiales :", error);

//     // Afficher un message d'erreur plus détaillé en fonction du type d'erreur
//     if (error.response) {
//       // Le serveur a répondu avec un code d'état autre que 2xx
//       console.error(`Erreur: ${error.response.status} - ${error.response.statusText}`);
//     } else if (error.request) {
//       // La requête a été faite mais aucune réponse n'a été reçue
//       console.error("Aucune réponse du serveur :", error.request);
//     } else {
//       // Quelque chose s'est mal passé lors de la configuration de la requête
//       console.error("Erreur dans la requête :", error.message);
//     }

//     return null;
//   }
// }

// import config from "../../config";

async function fetchGeoData(geoObjectName) {
  try {
    // Appel API avec Axios, en utilisant la configuration de base
    const response = await axios.get(`${config.API_BASE_URL}/api/${geoObjectName}`);

    // Pas besoin de vérifier manuellement response.ok avec Axios
    return response.data; // Axios renvoie directement les données dans response.data
  } catch (error) {
    // Gestion des erreurs
    if (error.response) {
      // L'erreur est liée à la réponse (comme 404, 500, etc.)
      console.error(
        `Erreur lors de la récupération des données géospatiales : ${error.response.statusText}`
      );
    } else if (error.request) {
      // L'erreur est liée à la requête (pas de réponse du serveur)
      console.error(
        "Erreur lors de la récupération des données géospatiales : aucune réponse reçue du serveur"
      );
    } else {
      // Autre erreur
      console.error(
        "Erreur lors de la récupération des données géospatiales :",
        error.message
      );
    }
    return null;
  }
}

// async function fetchGeoData(geoObjectName) {
//   try {
//     const response = await fetch(`${config.API_BASE_URL}/api/${geoObjectName}`);
//     if (!response.ok) {
//       throw new Error(`Erreur: ${response.statusText}`);
//     }
//     return response.json();
//   } catch (error) {
//     console.error("Erreur lors de la récupération des données géospatiales :", error);
//     return null;
//   }
// }
</script>

<style>
#map {
  width: 100%;
  max-height: 600px;
}

/*Legend specific*/
.legend {
  padding: 6px 8px;
  font: 14px Arial, Helvetica, sans-serif;
  background: white;
  /* box-shadow: 0 0 15px rgba(0, 0, 0, 0.2); */
  /* border-radius: 5px; */
  line-height: 24px;
  /* border: 1px solid black; */
  /* color: #555; */
}
.legend h4 {
  text-align: center;
  font-size: 16px;
  margin: 2px 12px 8px;
  /* color: #777; */
}

.legend span {
  position: relative;
  bottom: 3px;
}

.legend i {
  width: 18px;
  height: 18px;
  float: left;
  margin: 0 8px 0 0;
  /* opacity: 0.7; */
  border-style: 5px;
}

.legend i.icon {
  background-size: 18px;
  background-color: rgba(255, 255, 255, 1);
}

.legend .circle {
  border-radius: 50%;
  width: 18px;
  height: 18px;
  float: left;
  margin: 0 8px 0 0;
  /* opacity: 0.7; */
  border: 1px solid black;
}
</style>
