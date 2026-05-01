<template>
  <div></div>
</template>

<script setup>
import { onMounted, watch, ref, onBeforeUnmount } from "vue";
import L from "leaflet";

// Définir les props
const props = defineProps({
  map: Object,
  geoData: Object,
  mPolygonStyle: Object,
  popupRoute: String,
  iconFile: String, // Prop pour le fichier PNG du marqueur
  iconHighlightFile: String, // Prop pour le fichier PNG du marqueur en surbrillance
  objectLib: String, // Prop pour le libellé de l'objet géographique
  popupAttribute: String, // Prop pour l'attribut à afficher dans le popup
});

// Référence pour la couche GeoJSON et la légende
const geoLayer = ref(null);
const legend = ref(null);

// Fonction pour ajouter la couche GeoJSON à la carte
const addGeoJsonLayer = () => {
  if (props.map && props.geoData) {
    // remove any previously created geojson layers created by this component
    try {
      props.map.eachLayer((l) => {
        if (l && l.__isGeoJsonLayer === true) {
          try { props.map.removeLayer(l); } catch (e) {}
        }
      });
    } catch (e) {
      // ignore
    }

    // Créer et ajouter la nouvelle couche GeoJSON
    geoLayer.value = L.geoJSON(props.geoData, {
      style: (feature) => {
        if (
          feature.geometry.type === "MultiPolygon" ||
          feature.geometry.type === "Polygon"
        ) {
          return props.mPolygonStyle; // Appliquer le style passé en prop pour les multipolygones
        }
      },
      pointToLayer: (feature, latlng) => {
        const icon = L.icon({
          iconUrl: `/images/${props.iconFile}`, // Utilisation de l'image du dossier public
          iconSize: [30, 42],
          iconAnchor: [15, 42],
          popupAnchor: [15, -42],
        });

        return L.marker(latlng, { icon: icon });
      },
      onEachFeature: (feature, layer) => {
        console.log("feature.geometry.type:", feature.geometry.type);
        if (layer instanceof L.Marker) {
          console.log("layer POINT");
          layer.on({
            mouseover: highlightMarker,
            mouseout: resetMarker,
            click: (e) => {
              props.map.setView(e.latlng, 15);
            },
          });
        } else {
          layer.on({
            click: (e) => {
              if (feature.geometry.type === "Point") {
                props.map.setView(e.latlng, 15);
              } else {
                props.map.fitBounds(e.target.getBounds());
              }
            },
            mouseover: highlightPolygon,
            mouseout: resetHighlight,
          });
        }
        // Ajouter un popup interactif avec un lien
        // layer.bindPopup(`<a href="${props.popupRoute}/${feature.id}">${feature.id}</a>`, {
        //   className: "custom-popup", // Classe CSS pour personnaliser
        //   closeButton: false, // Pour enlever le bouton de fermeture (optionnel)
        //   offset: [0, 60], // Décale légèrement le popup vers le bas
        // });
        layer.bindPopup(
          `<a href="${props.popupRoute}/${feature.id}">${
            feature.properties[props.popupAttribute]
          }</a>`
        );
      },
    }).addTo(props.map);
    // mark the created layer so we can remove it reliably later
    try { geoLayer.value.__isGeoJsonLayer = true; } catch (e) {}


    const bounds = geoLayer.value.getBounds();
    if (bounds.isValid()) {
      props.map.fitBounds(geoLayer.value.getBounds());
    } else {
      // const latlng = originalData.getLayers()[0].getLatLng();
      // map.setView(latlng, 15);
      props.map.setView([45.3405, 6.7533], 10);
    }

    // Ajuster la vue de la carte pour englober les données GeoJSON
    // props.map.fitBounds(geoLayer.value.getBounds());

    // Mettre à jour la légende
    addLegend();
  }
};

onBeforeUnmount(() => {
  try {
    if (geoLayer.value && props.map) {
      try { props.map.removeLayer(geoLayer.value); } catch (e) {}
      geoLayer.value = null;
    }
    if (legend.value && props.map) {
      try { props.map.removeControl(legend.value); } catch (e) {}
      legend.value = null;
    }
  } catch (e) {}
});

// Fonction pour ajouter la légende
const addLegend = () => {
  if (!props.map) return;

  // Supprimer la légende précédente si elle existe
  if (legend.value) {
    props.map.removeControl(legend.value);
  }

  // Créer et ajouter la nouvelle légende
  legend.value = L.control({ position: "bottomleft" });

  legend.value.onAdd = function () {
    const div = L.DomUtil.create("div", "info legend");

    // Ajouter une entrée pour le PNG de l'icône
    if (props.iconFile) {
      div.innerHTML = `
        <div>
          <img src="/images/${props.iconFile}" style="width: 30px; height: 42px;">
          <span>${props.objectLib}</span>
        </div>
      `;
    }

    // Ajouter une entrée pour les multipolygones
    if (props.mPolygonStyle) {
      div.innerHTML += `
        <div>
          <span class="multiPolygon-symbol"
            style="
            background-color: rgba(
            ${hexToRgb(props.mPolygonStyle.color)},
            ${props.mPolygonStyle.fillOpacity || 0.5}
            );
            border: ${props.mPolygonStyle.weight || 1}px solid ${
        props.mPolygonStyle.color
      };
            display: inline-block;
            width: 30px;
            height: 15px;"></span>
          <span>${props.objectLib}</span>
        </div>
      `;
    }

    return div;
  };

  // Ajouter la légende à la carte
  legend.value.addTo(props.map);
};

// Watch pour surveiller les changements dans la carte et les données GeoJSON
watch(
  () => [props.map, props.geoData],
  ([newMap, newGeoData]) => {
    if (newMap && newGeoData) {
      addGeoJsonLayer();
    }
  }
);

// Fonction utilitaire pour convertir la couleur hexadécimale en RGB
function hexToRgb(hex) {
  hex = hex.replace(/^#/, "");

  if (hex.length === 3) {
    hex = hex
      .split("")
      .map((char) => char + char)
      .join("");
  }

  const bigint = parseInt(hex, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `${r}, ${g}, ${b}`;
}

// Initialiser lorsque le composant est monté
onMounted(() => {
  if (props.map && props.geoData) {
    addGeoJsonLayer();
  }
});

// Mise en évidence du polygone
const highlightPolygon = (e) => {
  // console.log("highlight");
  const layer = e.target;
  layer.setStyle({
    weight: 4,
    dashArray: "5, 5",
    dashOffset: "5",
  });
};

// Fonction pour réinitialiser le style du polygone
const resetHighlight = (e) => {
  // console.log("reset");
  const layer = e.target;
  geoLayer.value.resetStyle(layer);
};

// Affiche le marqueur au survol
const highlightMarker = (e) => {
  const marker = e.target;
  marker.setIcon(
    L.icon({
      iconUrl: `/images/${props.iconHighlightFile}`, // Utilisation de l'image du dossier public
      iconSize: [30, 42],
      iconAnchor: [15, 42],
      popupAnchor: [0, -42],
    })
  );
};

// Fonction pour réinitialiser l'icône du marqueur
const resetMarker = (e) => {
  const marker = e.target;
  marker.setIcon(
    L.icon({
      iconUrl: `/images/${props.iconFile}`, // Utilisation de l'image du dossier public
      iconSize: [30, 42],
      iconAnchor: [15, 42],
    })
  );
};
</script>

<style>
/* Styles pour la légende */
.info.legend {
  padding: 10px;
}

.info.legend img {
  display: inline-block;
  width: 30px;
  height: 42px;
  margin-right: 10px;
}

.info.legend div {
  display: flex;
  align-items: center;
  margin-bottom: 8px; /* Espacement entre les lignes de légende */
}

.info.legend .multiPolygon-symbol {
  display: inline-block;
  width: 30px;
  height: 15px;
  margin-right: 10px; /* Espacement entre le symbole et le texte */
}
</style>
