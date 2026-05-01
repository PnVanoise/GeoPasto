<template>
  <div></div>
</template>

<script setup>
import { watch, onMounted, ref } from "vue";
import L from "leaflet";

const props = defineProps({
  map: Object, // Carte Leaflet passée en prop
});

onMounted(() => {
  watch(
    () => props.map,
    (newMap) => {
      if (newMap) {
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

        const OrthoIGN = L.tileLayer(
          "https://data.geopf.fr/wmts?" +
            "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&TILEMATRIXSET=PM" +
            "&LAYER={ignLayer}&STYLE={style}&FORMAT={format}" +
            "&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}",
          {
            ignLayer: "ORTHOIMAGERY.ORTHOPHOTOS",
            style: "normal",
            format: "image/jpeg",
            service: "WMTS",
          }
        );

        const ign3 = L.tileLayer(
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
            minZoom: 0,
            maxZoom: 18,
            attribution: "IGN-F/Geoportail",
            tileSize: 256, // les tuiles du Géooportail font 256x256px
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

        const osmplan = L.tileLayer(
          "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
          {
            attribution: "© OpenStreetMap contributors",
          }
        );

        const otmplan = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenTopoMap contributors",
        });

        const baseMaps = {
          "IGN Scan25": ignscan25,
          "Orthophoto IGN": ignorthophoto,
          OpenStreetMap: osmplan,
        };

        L.control.layers(baseMaps).addTo(newMap);
      }
    }
  );
});
</script>
