<template>
  <div class="quartier-geometry-editor">
    <div ref="mapElement" class="geometry-map"></div>

    <div v-if="!props.disabled" class="geometry-toolbar">
      <v-btn
        size="small"
        color="primary"
        variant="tonal"
        prepend-icon="mdi-pencil"
        @click="enableDraw"
      >
        Dessiner
      </v-btn>
      <v-btn
        size="small"
        color="primary"
        variant="tonal"
        prepend-icon="mdi-vector-polyline-edit"
        @click="enableModify"
      >
        Modifier
      </v-btn>
      <v-btn
        size="small"
        color="error"
        variant="tonal"
        prepend-icon="mdi-delete"
        @click="clearGeometry"
      >
        Effacer
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, nextTick, ref, watch } from "vue";
import "ol/ol.css";

import GeoJSON from "ol/format/GeoJSON";
import Map from "ol/Map";
import View from "ol/View";
import Draw from "ol/interaction/Draw";
import Modify from "ol/interaction/Modify";
import Snap from "ol/interaction/Snap";
import { Fill, Stroke, Style, Circle as CircleStyle, RegularShape } from "ol/style";
import TileLayer from "ol/layer/Tile";
import LayerGroup from "ol/layer/Group";
import VectorLayer from "ol/layer/Vector";
import OSM from "ol/source/OSM";
import VectorSource from "ol/source/Vector";
import XYZ from "ol/source/XYZ";
import LayerSwitcher from "ol-layerswitcher";
import "ol-layerswitcher/dist/ol-layerswitcher.css";

const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
  geometryType: {
    type: String,
    default: "Polygon",
  },
  contextGeoData: {
    type: Object,
    default: null,
  },
  contextLayers: {
    type: Array,
    default: () => [],
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "geometry-validity-change"]);
const mapElement = ref(null);

let map = null;
let source = null;
let vectorLayer = null;
let contextSource = null;
let contextLayer = null;
let contextPointOverlayLayer = null;
let drawInteraction = null;
let modifyInteraction = null;
let snapInteraction = null;
let contextSnapInteraction = null;
let resizeObserver = null;

const buildXyzSource = (url) => {
  return new XYZ({
    url,
    crossOrigin: "anonymous",
  });
};

const geometryTypeForDraw = () => {
  if (props.geometryType === "MultiPolygon") return "Polygon";
  return props.geometryType || "Polygon";
};

const normalizeGeoData = (payload) => {
  if (!payload) return null;
  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
    return payload;
  }
  if (payload.type === "Feature") {
    return { type: "FeatureCollection", features: [payload] };
  }
  if (Array.isArray(payload)) {
    return { type: "FeatureCollection", features: payload };
  }
  if (payload.geometry) {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: payload.geometry,
          properties: payload.properties || {},
        },
      ],
    };
  }
  return null;
};

const hexToRgba = (hexColor, alpha = 0.2) => {
  if (typeof hexColor !== "string") return `rgba(51, 65, 85, ${alpha})`;
  const sanitized = hexColor.replace("#", "");
  if (![3, 6].includes(sanitized.length)) return `rgba(51, 65, 85, ${alpha})`;
  const normalized = sanitized.length === 3
    ? sanitized.split("").map((char) => char + char).join("")
    : sanitized;
  const r = parseInt(normalized.slice(0, 2), 16);
  const g = parseInt(normalized.slice(2, 4), 16);
  const b = parseInt(normalized.slice(4, 6), 16);
  if ([r, g, b].some((value) => Number.isNaN(value))) return `rgba(51, 65, 85, ${alpha})`;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const buildContextFeatureStyle = (feature) => {
  const layerStyle = feature?.get?.("__layerStyle") || {};
  const geometryType = feature?.getGeometry?.()?.getType?.() || "";
  const strokeColor = layerStyle.strokeColor || "#334155";
  const strokeWidth = Number.isFinite(layerStyle.strokeWidth) ? layerStyle.strokeWidth : 1.4;
  const fillOpacity = Number.isFinite(layerStyle.fillOpacity) ? layerStyle.fillOpacity : 0.2;
  const lineDash = Array.isArray(layerStyle.lineDash) ? layerStyle.lineDash : undefined;
  const pointRadius = Number.isFinite(layerStyle.pointRadius) ? layerStyle.pointRadius : 6;
  const pointShape = layerStyle.pointShape || "circle";
  const pointStrokeColor = layerStyle.pointStrokeColor || "#ffffff";
  const pointStrokeWidth = Number.isFinite(layerStyle.pointStrokeWidth)
    ? layerStyle.pointStrokeWidth
    : 1.3;

  const styleZIndex = (geometryType === "Point" || geometryType === "MultiPoint")
    ? 32
    : (geometryType === "LineString" || geometryType === "MultiLineString")
      ? 24
      : 12;

  let imageStyle;
  if (pointShape === "triangle") {
    imageStyle = new RegularShape({
      points: 3,
      radius: pointRadius,
      fill: new Fill({ color: strokeColor }),
      stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
    });
  } else if (pointShape === "square") {
    imageStyle = new RegularShape({
      points: 4,
      radius: pointRadius,
      angle: 0,
      fill: new Fill({ color: strokeColor }),
      stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
    });
  } else if (pointShape === "diamond") {
    imageStyle = new RegularShape({
      points: 4,
      radius: pointRadius,
      angle: Math.PI / 4,
      fill: new Fill({ color: strokeColor }),
      stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
    });
  } else {
    imageStyle = new CircleStyle({
      radius: pointRadius,
      fill: new Fill({ color: strokeColor }),
      stroke: new Stroke({ color: pointStrokeColor, width: pointStrokeWidth }),
    });
  }

  return new Style({
    zIndex: styleZIndex,
    stroke: new Stroke({
      color: strokeColor,
      width: strokeWidth,
      lineDash,
    }),
    fill: new Fill({
      color: hexToRgba(strokeColor, fillOpacity),
    }),
    image: imageStyle,
  });
};

const getGeometryType = (feature) => {
  return feature?.getGeometry?.()?.getType?.() || "";
};

const isPointGeometry = (feature) => {
  const geometryType = getGeometryType(feature);
  return geometryType === "Point" || geometryType === "MultiPoint";
};

const buildContextBaseStyle = (feature) => {
  if (isPointGeometry(feature)) return null;
  return buildContextFeatureStyle(feature);
};

const buildContextPointOverlayStyle = (feature) => {
  if (!isPointGeometry(feature)) return null;
  return buildContextFeatureStyle(feature);
};

const geometryMatchesType = (geometryType) => {
  if (!geometryType) return false;
  if (props.geometryType === "MultiPolygon") {
    return geometryType === "Polygon" || geometryType === "MultiPolygon";
  }
  return geometryType === props.geometryType;
};

const computeGeometryValidity = (geometry) => {
  if (!geometry || !geometry.type) {
    return { isValid: false, reason: "geometry_required" };
  }

  if (!geometryMatchesType(geometry.type)) {
    return { isValid: false, reason: "geometry_type_mismatch" };
  }

  if (geometry.type === "Point") {
    const isValidPoint = Array.isArray(geometry.coordinates) && geometry.coordinates.length >= 2;
    return { isValid: isValidPoint, reason: isValidPoint ? null : "point_coordinates_invalid" };
  }

  if (geometry.type === "LineString") {
    const isValidLine = Array.isArray(geometry.coordinates) && geometry.coordinates.length >= 2;
    return { isValid: isValidLine, reason: isValidLine ? null : "line_coordinates_invalid" };
  }

  if (geometry.type === "Polygon") {
    const ring = geometry.coordinates?.[0];
    const isValidPolygon = Array.isArray(ring) && ring.length >= 4;
    return { isValid: isValidPolygon, reason: isValidPolygon ? null : "polygon_coordinates_invalid" };
  }

  if (geometry.type === "MultiPolygon") {
    const firstRing = geometry.coordinates?.[0]?.[0];
    const isValidMultiPolygon = Array.isArray(firstRing) && firstRing.length >= 4;
    return { isValid: isValidMultiPolygon, reason: isValidMultiPolygon ? null : "multipolygon_coordinates_invalid" };
  }

  return { isValid: false, reason: "unsupported_geometry_type" };
};

const emitGeometryValidity = (geometry) => {
  const validity = computeGeometryValidity(geometry);
  emit("geometry-validity-change", validity);
};

const keepOnlyLastEditableFeature = () => {
  if (!source) return;
  const features = source.getFeatures();
  if (!Array.isArray(features) || features.length <= 1) return;

  const lastFeature = features[features.length - 1];
  source.clear();
  source.addFeature(lastFeature);
};

const fitToFeatures = () => {
  if (!map || !source) return;
  const features = source.getFeatures();
  if (!features.length) return;
  const extent = source.getExtent();
  if (!extent || extent.some((v) => !Number.isFinite(v))) return;
  map.getView().fit(extent, {
    padding: [30, 30, 30, 30],
    duration: 200,
    maxZoom: 17,
  });
};

const fitToGeometry = (geometry3857) => {
  if (!map || !geometry3857) return;
  const extent = geometry3857.getExtent();
  if (!extent || extent.some((v) => !Number.isFinite(v))) return;
  map.getView().fit(extent, {
    padding: [30, 30, 30, 30],
    duration: 200,
    maxZoom: 17,
  });
};

const fitToAvailableFeatures = () => {
  if (!map) return;

  const editableCount = source?.getFeatures()?.length || 0;
  const contextCount = contextSource?.getFeatures()?.length || 0;

  if (editableCount > 0) {
    fitToFeatures();
    return;
  }

  if (contextCount > 0) {
    const extent = contextSource.getExtent();
    if (!extent || extent.some((v) => !Number.isFinite(v))) return;
    map.getView().fit(extent, {
      padding: [30, 30, 30, 30],
      duration: 200,
      maxZoom: 17,
    });
  }
};

const syncContextLayer = () => {
  if (!contextSource) return;

  contextSource.clear();

  const normalizedLayers = (Array.isArray(props.contextLayers) ? props.contextLayers : [])
    .filter((layer) => layer && layer.visible !== false)
    .map((layer, index) => ({
      id: layer.id || `context_${index + 1}`,
      data: normalizeGeoData(layer.data),
      style: layer.style || {},
    }))
    .filter((layer) => layer.data);

  if (!normalizedLayers.length) {
    const legacyCollection = normalizeGeoData(props.contextGeoData);
    if (!legacyCollection) return;

    const legacyFeatures = new GeoJSON().readFeatures(legacyCollection, {
      dataProjection: "EPSG:4326",
      featureProjection: "EPSG:3857",
    });

    legacyFeatures.forEach((feature) => {
      feature.set("__layerStyle", {
        strokeColor: "#334155",
        strokeWidth: 1.2,
        lineDash: [12, 7],
        fillOpacity: 0.24,
      });
    });

    contextSource.addFeatures(legacyFeatures);
    return;
  }

  normalizedLayers.forEach((layer) => {
    const features = new GeoJSON().readFeatures(layer.data, {
      dataProjection: "EPSG:4326",
      featureProjection: "EPSG:3857",
    });

    features.forEach((feature) => {
      feature.set("__layerStyle", layer.style || {});
      feature.set("__layerId", layer.id);
    });

    contextSource.addFeatures(features);
  });
};

const refreshMapSize = () => {
  if (!map) return;

  // OpenLayers can initialize before modal/layout dimensions settle.
  requestAnimationFrame(() => {
    map.updateSize();
    fitToAvailableFeatures();
  });

  setTimeout(() => {
    if (!map) return;
    map.updateSize();
    fitToAvailableFeatures();
  }, 120);
};

const toOutputGeometry = () => {
  if (!source) return null;
  keepOnlyLastEditableFeature();
  const features = source.getFeatures();
  if (!features.length) return null;

  const feature = features[features.length - 1].clone();
  const geometry = feature.getGeometry();
  if (!geometry) return null;

  geometry.transform("EPSG:3857", "EPSG:4326");
  const geometryObject = new GeoJSON().writeGeometryObject(geometry);

  if (props.geometryType === "MultiPolygon" && geometryObject.type === "Polygon") {
    return {
      type: "MultiPolygon",
      coordinates: [geometryObject.coordinates],
    };
  }

  return geometryObject;
};

const toOutputGeometryFromFeature = (feature) => {
  if (!feature) return null;

  const clonedFeature = feature.clone();
  const geometry = clonedFeature.getGeometry();
  if (!geometry) return null;

  geometry.transform("EPSG:3857", "EPSG:4326");
  const geometryObject = new GeoJSON().writeGeometryObject(geometry);

  if (props.geometryType === "MultiPolygon" && geometryObject.type === "Polygon") {
    return {
      type: "MultiPolygon",
      coordinates: [geometryObject.coordinates],
    };
  }

  return geometryObject;
};

const syncFromModel = () => {
  if (!source) return;

  source.clear();

  const geometry = props.modelValue;
  if (!geometry || !geometry.coordinates) return;
  if (!geometryMatchesType(geometry.type)) return;

  const normalizedGeometry =
    props.geometryType === "MultiPolygon" && geometry.type === "Polygon"
      ? { type: "MultiPolygon", coordinates: [geometry.coordinates] }
      : geometry;

  const feature = new GeoJSON().readFeature(
    {
      type: "Feature",
      geometry: normalizedGeometry,
      properties: {},
    },
    {
      dataProjection: "EPSG:4326",
      featureProjection: "EPSG:3857",
    }
  );

  source.addFeature(feature);
  keepOnlyLastEditableFeature();
  refreshMapSize();
};

const emitGeometry = () => {
  const geometry = toOutputGeometry();
  emit("update:modelValue", geometry);
  emitGeometryValidity(geometry);
};

const removeInteractions = () => {
  if (!map) return;
  if (drawInteraction) map.removeInteraction(drawInteraction);
  if (modifyInteraction) map.removeInteraction(modifyInteraction);
  if (snapInteraction) map.removeInteraction(snapInteraction);
  if (contextSnapInteraction) map.removeInteraction(contextSnapInteraction);
  drawInteraction = null;
  modifyInteraction = null;
  snapInteraction = null;
  contextSnapInteraction = null;
};

const enableDraw = () => {
  if (!map || !source) return;
  removeInteractions();

  drawInteraction = new Draw({
    source,
    type: geometryTypeForDraw(),
  });

  drawInteraction.on("drawstart", () => {
    source.clear();
  });

  drawInteraction.on("drawend", (event) => {
    keepOnlyLastEditableFeature();
    const outputGeometry = toOutputGeometryFromFeature(event.feature);
    emit("update:modelValue", outputGeometry);
    emitGeometryValidity(outputGeometry);
    fitToGeometry(event.feature?.getGeometry?.());
    enableModify();
  });

  map.addInteraction(drawInteraction);
  snapInteraction = new Snap({ source });
  map.addInteraction(snapInteraction);
  if (contextSource) {
    contextSnapInteraction = new Snap({ source: contextSource });
    map.addInteraction(contextSnapInteraction);
  }
};

const enableModify = () => {
  if (!map || !source) return;
  removeInteractions();

  modifyInteraction = new Modify({ source });
  modifyInteraction.on("modifyend", () => {
    emitGeometry();
  });

  map.addInteraction(modifyInteraction);
  snapInteraction = new Snap({ source });
  map.addInteraction(snapInteraction);
  if (contextSource) {
    contextSnapInteraction = new Snap({ source: contextSource });
    map.addInteraction(contextSnapInteraction);
  }
};

const clearGeometry = () => {
  if (!source) return;
  source.clear();
  emit("update:modelValue", null);
  emitGeometryValidity(null);
};

const applyInteractionMode = () => {
  if (!map || !source) return;
  removeInteractions();
  if (props.disabled) return;

  if (source.getFeatures().length) {
    enableModify();
  } else {
    enableDraw();
  }
};

defineExpose({
  getGeometry: () => toOutputGeometry(),
  hasGeometry: () => {
    if (!source) return false;
    const features = source.getFeatures();
    return Array.isArray(features) && features.length > 0;
  },
});

onMounted(async () => {
  await nextTick();
  if (!mapElement.value) return;

  source = new VectorSource();
  contextSource = new VectorSource();

  vectorLayer = new VectorLayer({ source });
  contextLayer = new VectorLayer({
    source: contextSource,
    zIndex: 8,
    style: buildContextBaseStyle,
  });

  contextPointOverlayLayer = new VectorLayer({
    source: contextSource,
    zIndex: 16,
    style: buildContextPointOverlayStyle,
  });

  vectorLayer.setZIndex(12);
  vectorLayer.set("displayInLayerSwitcher", false);
  contextLayer.set("displayInLayerSwitcher", false);
  contextPointOverlayLayer.set("displayInLayerSwitcher", false);

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

  map = new Map({
    target: mapElement.value,
    layers: [
      baseMapsGroup,
      overlaysGroup,
      contextLayer,
      vectorLayer,
      contextPointOverlayLayer,
    ],
    view: new View({
      center: [751000, 5721000],
      zoom: 10,
    }),
  });

  const layerSwitcher = new LayerSwitcher({
    activationMode: "click",
    startActive: false,
    tipLabel: "Fonds de carte",
    groupSelectStyle: "none",
  });
  map.addControl(layerSwitcher);

  resizeObserver = new ResizeObserver(() => {
    refreshMapSize();
  });
  resizeObserver.observe(mapElement.value);

  syncContextLayer();
  syncFromModel();
  applyInteractionMode();
  emitGeometryValidity(props.modelValue ?? null);

  refreshMapSize();
});

watch(
  () => props.modelValue,
  (newValue) => {
    syncFromModel();
    applyInteractionMode();
    refreshMapSize();
    emitGeometryValidity(newValue ?? null);
  },
  { deep: true }
);

watch(
  () => props.disabled,
  () => {
    applyInteractionMode();
  }
);

watch(
  () => props.contextGeoData,
  () => {
    syncContextLayer();
    refreshMapSize();
  },
  { deep: true }
);

watch(
  () => props.contextLayers,
  () => {
    syncContextLayer();
    refreshMapSize();
  },
  { deep: true }
);

watch(
  () => props.geometryType,
  (newType, oldType) => {
    if (!map || !source) return;
    if (newType === oldType) return;

    source.clear();
    emit("update:modelValue", null);
    emitGeometryValidity(null);
    applyInteractionMode();
    refreshMapSize();
  }
);

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }

  removeInteractions();
  if (map) {
    map.setTarget(undefined);
    map = null;
  }
  contextSource = null;
  contextLayer = null;
  contextPointOverlayLayer = null;
});
</script>

<style scoped>
.quartier-geometry-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.geometry-map {
  width: 100%;
  height: 420px;
  min-height: 360px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  overflow: hidden;
}

.geometry-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
</style>
