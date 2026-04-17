<template>
  <div class="quartier-geometry-editor">
    <div ref="mapElement" class="geometry-map"></div>

    <div class="geometry-toolbar">
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
import { Fill, Stroke, Style } from "ol/style";
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
});

const emit = defineEmits(["update:modelValue"]);
const mapElement = ref(null);

let map = null;
let source = null;
let vectorLayer = null;
let contextSource = null;
let contextLayer = null;
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

const geometryMatchesType = (geometryType) => {
  if (!geometryType) return false;
  if (props.geometryType === "MultiPolygon") {
    return geometryType === "Polygon" || geometryType === "MultiPolygon";
  }
  return geometryType === props.geometryType;
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
  const payload = props.contextGeoData;
  if (!payload) return;

  let featureCollection = null;

  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
    featureCollection = payload;
  } else if (payload.type === "Feature") {
    featureCollection = { type: "FeatureCollection", features: [payload] };
  } else if (Array.isArray(payload)) {
    featureCollection = { type: "FeatureCollection", features: payload };
  }

  if (!featureCollection) return;

  const features = new GeoJSON().readFeatures(featureCollection, {
    dataProjection: "EPSG:4326",
    featureProjection: "EPSG:3857",
  });

  contextSource.addFeatures(features);
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
  const features = source.getFeatures();
  if (!features.length) return null;

  const feature = features[0].clone();
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
  refreshMapSize();
};

const emitGeometry = () => {
  emit("update:modelValue", toOutputGeometry());
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
    emit("update:modelValue", toOutputGeometryFromFeature(event.feature));
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
    style: new Style({
      stroke: new Stroke({
        color: "rgba(51, 65, 85, 1)",
        width: 1.2,
        lineDash: [12, 7],
      }),
      fill: new Fill({
        color: "rgba(148, 163, 184, 0.24)",
      }),
    }),
  });

  vectorLayer.setZIndex(12);
  vectorLayer.set("displayInLayerSwitcher", false);
  contextLayer.set("displayInLayerSwitcher", false);

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
  if (source.getFeatures().length) {
    enableModify();
  } else {
    enableDraw();
  }

  refreshMapSize();
});

watch(
  () => props.modelValue,
  () => {
    syncFromModel();
    refreshMapSize();
  },
  { deep: true }
);

watch(
  () => props.contextGeoData,
  () => {
    syncContextLayer();
    refreshMapSize();
  },
  { deep: true }
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
