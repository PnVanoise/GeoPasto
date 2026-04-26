<template>
  <div class="event-form">
    <h2>Créer un événement</h2>

    <form @submit.prevent="submitEvent">
      <div>
        <label>Date de l'événement</label>
        <input type="date" v-model="form.date_evenement" required />
      </div>

      <div>
        <label>Observateur</label>
        <input type="text" v-model="form.observateur" required />
      </div>

      <div>
        <label>Date d'observation</label>
        <input type="date" v-model="form.date_observation" required />
      </div>

      <div>
        <label>Source</label>
        <input type="text" v-model="form.source" />
      </div>

      <div>
        <label>Type d'événement</label>
        <select v-model.number="form.type_evenement">
          <option :value="null">-- Choisir --</option>
          <option v-for="t in types" :key="t.id_type_evenement" :value="t.id_type_evenement">{{ t.description }}</option>
        </select>
      </div>

      <div>
        <label>Unité pastorale</label>
        <select v-model.number="form.unite_pastorale">
          <option :value="null">-- Choisir --</option>
          <option v-for="u in ups" :key="u.id_unite_pastorale" :value="u.id_unite_pastorale">{{ u.nom_up }} - {{ u.secteur }}</option>
        </select>
      </div>

      <div>
        <label>Description</label>
        <textarea v-model="form.description"></textarea>
      </div>

      <div>
        <label>Géométrie (dessiner sur la carte)</label>
        <div id="map" style="height: 400px; margin-bottom: 8px;"></div>
        <div>Type sélectionné: <strong>{{ geometryType || 'aucune' }}</strong></div>
        <button type="button" @click="clearGeometry">Effacer la géométrie</button>
      </div>

      <div style="margin-top:12px;">
        <button type="submit">Créer</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'
import 'leaflet-draw'
import auth from '../../auth'
import config from '../../config'

const form = ref({
  date_evenement: '',
  observateur: '',
  date_observation: '',
  source: '',
  description: '',
  geometry: null,
  unite_pastorale: null,
  type_evenement: null,
})

const types = ref([])
const ups = ref([])
const map = ref(null)
const drawControl = ref(null)
const drawnLayer = ref(null)
const geometryType = ref(null)

const fetchTypes = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/typeEvenement/`)
    types.value = res.data
  } catch (err) {
    console.error('Erreur fetch types', err)
  }
}

const fetchUps = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/unitePastorale/light/`)
    ups.value = res.data
  } catch (err) {
    console.error('Erreur fetch UP', err)
  }
}

const initMap = () => {
  map.value = L.map('map').setView([45.0, 6.0], 8)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OSM'
  }).addTo(map.value)

  const editableLayers = new L.FeatureGroup()
  map.value.addLayer(editableLayers)

  drawControl.value = new L.Control.Draw({
    edit: { featureGroup: editableLayers, remove: true },
    draw: {
      polygon: true,
      polyline: true,
      rectangle: false,
      circle: false,
      circlemarker: false,
      marker: true
    }
  })

  map.value.addControl(drawControl.value)

  map.value.on(L.Draw.Event.CREATED, function (e) {
    const layer = e.layer
    // supprimer ancienne couche
    editableLayers.clearLayers()
    editableLayers.addLayer(layer)
    drawnLayer.value = layer
    const geo = layer.toGeoJSON().geometry
    geometryType.value = geo.type
    form.value.geometry = geo
  })

  map.value.on('draw:deleted', function () {
    clearGeometry()
  })
}

const clearGeometry = () => {
  if (map.value) {
    map.value.eachLayer(layer => {
      // ne pas supprimer la couche tile
    })
  }
  form.value.geometry = null
  geometryType.value = null
  if (map.value) {
    // vider featuregroup
    map.value.eachLayer(l => {
      if (l instanceof L.FeatureGroup) {
        l.clearLayers()
      }
    })
  }
}

const submitEvent = async () => {
  try {
    const payload = {
      date_evenement: form.value.date_evenement || null,
      observateur: form.value.observateur || '',
      date_observation: form.value.date_observation || null,
      source: form.value.source || '',
      description: form.value.description || '',
      geometry: form.value.geometry,
      unite_pastorale: form.value.unite_pastorale || null,
      type_evenement: form.value.type_evenement || null,
    }

    const res = await auth.axiosInstance.post(`${config.API_BASE_URL}/api/evenement/`, payload)
    alert('Événement créé (id: ' + (res.data.id_evenement || res.data.id) + ')')
    form.value = { date_evenement:'', observateur:'', date_observation:'', source:'', description:'', geometry:null, unite_pastorale:null, type_evenement:null }
    clearGeometry()
  } catch (err) {
    console.error('Erreur création événement', err)
    alert('Erreur création événement')
  }
}

onMounted(() => {
  fetchTypes()
  fetchUps()
  initMap()
})
</script>

<style scoped>
/* basic spacing */
.event-form > form > div { margin-bottom: 8px }
#map { border: 1px solid #ccc }
</style>
