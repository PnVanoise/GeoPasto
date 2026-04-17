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
import { Fill, Stroke, Style, Circle as CircleStyle, RegularShape } from "ol/style";
import Overlay from "ol/Overlay";
import TileLayer from "ol/layer/Tile";
import LayerGroup from "ol/layer/Group";
import VectorLayer from "ol/layer/Vector";
import OSM from "ol/source/OSM";
import VectorSource from "ol/source/Vector";
import XYZ from "ol/source/XYZ";
import LayerSwitcher from "ol-layerswitcher";
import "ol-layerswitcher/dist/ol-layerswitcher.css";

const emit = defineEmits(["open-popup-item"]);

const props = defineProps({
  layers: {
    type: Array,
    default: () => [],
  },
});

const mapElement = ref(null);
const popupElement = ref(null);
const popupContent = ref(null);

let map = null;
let vectorLayer = null;
let popupOverlay = null;

const buildXyzSource = (url) => {
  return new XYZ({
    url,
    crossOrigin: "anonymous",
  });
};

const buildStyle = () => {
  return (feature) => {
    const layerStyle = feature?.get?.("__layerStyle") || {};
    const layerName = feature?.get?.("__layer") || "quartier";
    const isUpOutline = layerName === "up_outline";
    const isEvent = layerName === "evenement" || layerName === "evenement_marker";
    const isEventMarker = layerName === "evenement_marker";

    const strokeColor = layerStyle.strokeColor || (isUpOutline
      ? "#dc2626"
      : isEvent
        ? "#dc2626"
        : "#008000");

    const strokeWidth = layerStyle.strokeWidth ?? (isUpOutline
      ? 2
      : isEvent
        ? 2
        : 2);

    const fillOpacity = layerStyle.fillOpacity ?? (isUpOutline
      ? 0
      : isEvent
        ? 0.15
        : 0.3);

    const radius = layerStyle.pointRadius ?? (isEventMarker
      ? 8
      : isEvent
        ? 6
        : 6);
    const pointShape = layerStyle.pointShape || "circle";
    const pointStrokeColor = layerStyle.pointStrokeColor || "#ffffff";
    const pointStrokeWidth = Number.isFinite(layerStyle.pointStrokeWidth)
      ? layerStyle.pointStrokeWidth
      : 2;

    const lineDash = Array.isArray(layerStyle.lineDash)
      ? layerStyle.lineDash
      : (isUpOutline ? [8, 6] : undefined);

    const zIndex = layerStyle.zIndex ?? (isUpOutline ? 12 : isEventMarker ? 20 : isEvent ? 15 : 10);

    let imageStyle;
    if (pointShape === "triangle") {
      imageStyle = new RegularShape({
        points: 3,
        radius,
        rotation: 0,
        fill: new Fill({ color: strokeColor }),
        stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
      });
    } else if (pointShape === "diamond") {
      imageStyle = new RegularShape({
        points: 4,
        radius,
        angle: Math.PI / 4,
        fill: new Fill({ color: strokeColor }),
        stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
      });
    } else if (pointShape === "square") {
      imageStyle = new RegularShape({
        points: 4,
        radius,
        angle: 0,
        fill: new Fill({ color: strokeColor }),
        stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
      });
    } else {
      imageStyle = new CircleStyle({
        radius,
        fill: new Fill({ color: strokeColor }),
        stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
      });
    }

    return new Style({
      stroke: new Stroke({
        color: strokeColor,
        width: strokeWidth,
        lineDash,
      }),
      fill: new Fill({
        color: hexToRgba(strokeColor, fillOpacity),
      }),
      image: imageStyle,
      zIndex,
    });
  };
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
  const source = vectorLayer.getSource();
  source.clear();

  const normalizedLayers = (Array.isArray(props.layers) ? props.layers : [])
    .filter((layer) => layer && layer.visible !== false)
    .map((layer, idx) => ({
      id: layer.id || `layer_${idx + 1}`,
      data: normalizeGeoData(layer.data),
      style: layer.style || {},
      popup: layer.popup || {},
    }))
    .filter((layer) => layer.data);

  if (!normalizedLayers.length) {
    map.getView().setCenter([0, 0]);
    map.getView().setZoom(2);
    return;
  }

  const features = [];

  normalizedLayers.forEach((layer) => {
    const layerFeatures = new GeoJSON().readFeatures(layer.data, {
      featureProjection: "EPSG:3857",
    });

    layerFeatures.forEach((f) => {
      if (!f.get("__layer")) {
        f.set("__layer", layer.id);
      }
      f.set("__layerStyle", layer.style || {});
      f.set("__popupConfig", layer.popup || {});
    });

    features.push(...layerFeatures);
  });

  if (!features.length) {
    map.getView().setCenter([0, 0]);
    map.getView().setZoom(2);
    return;
  }

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
  const popupConfig = properties.__popupConfig || {};
  const popupIdAttribute = popupConfig.idAttribute || null;
  const id = popupIdAttribute
    ? (properties[popupIdAttribute] ?? properties.id ?? feature.getId())
    : (properties.id ?? feature.getId());
  const layerName = properties.__layer || "";
  const objectTypeLabel = popupConfig.typeLabel || getObjectTypeLabel(layerName);
  const popupAttribute = popupConfig.attribute || "id";
  const popupRoute = popupConfig.route ?? "";
  const popupContentType = popupConfig.contentType || null;
  const label = properties[popupAttribute] || id || "Détails";

  const href = id && popupRoute ? `${popupRoute}/${id}` : "";

  if (popupContentType === "eventCompact") {
    popupContent.value.innerHTML = buildEventPopupHtml(properties, label, href, id, objectTypeLabel);
    popupOverlay.setPosition(coordinate);
    return;
  }

  popupContent.value.innerHTML = buildGenericPopupHtml(label, href, id, objectTypeLabel, popupConfig);

  popupOverlay.setPosition(coordinate);
};

const getObjectTypeLabel = (layerName) => {
  if (layerName === "up_outline") return "UP";
  if (layerName === "quartier") return "Quartier";
  if (layerName === "evenement" || layerName === "evenement_marker") return "Événement";
  return "Objet";
};

const buildGenericPopupHtml = (label, href, id, objectTypeLabel, popupConfig = {}) => {
  const safeLabel = escapeHtml(String(label || "Détails"));
  const safeType = escapeHtml(String(objectTypeLabel || "Objet"));
  const safeId = id ? escapeHtml(String(id)) : "";

  if (!href || !id) {
    return `
      <div class="popup-object-type"><strong>${safeType}</strong></div>
      <div><strong>${safeLabel}</strong></div>
    `;
  }

  const popupEditHref = href;
  const popupViewHref = popupConfig.viewRoute
    ? `${popupConfig.viewRoute}/${id}`
    : popupEditHref;
  const canEdit = popupConfig.canEdit !== false;

  return `
    <div class="popup-object-type"><strong>${safeType}</strong></div>
    <div><strong>${safeLabel}</strong></div>
    <div class="popup-actions">
      <a
        href="${popupViewHref}"
        class="popup-action-link popup-action-link--view"
        data-feature-id="${safeId}"
        data-feature-label="${safeLabel}"
        data-feature-action="view"
        title="Voir"
        aria-label="Voir"
      >voir</a>
      ${canEdit ? `
      <a
        href="${popupEditHref}"
        class="popup-action-link popup-action-link--edit"
        data-feature-id="${safeId}"
        data-feature-label="${safeLabel}"
        data-feature-action="edit"
        title="Éditer"
        aria-label="Éditer"
      >éditer</a>
      ` : ""}
    </div>
  `;
};

const buildEventPopupHtml = (properties, label, href, id, objectTypeLabel) => {
  const safeType = escapeHtml(String(objectTypeLabel || "Événement"));
  const dateEvenement = properties.date_evenement ? escapeHtml(String(properties.date_evenement)) : "date inconnue";
  const observateur = properties.observateur ? escapeHtml(String(properties.observateur)) : "Observateur inconnu";
  const typeEvenementRaw =
    properties.type_evenement_label
    || properties.type_evenement_detail?.description
    || (properties.type_evenement != null ? `Type ${properties.type_evenement}` : null);
  const typeEvenement = typeEvenementRaw ? escapeHtml(String(typeEvenementRaw)) : "Type inconnu";
  const description = properties.description ? escapeHtml(String(properties.description)) : "-";

  const details = `
    <div class="popup-event">
      <div class="popup-object-type"><strong>${safeType}</strong></div>
      <div>${observateur} le ${dateEvenement}</div>
      <div>${typeEvenement}</div>
      <div>${description}</div>
    </div>
  `;

  if (!href || !id) return details;

  return `${details}<div class="popup-event-link"><a href="${href}" data-feature-id="${escapeHtml(String(id))}" data-feature-label="${escapeHtml(String(label || "Événement"))}">lien vers fiche</a></div>`;
};

const onPopupContentClick = (event) => {
  const link = event.target?.closest?.("a[data-feature-id]");
  if (!link) return;

  event.preventDefault();
  const id = link.getAttribute("data-feature-id");
  const label = link.getAttribute("data-feature-label") || "";
  const action = link.getAttribute("data-feature-action") || "view";
  if (!id) return;

  emit("open-popup-item", { id, label, action });
};

const zoomToFeature = (feature) => {
  if (!map || !feature) return;

  const geometry = feature.getGeometry?.();
  if (!geometry) return;

  const extent = geometry.getExtent?.();
  if (!extent || !extent.every((v) => Number.isFinite(v))) return;

  if (geometry.getType?.() === "Point") {
    const center = geometry.getCoordinates?.();
    if (!center || !center.every((v) => Number.isFinite(v))) return;
    map.getView().animate({
      center,
      duration: 250,
      zoom: Math.max(map.getView().getZoom() || 2, 16),
    });
    return;
  }

  map.getView().fit(extent, {
    duration: 250,
    padding: [30, 30, 30, 30],
    maxZoom: 16,
  });
};

const closePopup = () => {
  if (popupOverlay) popupOverlay.setPosition(undefined);
};

const pickFeatureForPopup = (event) => {
  if (!map) return null;

  const picked = [];
  map.forEachFeatureAtPixel(event.pixel, (feature) => {
    if (feature) picked.push(feature);
    return false;
  });

  if (!picked.length) return null;

  const getPriority = (feature) => {
    const layerName = feature?.get?.("__layer") || "";
    const geometryType = feature?.getGeometry?.()?.getType?.() || "";
    const layerStyle = feature?.get?.("__layerStyle") || {};
    const zIndex = Number.isFinite(layerStyle.zIndex) ? layerStyle.zIndex : 0;
    const isPoint = geometryType === "Point";

    // Strongly prefer point-like interactive objects over background polygons.
    if (layerName === "evenement" && isPoint) return 1;
    if (layerName === "equipement_up" && isPoint) return 2;
    if (layerName === "equipement_situation" && isPoint) return 3;
    if (layerName === "evenement") return 4;
    if (layerName === "equipement_up") return 5;
    if (layerName === "equipement_situation") return 6;
    if (layerName === "quartier") return 10;
    if (layerName === "up_outline") return 20;

    // Fallback: higher visual zIndex should win.
    return 100 - zIndex;
  };

  picked.sort((a, b) => getPriority(a) - getPriority(b));
  return picked[0] || null;
};

const initMap = () => {
  const osmLayer = new TileLayer({
    title: "OpenStreetMap",
    type: "base",
    source: new OSM(),
    visible: true,
  });

  const ignScan25Layer = new TileLayer({
    title: "IGN Scan25",
    type: "base",
    source: buildXyzSource(
      "https://data.geopf.fr/private/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&FORMAT=image/jpeg&STYLE=normal&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&apikey=ign_scan_ws"
    ),
    visible: false,
  });

  const ignOrthoLayer = new TileLayer({
    title: "IGN Orthophoto",
    type: "base",
    source: buildXyzSource(
      "https://data.geopf.fr/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
    ),
    visible: false,
  });

  const cadastreLayer = new TileLayer({
    title: "Parcelles cadastrales",
    source: buildXyzSource(
      "https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
    ),
    visible: false,
  });

  const baseMapsGroup = new LayerGroup({
    title: "Fonds",
    layers: [osmLayer, ignScan25Layer, ignOrthoLayer],
  });

  const overlaysGroup = new LayerGroup({
    title: "Surcouches",
    layers: [cadastreLayer],
  });

  vectorLayer = new VectorLayer({
    source: new VectorSource(),
    style: buildStyle(),
  });
  vectorLayer.set("displayInLayerSwitcher", false);

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
      baseMapsGroup,
      overlaysGroup,
      vectorLayer,
    ],
    overlays: [popupOverlay],
    controls: defaultControls().extend([new ScaleLine()]),
    view: new View({
      center: [0, 0],
      zoom: 2,
    }),
  });

  const layerSwitcher = new LayerSwitcher({
    activationMode: "click",
    startActive: false,
    tipLabel: "Fonds de carte",
    groupSelectStyle: "none",
  });
  map.addControl(layerSwitcher);

  map.on("singleclick", (event) => {
    const pickedFeature = pickFeatureForPopup(event);

    if (pickedFeature) {
      zoomToFeature(pickedFeature);
      openPopupForFeature(pickedFeature, event.coordinate);
    } else {
      closePopup();
    }
  });

  updateVectorLayer();
};

watch(
  () => props.layers,
  () => {
    updateVectorLayer();
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

:deep(.layer-switcher) {
  top: 0.75em;
  right: 0.75em;
}

:deep(.layer-switcher button) {
  width: 28px;
  height: 28px;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  text-align: center;
  border-radius: 6px;
  background-size: 16px 16px;
  background-position: center center;
}

:deep(.layer-switcher .panel) {
  min-width: 170px;
  max-width: 220px;
  max-height: 220px;
  overflow: auto;
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 0.74rem;
  line-height: 1.15;
}

:deep(.layer-switcher .group label) {
  font-size: 0.74rem;
}

:deep(.layer-switcher .group + .group) {
  margin-top: 6px;
}

:deep(.layer-switcher .group ul) {
  margin: 4px 0 0;
}

:deep(.layer-switcher li) {
  margin: 2px 0;
}

:deep(.layer-switcher input) {
  transform: scale(0.9);
  margin-right: 4px;
}

.ol-map {
  width: 100%;
  height: 600px;
}

.ol-popup {
  position: absolute;
  background-color: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #cccccc;
  min-width: 170px;
  max-width: 260px;
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
  margin-top: 4px;
  font-size: 0.78rem;
}

:deep(.popup-actions) {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}

:deep(.popup-action-link) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  font-size: 0.76rem;
  line-height: 1;
}

:deep(.popup-action-link::before) {
  content: "";
  width: 14px;
  height: 14px;
  display: inline-block;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 14px 14px;
}

:deep(.ol-popup-content a) {
  color: inherit;
  font-weight: 600;
  text-decoration: none;
}

:deep(.ol-popup-content a:hover) {
  text-decoration: underline;
}

:deep(.popup-event) {
  display: grid;
  gap: 1px;
  font-size: 0.76rem;
  line-height: 1.2;
}

:deep(.popup-object-type) {
  font-size: 0.72rem;
  color: #475569;
}

:deep(.popup-event-link) {
  margin-top: 4px;
}

:deep(.popup-action-link--view) {
  color: #2ecc71;
}

:deep(.popup-action-link--view::before) {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232ecc71' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E");
}

:deep(.popup-action-link--view:hover) {
  color: #27ae60;
}

:deep(.popup-action-link--view:hover::before) {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2327ae60' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E");
}

:deep(.popup-action-link--edit) {
  color: #3498db;
}

:deep(.popup-action-link--edit::before) {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233498db' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 20h9'/%3E%3Cpath d='M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z'/%3E%3C/svg%3E");
}

:deep(.popup-action-link--edit:hover) {
  color: #2980b9;
}

:deep(.popup-action-link--edit:hover::before) {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232980b9' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 20h9'/%3E%3Cpath d='M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z'/%3E%3C/svg%3E");
}
</style>
