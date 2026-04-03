<template>
  <div>
    <div id="map-container">
      <div id="map"></div>
    </div>

    <button type="button" @click="toggleEditMode">
      {{ editingMode ? "Annuler" : "Éditer" }}
    </button>
    <button type="button" v-if="editingMode" @click="saveGeometry">Valider</button>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, toRaw, nextTick, onBeforeUnmount } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";

// --- Fonds de carte ---
const ignscan25 = L.tileLayer(
  "https://data.geopf.fr/private/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0" +
    "&FORMAT=image/jpeg&STYLE=normal&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR" +
    "&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&apikey=ign_scan_ws",
  {
    attribution: "IGN-F/Geoportail",
    maxZoom: 16,
    minZoom: 5,
  }
);

const osmplan = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
  maxZoom: 19,
});

const cadastr = L.tileLayer(
  "https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}",
  {
    attribution: "IGN-F",
    maxZoom: 19,
  }
);

const baseMaps = {
  "IGN Scan25": ignscan25,
  "OpenStreetMap": osmplan,
  "Parcelles cadastrales": cadastr,
};

// --- Props & emits ---
const props = defineProps({
  modelValue: {
    type: Object,
    required: false,
    default: () => null,
  },
  geometryType: {
    type: String,
    required: true,
    validator: (value) => ["Point", "LineString", "Polygon", "MultiPolygon"].includes(value),
  },
  referenceGeometry: {
    type: Object,
    required: false,
    default: () => null,
  },
  // Optional vector layers to display as overlays.
  // Each entry: { id: String, label: String, data: Object|String (GeoJSON or URL), style: Function|Object, visible: Boolean }
  vectorLayers: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);

// --- Variables globales ---
let map;
let drawControl;
let drawnItems;
let originalData;
const editingMode = ref(false);
const jsonCoordinates = ref("");

let referenceLayer;
let vectorLayerMap = {}; // id -> L.Layer
let overlaysControl = null;
let legendControl = null;

// --- Initialisation ---
onMounted(async () => {
  await nextTick();

  // Création de la carte avec un zoom max "global"
  map = L.map("map", {
    center: [45.3405, 6.7533],
    zoom: 10,
    zoomControl: false,
    layers: [osmplan],
    minZoom: 5,
    maxZoom: 19, // max général, adapté ensuite dynamiquement
  });

  // Contrôle des fonds de carte
  // create overlays container (will be populated with vector layers)
  const overlays = {};
  overlaysControl = L.control.layers(baseMaps, overlays).addTo(map);
  // update legend when overlays are toggled via the control
  map.on('overlayadd', updateLegend);
  map.on('overlayremove', updateLegend);

  // --- Synchronisation du zoom max selon le fond sélectionné ---
  map.on("baselayerchange", function (e) {
    if (e.name === "IGN Scan25") {
      map.setMaxZoom(16);
      if (map.getZoom() > 16) map.setZoom(16);
    } else {
      map.setMaxZoom(19);
    }
  });

  // --- Groupes de données ---
  originalData = new L.FeatureGroup().addTo(map);
  drawnItems = new L.FeatureGroup().addTo(map);

  if (props.referenceGeometry) {
    referenceLayer = new L.FeatureGroup();
    displayReferenceGeometry();
    referenceLayer.addTo(map);
  }

  // Add any provided vector layers as overlays
  updateVectorLayers();
  // add legend for vector layers
  updateLegend();

  const myIcon = L.icon({
    iconUrl: `/images/marqueur_rouge.png`,
    iconSize: [30, 42],
    iconAnchor: [15, 42],
    popupAnchor: [15, -42],
  });

  // --- Contrôle de dessin ---
  drawControl = new L.Control.Draw({
    edit: {
      featureGroup: drawnItems,
      edit: props.geometryType !== "Point" ? {} : false,
      remove: props.geometryType !== "Point" ? {} : false,
    },
    draw: {
      marker: props.geometryType === "Point" ? { icon: myIcon } : false,
      polygon: props.geometryType === "Polygon" || props.geometryType === "MultiPolygon",
      polyline: props.geometryType === "LineString",
      rectangle: false,
      circle: false,
      circlemarker: false,
    },
  });

  // --- Événements dessin ---
  map.on(L.Draw.Event.CREATED, (event) => {
    const layer = event.layer;
    if (props.geometryType === "Point") drawnItems.clearLayers();
    drawnItems.addLayer(layer);
    updateGeometry();
  });

  map.on(L.Draw.Event.EDITED, updateGeometry);
  map.on(L.Draw.Event.DELETED, updateGeometry);

  // --- Chargement des géométries existantes ---
  if (props.modelValue && props.modelValue.coordinates) {
    displayOriginalGeometry();
  }

  if (props.referenceGeometry) {
    displayReferenceGeometry();
  }
});

// Update vector overlays based on props.vectorLayers
function updateVectorLayers() {
  if (!map) return;

  // remove existing vector layers from map and control
  Object.values(vectorLayerMap).forEach((layer) => {
    try { map.removeLayer(layer); } catch (e) {}
    try { overlaysControl && overlaysControl.removeLayer && overlaysControl.removeLayer(layer); } catch (e) {}
  });
  vectorLayerMap = {};

  // helper to add a created layer into maps and control
  const addOverlay = (id, label, layer, visible) => {
    vectorLayerMap[id] = layer;
    overlaysControl && overlaysControl.addOverlay && overlaysControl.addOverlay(layer, label);
    if (visible) layer.addTo(map);
  };

  // create each layer (supports direct GeoJSON object or URL to fetch)
  props.vectorLayers.forEach((vl, idx) => {
    const id = vl.id || `vl_${idx}`;
    const label = vl.label || id;
    const style = vl.style || function() { return {}; };
    const visible = !!vl.visible;

    if (!vl.data) return;

    if (typeof vl.data === 'string') {
      // treat as URL
      fetch(vl.data)
        .then(res => res.json())
        .then((geojson) => {
          const layer = L.geoJSON(geojson, { style: vl.style, onEachFeature: vl.onEachFeature, pointToLayer: vl.pointToLayer || function(feature, latlng) {
            // default point rendering: try to derive from style(feature) or fallback to circleMarker
            try {
              const s = (typeof vl.style === 'function') ? vl.style(feature) : (vl.style || {});
              const color = (s && (s.fillColor || s.color)) || (vl.legend && (vl.legend.color || vl.legend.fillColor)) || '#1E90FF';
              const radius = (s && (s.radius || s.pointRadius)) || (vl.legend && vl.legend.radius) || 6;
              const legendFillOpacity = (vl.legend && typeof vl.legend.fillOpacity !== 'undefined') ? vl.legend.fillOpacity : undefined;
              const fillOpacity = (typeof legendFillOpacity !== 'undefined') ? legendFillOpacity : (s && typeof s.fillOpacity !== 'undefined' ? s.fillOpacity : (s && s.fill ? 1 : 0.85));
              const weight = (s && (s.weight || s.strokeWidth)) || (vl.legend && vl.legend.weight) || 1;
              return L.circleMarker(latlng, { radius: radius, color: color, fillColor: color, fillOpacity: fillOpacity, weight: weight });
            } catch (e) {
              return L.marker(latlng);
            }
          } });
          addOverlay(id, label, layer, visible);
        })
        .catch(err => console.error("Failed to load vector layer:", vl.data, err));
      } else {
      // assume GeoJSON object
      const layer = L.geoJSON(vl.data, { style: vl.style, onEachFeature: vl.onEachFeature, pointToLayer: vl.pointToLayer || function(feature, latlng) {
        try {
          const s = (typeof vl.style === 'function') ? vl.style(feature) : (vl.style || {});
          const color = (s && (s.fillColor || s.color)) || (vl.legend && (vl.legend.color || vl.legend.fillColor)) || '#1E90FF';
          const radius = (s && (s.radius || s.pointRadius)) || (vl.legend && vl.legend.radius) || 6;
          const legendFillOpacity = (vl.legend && typeof vl.legend.fillOpacity !== 'undefined') ? vl.legend.fillOpacity : undefined;
          const fillOpacity = (typeof legendFillOpacity !== 'undefined') ? legendFillOpacity : (s && typeof s.fillOpacity !== 'undefined' ? s.fillOpacity : (s && s.fill ? 1 : 0.85));
          const weight = (s && (s.weight || s.strokeWidth)) || (vl.legend && vl.legend.weight) || 1;
          return L.circleMarker(latlng, { radius: radius, color: color, fillColor: color, fillOpacity: fillOpacity, weight: weight });
        } catch (e) {
          return L.marker(latlng);
        }
      } });
      addOverlay(id, label, layer, visible);
    }
  });
  // update legend after overlays changed
  updateLegend();
}

// Build or update the legend control based on current vectorLayers
function updateLegend() {
  if (!map) return;

  // remove existing legend
  if (legendControl) {
    try { legendControl.remove(); } catch (e) {}
    legendControl = null;
  }

  const layers = props.vectorLayers || [];
  if (!layers || layers.length === 0) return;

  // only include layers that are currently added to the map
  const visibleLayers = layers.filter((vl, idx) => {
    const id = vl.id || `vl_${idx}`;
    const layer = vectorLayerMap[id];
    return layer && map.hasLayer(layer);
  });
  if (visibleLayers.length === 0) return;

  legendControl = L.control({ position: 'bottomright' });
  legendControl.onAdd = function () {
    const div = L.DomUtil.create('div', 'leaflet-legend');
    div.style.background = 'white';
    div.style.padding = '6px';
    div.style.borderRadius = '4px';
    div.style.boxShadow = '0 1px 4px rgba(0,0,0,0.2)';
    div.style.fontSize = '12px';
    div.innerHTML = '<strong>Légende</strong><br/>';

    visibleLayers.forEach((vl) => {
      const label = vl.legend?.label || vl.label || vl.id || '';

      // if explicit legend icon HTML provided, use it
      if (vl.legend && vl.legend.iconHtml) {
        const iconHtml = vl.legend.iconHtml;
        div.innerHTML += `<div style="margin-bottom:6px;">${iconHtml}<span style="margin-left:8px">${label}</span></div>`;
        return;
      }

      // fallback to swatch derived from legend or style (supports style function)
      let color = vl.legend?.color || '#3388ff';
      let fill = vl.legend?.fill ?? false;
      let strokeW = null;
      let radius = null;

      // prefer explicit geometry hints first (parent can declare geometryType or legend.symbol)
      const explicitPoint = (vl.geometryType === 'Point') || (vl.legend && vl.legend.symbol === 'point');
      const features = (vl.data && vl.data.features) || [];
      let hasPoint = false;
      let sampleFeature = null;
      if (!explicitPoint) {
        hasPoint = features.some((f) => f && f.geometry && f.geometry.type === 'Point');
        sampleFeature = hasPoint ? features.find((f) => f && f.geometry && f.geometry.type === 'Point') : (features[0] || null);
      } else {
        // if caller explicitly declared Point, prefer any Point feature as sample if present, otherwise first feature
        sampleFeature = features.find((f) => f && f.geometry && f.geometry.type === 'Point') || (features[0] || null);
        hasPoint = explicitPoint;
      }

      // Resolve a style object `s` whether vl.style is a function or an object
      let s = null;
      try {
        if (typeof vl.style === 'function') {
          s = vl.style(sampleFeature || {});
        } else if (vl.style && typeof vl.style === 'object') {
          s = vl.style;
        }
      } catch (e) {
        s = null;
      }

      if (s) {
        color = vl.legend?.color || s.color || s.fillColor || color;
        // prefer explicit vl.legend.fill when present, otherwise check style
        if (typeof vl.legend?.fill === 'boolean') fill = vl.legend.fill;
        else fill = !!s.fill || !!s.fillOpacity || fill;
        strokeW = s.weight || s.strokeWidth || null;
        radius = s.radius || s.pointRadius || null;
      }

      // Also allow legend hints to override
      if (vl.legend) {
        strokeW = strokeW || vl.legend.weight || null;
        radius = radius || vl.legend.radius || null;
      }

      // Decide swatch type: point, polygon, line, or filled polygon. Prefer explicit hints first.
      const geomType = sampleFeature && sampleFeature.geometry ? sampleFeature.geometry.type : null;
      const pointLike = explicitPoint || geomType === 'Point' || hasPoint || !!radius;
      const explicitPolygon = (vl.geometryType && (vl.geometryType.indexOf('Polygon') >= 0)) || (vl.legend && vl.legend.symbol === 'polygon');
      const polygonLike = explicitPolygon || geomType === 'Polygon' || geomType === 'MultiPolygon';

      console.log("Legend item:", label, "color:", color, "fill:", fill, "strokeW:", strokeW, "radius:", radius, "pointLike:", pointLike, "geomType:", geomType);

      let swatchHtml = '';
      try {
        if (pointLike) {
          const r = (radius && !isNaN(radius)) ? Math.max(3, Math.min(10, radius)) : 6;
          const weight = (vl.legend && vl.legend.weight) || (s && (s.weight || s.strokeWidth)) || 1;
          // SVG diameter should match marker visual: diameter + stroke, add tiny padding
          const svgDiameter = Math.ceil((r + weight) * 2 + 2);
          const cx = svgDiameter / 2;
          const cy = svgDiameter / 2;
          const legendFillOpacity = (vl.legend && typeof vl.legend.fillOpacity !== 'undefined') ? vl.legend.fillOpacity : undefined;
          const sFillOpacity = (s && typeof s.fillOpacity !== 'undefined') ? s.fillOpacity : undefined;
          const fillOpacity = (typeof legendFillOpacity !== 'undefined') ? legendFillOpacity : (typeof sFillOpacity !== 'undefined' ? sFillOpacity : (fill ? 1 : 0));
          const fillColor = (vl.legend && vl.legend.fillColor) || (s && (s.fillColor || s.color)) || color;
          swatchHtml = `<svg width="${svgDiameter}" height="${svgDiameter}" style="vertical-align:middle;margin-right:8px"><circle cx="${cx}" cy="${cy}" r="${r}" fill="${fillColor}" stroke="${color}" stroke-width="${weight}" fill-opacity="${fillOpacity}"/></svg>`;
        } else if (polygonLike) {
          // polygon swatch: show an outlined polygon (rect) using stroke and optional fill
          const sw = 20;
          const bg = fill ? color : 'transparent';
          const strokeWidth = (strokeW && Math.max(1, Math.min(6, strokeW))) || 1;
          swatchHtml = `<svg width="${sw}" height="14" style="vertical-align:middle;margin-right:8px"><rect x="0" y="0" width="${sw}" height="14" fill="${bg}" stroke="${color}" stroke-width="${strokeWidth}"/></svg>`;
        } else if (strokeW) {
          const stroke = color;
          const w = 34;
          const h = 14;
          const y = h / 2;
          const strokeWidth = Math.max(1, Math.min(6, strokeW));
          swatchHtml = `<svg width="${w}" height="${h}" style="vertical-align:middle;margin-right:8px"><line x1="2" y1="${y}" x2="${w-2}" y2="${y}" stroke="${stroke}" stroke-width="${strokeWidth}" stroke-linecap="round"/></svg>`;
        } else {
          const sw = 18;
          const bg = fill ? color : 'transparent';
          swatchHtml = `<svg width="${sw}" height="12" style="vertical-align:middle;margin-right:8px"><rect x="0" y="0" width="${sw}" height="12" fill="${bg}" stroke="${color}" stroke-width="1"/></svg>`;
        }
      } catch (e) {
        swatchHtml = `<i style="display:inline-block;width:18px;height:12px;margin-right:8px;border:1px solid ${color};background:${fill ? color : 'transparent'}"></i>`;
      }

      div.innerHTML += `<div style="margin-bottom:4px;">${swatchHtml}<span style="vertical-align:middle">${label}</span></div>`;
    });

    // prevent clicks on legend from propagating to the map
    L.DomEvent.disableClickPropagation(div);
    return div;
  };

  legendControl.addTo(map);
}

// --- Watchers ---
watch(
  () => props.modelValue,
  (newGeometry) => {
    
    if (!map || !drawnItems || !originalData) return; // ✅ évite l’erreur avant init

    if (newGeometry && newGeometry.coordinates) {
      displayOriginalGeometry();
    } else if (map) {
      map.setView([45.3405, 6.7533], 10);
    }
  },
  { immediate: true, deep: true }
);

watch(
  () => props.referenceGeometry,
  () => {
    if (props.referenceGeometry) displayReferenceGeometry();
  },
  { deep: true }
);

// Watch vectorLayers prop to update overlays dynamically
watch(
  () => props.vectorLayers,
  () => {
    updateVectorLayers();
  },
  { deep: true }
);

onBeforeUnmount(() => {
  // remove legend control
  if (legendControl) {
    try { legendControl.remove(); } catch (e) {}
    legendControl = null;
  }
  // remove overlays control
  if (overlaysControl) {
    try { overlaysControl.remove(); } catch (e) {}
    overlaysControl = null;
  }
  // remove vector layers
  Object.values(vectorLayerMap).forEach((layer) => {
    try { map.removeLayer(layer); } catch (e) {}
  });
  vectorLayerMap = {};
});

// --- Fonctions d'affichage ---
function displayReferenceGeometry() {
  
  // ✅ Sécurisation : si la carte n’est pas prête, on sort
  if (!map || !drawnItems || !originalData) return;

  if (!props.referenceGeometry) return;
  referenceLayer.clearLayers();

  const rawReference = toRaw(props.referenceGeometry);
  if (rawReference.type === "FeatureCollection") {
    rawReference.features.forEach((feature) => {
      if (
        feature.geometry &&
        (feature.geometry.type === "Polygon" || feature.geometry.type === "MultiPolygon")
      ) {
        const polygons =
          feature.geometry.type === "MultiPolygon"
            ? feature.geometry.coordinates.map((p) =>
                p.map((ring) => ring.map(([lng, lat]) => [lat, lng]))
              )
            : [
                feature.geometry.coordinates.map((ring) =>
                  ring.map(([lng, lat]) => [lat, lng])
                ),
              ];

        polygons.forEach((polygon) =>
          L.polygon(polygon, {
            color: "blue",
            weight: 1,
            opacity: 0.8,
            fill: false,
            dashArray: "5, 5",
          }).addTo(referenceLayer)
        );
      }
    });

    // const bounds = referenceLayer.getBounds();
    // if (bounds.isValid()) map.fitBounds(bounds);
  }
}

function displayOriginalGeometry() {
  if (!props.modelValue || !props.modelValue.coordinates) return;
  drawnItems.clearLayers();
  originalData.clearLayers();

  const rawModelValue = toRaw(props.modelValue);

  if (props.modelValue.type === "Point") {
    const [lng, lat] = props.modelValue.coordinates;
    const myIcon = L.icon({
      iconUrl: `/images/marqueur_bleu.png`,
      iconSize: [30, 42],
      iconAnchor: [15, 42],
      popupAnchor: [15, -42],
    });
    if (typeof lng === "number" && typeof lat === "number")
      L.marker([lat, lng], { icon: myIcon }).addTo(originalData);
  } else if (props.modelValue.type === "LineString") {
    // LineString: coordinates is an array of [lng, lat]
    const latlngs = props.modelValue.coordinates.map(([lng, lat]) => [lat, lng]);
    L.polyline(latlngs, {
      color: "red",
      weight: 2,
      opacity: 1,
    }).addTo(originalData);
    // also add to drawnItems for editing preview
    L.polyline(latlngs, {
      color: "#F16E60",
      weight: 3,
      opacity: 0.6,
    }).addTo(drawnItems);
  } else {
    const polygons =
      props.modelValue.type === "MultiPolygon"
        ? props.modelValue.coordinates.map((p) =>
            p.map((ring) => ring.map(([lng, lat]) => [lat, lng]))
          )
        : [
            props.modelValue.coordinates.map((ring) =>
              ring.map(([lng, lat]) => [lat, lng])
            ),
          ];

    polygons.forEach((polygon) => {
      L.polygon(polygon, {
        color: "red",
        weight: 2,
        opacity: 1,
        fill: false,
        dashArray: "10",
      }).addTo(originalData);

      L.polygon(polygon, {
        fillColor: "#F16E60",
        fillOpacity: 0.4,
        weight: 0,
      }).addTo(drawnItems);
    });
  }

  const bounds = drawnItems.getBounds();
  if (bounds.isValid()) map.fitBounds(bounds);
  else map.setView([45.3405, 6.7533], 10);
  map.invalidateSize();
}

// --- Mise à jour géométrie ---
function updateGeometry() {
  const targetType = (props.modelValue && props.modelValue.type) || props.geometryType;
  const geojson = { type: targetType, coordinates: [] };

  drawnItems.eachLayer((layer) => {
    const targetType = (props.modelValue && props.modelValue.type) || props.geometryType;
    if (targetType === "Point") {
      const ll = layer.getLatLng();
      geojson.coordinates = [ll.lng, ll.lat];
    } else if (layer instanceof L.Polygon) {
      const latlngs = layer.getLatLngs()[0].map((latlng) => [latlng.lng, latlng.lat]);
      if (targetType === "MultiPolygon") geojson.coordinates.push([latlngs]);
      else geojson.coordinates = [latlngs];
    } else if (layer instanceof L.Polyline) {
      // Polyline covers LineString (and Polygon too but polygon handled above)
      const latlngs = layer.getLatLngs().map((latlng) => [latlng.lng, latlng.lat]);
      geojson.coordinates = latlngs;
    }
  });

  jsonCoordinates.value = JSON.stringify(geojson.coordinates);
}

// --- Sauvegarde ---
function saveGeometry() {
  const targetType = (props.modelValue && props.modelValue.type) || props.geometryType;
  const geojson = { type: targetType, coordinates: [] };
  drawnItems.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      geojson.coordinates = [layer.getLatLng().lng, layer.getLatLng().lat];
    } else if (layer instanceof L.Polygon) {
      const latlngs = layer.getLatLngs()[0].map((latlng) => [latlng.lng, latlng.lat]);
      if (
        latlngs.length > 2 &&
        (latlngs[0][0] !== latlngs[latlngs.length - 1][0] ||
          latlngs[0][1] !== latlngs[latlngs.length - 1][1])
      )
        latlngs.push(latlngs[0]);

      if (targetType === "MultiPolygon") geojson.coordinates.push([latlngs]);
      else geojson.coordinates = [latlngs];
    } else if (layer instanceof L.Polyline) {
      const latlngs = layer.getLatLngs().map((latlng) => [latlng.lng, latlng.lat]);
      geojson.coordinates = latlngs;
    }
  });

  toggleEditMode();
  jsonCoordinates.value = JSON.stringify(geojson.coordinates);
  emit("update:modelValue", geojson);
}

// --- Mode édition ---
function toggleEditMode() {
  editingMode.value = !editingMode.value;
  if (editingMode.value) map.addControl(drawControl);
  else {
    map.removeControl(drawControl);
    displayOriginalGeometry();
  }
}
</script>

<style scoped>
#map {
  width: 100%;
  height: 400px;
}
</style>
