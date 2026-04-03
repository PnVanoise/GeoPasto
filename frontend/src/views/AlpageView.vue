<template>
    <div>
        <h2>Quartier d'alpage {{ quartier_nom }}</h2>
        <div id="map-container">
            <div id="map" style="height: 500px;"></div>
        </div>
        <hr>
        <div v-if="selectedFeature">
            <div v-if="!isEditing">
                <h3>Détails du Quartier</h3>
                <p><strong>Code du quartier:</strong> {{ selectedFeature.properties.quartier_code }}</p>
                <p><strong>Surface du quartier:</strong> {{ selectedFeature.properties.surface }}</p>
                <p><strong>Code de l'UP:</strong> {{ selectedFeature.properties.up_code }}</p>
                <p><strong>Nom de l'UP (1):</strong> {{ selectedFeature.properties.up_nom_1 }}</p>
                <p><strong>Nom de l'UP (2):</strong> {{ selectedFeature.properties.up_nom_2 }}</p>
                <p><strong>Code quartier (court):</strong> {{ selectedFeature.properties.quartier_code_court }}</p>
                <p><strong>Nom du quartier:</strong> {{ selectedFeature.properties.quartier_nom }}</p>
                <button @click="startEdit">Modifier</button>
                <button @click="confirmDelete">Supprimer</button>
            </div>

            <div v-else>
                <h2>Éditer Alpage</h2>
                <div class="container">
                    <form @submit.prevent="updateAlpage">
                        <div class="row">
                            <div class="col-25">
                                <label for="quartier_code">Code du quartier:</label>
                            </div>
                            <div class="col-75">
                                <input id="quartier_code" type="text" placeholder="Code du quartier"
                                    v-model="selectedFeature.properties.quartier_code" />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-25">
                                <label for="surface_quartier">Surface du quartier:</label>
                            </div>
                            <div class="col-75">
                                <input id="surface_quartier" type="text" placeholder="Surface du quartier"
                                    v-model="selectedFeature.properties.surface" />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-25">
                                <label for="up_code">Code de l'UP:</label>
                            </div>
                            <div class="col-75">
                                <input id="up_code" type="text" placeholder="Code de l'UP"
                                    v-model="selectedFeature.properties.up_code" />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-25">
                                <label for="up_nom_1">Nom de l'UP (1):</label>
                            </div>
                            <div class="col-75">
                                <input id="up_nom_1" type="text" placeholder="Nom de l'UP (1)"
                                    v-model="selectedFeature.properties.up_nom_1" />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-25">
                                <label for="up_nom_2">Nom de l'UP (2):</label>
                            </div>
                            <div class="col-75">
                                <input id="up_nom_2" type="text" placeholder="Nom de l'UP (2)"
                                    v-model="selectedFeature.properties.up_nom_2" />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-25">
                                <label for="quartier_code_court">Code quartier (court):</label>
                            </div>
                            <div class="col-75">
                                <input id="quartier_code_court" type="text" placeholder="Code quartier (court)"
                                    v-model="selectedFeature.properties.quartier_code_court" />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-25">
                                <label for="quartier_nom">Nom du quartier:</label>
                            </div>
                            <div class="col-75">
                                <input id="quartier_nom" type="text" placeholder="Nom du quartier"
                                    v-model="selectedFeature.properties.quartier_nom" />
                            </div>
                        </div>
                        <!-- <div class="row">
                            <div class="col-25">
                                <label for="quartier_geom">Géométrie:</label>
                            </div>
                            <div class="col-75">
                                <textarea id="quartier_geom" placeholder="Géométrie" v-model="selectedFeature.geometry"
                                    style="height:200px"></textarea>
                            </div>
                        </div> -->
                        <br>
                        <div class="row">
                            <button type="submit">Enregistrer</button>
                            <button @click="cancelEdit">Annuler</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Modale de confirmation de suppression -->
        <div v-if="showDeleteModal" class="modal">
            <div class="modal-content">
                <span class="close" @click="closeDeleteModal">&times;</span>
                <p>Êtes-vous sûr de vouloir supprimer ce quartier ?</p>
                <button @click="deleteAlpage">Oui</button>
                <button @click="closeDeleteModal">Non</button>
            </div>
        </div>
    </div>
</template>

<script setup>

import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';

import config from '../../config';

const route = useRoute();
const router = useRouter();
let map;
let datajson = ref();
let quartier_nom = ref(null);
let selectedFeature = ref(null);
let isEditing = ref(false);
let showDeleteModal = ref(false);
let editableLayers;

const ignscan25 = L.tileLayer('https://data.geopf.fr/private/wmts?' +
    'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0' +
    '&FORMAT=image/jpeg' +
    '&STYLE=normal' +
    '&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR' +
    '&TILEMATRIXSET=PM' +
    '&TILEMATRIX={z}' +
    '&TILEROW={y}' +
    '&TILECOL={x}' +
    '&apikey=ign_scan_ws', {
    attribution: 'IGN-F/Geoportail'
});
const ignorthophoto = L.tileLayer("https://data.geopf.fr/wmts?" +
    "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
    "&STYLE=normal" +
    "&TILEMATRIXSET=PM" +
    "&FORMAT=image/jpeg" +
    "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS" +
    "&TILEMATRIX={z}" +
    "&TILEROW={y}" +
    "&TILECOL={x}", {
    attribution: 'IGN-F/Geoportail'
});

const osmplan = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
});

const otmplan = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenTopoMap contributors'
});

const baseMaps = {
    "IGN Scan25": ignscan25,
    "Orthophoto IGN": ignorthophoto,
    "OpenStreetMap": osmplan,
    "OpenTopoMaps": otmplan
};

async function fetchGeoJSON() {
    try {
        const response = await fetch(`${config.API_BASE_URL}/api/quartierUP/${route.params.id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        datajson.value = await response.json();
        return datajson.value;
    } catch (error) {
        console.error('Error fetching GeoJSON:', error);
        return null;
    }
}

function startEdit() {
    isEditing.value = true;
    if (selectedFeature.value) {
        editableLayers = new L.FeatureGroup();
        map.addLayer(editableLayers);

        const editableFeature = L.geoJSON(selectedFeature.value, {
            onEachFeature: function (feature, layer) {
                editableLayers.addLayer(layer);
            }
        }).addTo(map);
        map.fitBounds(editableFeature.getBounds());

        const drawControl = new L.Control.Draw({
            edit: {
                featureGroup: editableLayers,
                selectedPathOptions: {
                    maintainColor: true,
                    opacity: 0.3
                },
            },
            draw: false
        });
        map.addControl(drawControl);


        map.on('draw:editvertex', function (event) {
            console.log('event.poly: ', event.poly);
        });

        map.on(L.Draw.Event.EDITED, function (event) {
            const layers = event.layers;
            layers.eachLayer(function (layer) {
                selectedFeature.value.geometry = layer.toGeoJSON().geometry;
            });
        });

    }
}

function cancelEdit() {
    isEditing.value = false;
    map.removeLayer(editableLayers);
    map.eachLayer((layer) => {
        if (layer instanceof L.FeatureGroup) {
            map.removeLayer(layer);
        }
    });
    const geoJsonLayer = L.geoJSON(datajson.value).addTo(map);
    const bounds = geoJsonLayer.getBounds();
    map.fitBounds(bounds);
}

async function updateAlpage() {
    try {
        const response = await fetch(`${config.API_BASE_URL}/api/quartierUP//${route.params.id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(selectedFeature.value)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        alert('Quartier mis à jour avec succès!');
        isEditing.value = false;
        map.removeLayer(editableLayers);
    } catch (error) {
        console.error('Error updating GeoJSON:', error);
        alert('Erreur lors de la mise à jour du quartier.');
    }
}

async function deleteAlpage() {
    try {
        const response = await fetch(`${config.API_BASE_URL}/api/quartierUP/${route.params.id}/`, {
            method: 'DELETE',
            // headers: {
            //     'Content-Type': 'application/json',
            // },
            // body: JSON.stringify(selectedFeature.value)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        alert('Quartier supprimé avec succès.');
        router.push('/mapview');
    } catch (error) {
        console.error('Error deleting GeoJSON:', error);
        alert('Erreur lors de la suppression du quartier.');
    }
}



function confirmDelete() {
    showDeleteModal.value = true;
}

function closeDeleteModal() {
    showDeleteModal.value = false;
}

onMounted(async () => {
    try {
        map = L.map("map", {
            // center: [45.4, 7.0],
            // zoom: 11,
            // center: window.config.leaflet_centrage_initial,
            // zoom: window.config.leaflet_zoom_initial,
            zoomControl: false,
            zoomAnimation: true,
            layers: [osmplan]
        });

        // Gestionnaire de couches, outil zoom et échelle
        L.control.layers(baseMaps).addTo(map);
        L.control.zoom({ position: 'topright' }).addTo(map);
        L.control.scale({ imperial: false, position: 'bottomright' }).addTo(map);

        datajson.value = await fetchGeoJSON();

        quartier_nom.value = datajson.value.properties.quartier_nom;
        selectedFeature.value = datajson.value;

        if (datajson.value) {
            const geojsonLayer = L.geoJSON(datajson.value, {
                // style: style,
                // onEachFeature: onEachFeature
            }).addTo(map);

            const bounds = geojsonLayer.getBounds();
            map.fitBounds(bounds);
        }

    } catch (error) {
        console.log("Erreur lors de l'initialisation de la carte : ", error);
    }
});
</script>

<style>
/* Styles pour la modale */
.modal {
    display: block;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgb(0, 0, 0);
    background-color: rgba(0, 0, 0, 0.4);
    padding-top: 60px;
}

.modal-content {
    background-color: #fefefe;
    margin: 5% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
}

.close:hover,
.close:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
}

.container .row {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.container .col-25 {
    flex: 25%;
    padding-right: 10px;
}

.container .col-75 {
    flex: 75%;
}

.container input[type="text"],
.container textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    resize: vertical;
}

.container input[type="submit"],
.container button {
    background-color: #4CAF50;
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.container button {
    margin-right: 10px;
}

.container input[type="submit"]:hover,
.container button:hover {
    background-color: #45a049;
}

hr {
    margin: 20px 0;
}
</style>
