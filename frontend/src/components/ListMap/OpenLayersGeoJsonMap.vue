<template>
  <div class="ol-map-wrapper">
    <div ref="mapElement" class="ol-map"></div>
    <div ref="popupElement" class="ol-popup">
      <a href="#" class="ol-popup-closer" @click.prevent="closePopup">×</a>
      <div ref="popupContent" class="ol-popup-content"></div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import "ol/ol.css";

import GeoJSON from "ol/format/GeoJSON";
import Map from "ol/Map";
import View from "ol/View";
import { defaults as defaultControls, ScaleLine } from "ol/control";
import { Fill, Stroke, Style, Circle as CircleStyle } from "ol/style";
import Overlay from "ol/Overlay";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import OSM from "ol/source/OSM";
import VectorSource from "ol/source/Vector";

const emit = defineEmits(["open-popup-item"]);

const props = defineProps({
  geoData: {
    type: [Object, Array],
    default: null,
  },
  mPolygonStyle: {
    type: Object,
    default: () => ({
      color: "#008000",
      weight: 2,
      fillOpacity: 0.3,
    }),
  },
  popupRoute: {
    type: String,
    default: "",
  },
  popupAttribute: {
    type: String,
    default: "id",
  },
  fallbackCenter: {
    type: Array,
    default: () => [6.7533, 45.3405],
  },
  fallbackZoom: {
    type: Number,
    default: 10,
  },
});

const mapElement = ref(null);
const popupElement = ref(null);
const popupContent = ref(null);

let map = null;
let vectorLayer = null;
let popupOverlay = null;

const buildStyle = () => {
  const strokeColor = props.mPolygonStyle?.color || "#008000";
  const strokeWidth = props.mPolygonStyle?.weight || 2;
  const fillOpacity = props.mPolygonStyle?.fillOpacity ?? 0.3;

  return new Style({
    stroke: new Stroke({
      color: strokeColor,
      width: strokeWidth,
    }),
    fill: new Fill({
      color: hexToRgba(strokeColor, fillOpacity),
    }),
    image: new CircleStyle({
      radius: 6,
      fill: new Fill({ color: strokeColor }),
      stroke: new Stroke({ color: "#ffffff", width: 2 }),
    }),
  });
};

const normalizeGeoData = (input) => {
  if (!input) return null;
  if (input.type === "FeatureCollection" || input.type === "Feature") return input;
  if (Array.isArray(input)) {
    return {
      type: "FeatureCollection",
      features: input,
    };
  }
  return null;
};

const updateVectorLayer = () => {
  if (!map || !vectorLayer) return;

  const normalized = normalizeGeoData(props.geoData);
  const source = vectorLayer.getSource();
  source.clear();

  if (!normalized) {
    map.getView().setCenter([0, 0]);
    map.getView().setZoom(2);
    return;
  }

  const features = new GeoJSON().readFeatures(normalized, {
    featureProjection: "EPSG:3857",
  });

  source.addFeatures(features);

  const extent = source.getExtent();
  if (extent && extent.every((v) => Number.isFinite(v))) {
    map.getView().fit(extent, {
      duration: 250,
      padding: [30, 30, 30, 30],
      maxZoom: 16,
    });
  }
};

const openPopupForFeature = (feature, coordinate) => {
  if (!popupOverlay || !popupContent.value) return;

  const properties = feature.getProperties() || {};
  const id = feature.getId() ?? properties.id;
  const label = properties[props.popupAttribute] || id || "Détails";

  if (!id) {
    popupContent.value.innerHTML = `<strong>${escapeHtml(String(label))}</strong>`;
  } else {
    const href = `${props.popupRoute}/${id}`;
    popupContent.value.innerHTML = `<a href="${href}" data-feature-id="${escapeHtml(String(id))}" data-feature-label="${escapeHtml(String(label))}">${escapeHtml(String(label))}</a>`;
  }

  popupOverlay.setPosition(coordinate);
};

const onPopupContentClick = (event) => {
  const link = event.target?.closest?.("a[data-feature-id]");
  if (!link) return;

  event.preventDefault();
  const id = link.getAttribute("data-feature-id");
  const label = link.getAttribute("data-feature-label") || "";
  if (!id) return;

  emit("open-popup-item", { id, label });
};

const closePopup = () => {
  if (popupOverlay) popupOverlay.setPosition(undefined);
};

const initMap = () => {
  vectorLayer = new VectorLayer({
    source: new VectorSource(),
    style: buildStyle(),
  });

  popupOverlay = new Overlay({
    element: popupElement.value,
    autoPan: {
      animation: {
        duration: 200,
      },
    },
  });

  map = new Map({
    target: mapElement.value,
    layers: [
      new TileLayer({
        source: new OSM(),
      }),
      vectorLayer,
    ],
    overlays: [popupOverlay],
    controls: defaultControls().extend([new ScaleLine()]),
    view: new View({
      center: [0, 0],
      zoom: 2,
    }),
  });

  map.on("singleclick", (event) => {
    const source = vectorLayer?.getSource();
    const pickedFeature = source?.getFeaturesAtCoordinate(event.coordinate)?.[0] || null;

    if (pickedFeature) {
      openPopupForFeature(pickedFeature, event.coordinate);
    } else {
      closePopup();
    }
  });

  updateVectorLayer();
};

watch(
  () => props.geoData,
  () => {
    updateVectorLayer();
  },
  { deep: true }
);

watch(
  () => props.mPolygonStyle,
  () => {
    if (vectorLayer) {
      vectorLayer.setStyle(buildStyle());
    }
  },
  { deep: true }
);

onMounted(() => {
  initMap();
  popupContent.value?.addEventListener("click", onPopupContentClick);
});

onBeforeUnmount(() => {
  popupContent.value?.removeEventListener("click", onPopupContentClick);
  if (map) {
    map.setTarget(undefined);
    map = null;
  }
  vectorLayer = null;
  popupOverlay = null;
});

function hexToRgba(hex, alpha) {
  const cleaned = String(hex || "").replace(/^#/, "");
  const validHex = cleaned.length === 3
    ? cleaned
        .split("")
        .map((ch) => ch + ch)
        .join("")
    : cleaned;

  const numeric = Number.parseInt(validHex, 16);
  const r = (numeric >> 16) & 255;
  const g = (numeric >> 8) & 255;
  const b = numeric & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
</script>

<style scoped>
.ol-map-wrapper {
  position: relative;
}

.ol-map {
  width: 100%;
  height: 600px;
}

.ol-popup {
  position: absolute;
  background-color: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #cccccc;
  min-width: 220px;
  transform: translate(-50%, -100%);
}

.ol-popup-closer {
  position: absolute;
  top: 4px;
  right: 8px;
  text-decoration: none;
  color: #222222;
}

.ol-popup-content {
  margin-top: 6px;
}

.ol-popup-content a {
  color: #1c4f86;
  font-weight: 600;
  text-decoration: none;
}

.ol-popup-content a:hover {
  text-decoration: underline;
}
</style>
