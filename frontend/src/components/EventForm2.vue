<template>
  <div class="event-form-modal">
    <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

    <form @submit.prevent="submitForm">
        <div class="w3-row form-ligne">
            <div class="w3-quarter form-cell">
              <label for="id_evenement">ID</label>
              <input id="id_evenement" type="number" v-model.number="form.id_evenement" :readonly="autoId" :disabled="props.mode === 'view'" />
              <label>
                <input
                  type="checkbox"
                  v-model="autoId"
                  :disabled="props.mode === 'view' || !can('change')"
                /> auto
              </label>
            </div>
            <div class="w3-quarter form-cell">
              <label>Date de l'événement</label>
              <input
                type="date"
                v-model="form.date_evenement"
                required
                :disabled="props.mode === 'view' || !can('change')"
              />
            </div>
            <div class="w3-quarter form-cell">
              <label>Date d'observation</label>
              <input
                type="date"
                v-model="form.date_observation"
                required
                :disabled="props.mode === 'view' || !can('change')"
              />
            </div>
            <div class="w3-quarter form-cell">
                <label>Observateur</label>
                <input
                  type="text"
                  v-model="form.observateur"
                  required
                  :disabled="props.mode === 'view' || !can('change')"
                />
            </div>
        </div>

        <div class="w3-row form-ligne">
            <div class="w3-quarter form-cell">
                <label>Source</label>
                <input
                  type="text"
                  v-model="form.source"
                  :disabled="props.mode === 'view' || !can('change')"
                />
            </div>
            <div class="w3-quarter form-cell">
                <label>Unité pastorale</label>
                <select
                  v-model.number="form.unite_pastorale" 
                  :disabled="props.mode === 'view' || !can('change')"
                >
                  <option :value="null">-- Choisir --</option>
                  <option v-for="u in ups" :key="u.id_unite_pastorale" :value="u.id_unite_pastorale">{{ u.nom_up }} - {{ u.secteur }}</option>
                </select>
                <label>Type d'événement</label>
                <select
                  v-model.number="form.type_evenement" 
                  :disabled="props.mode === 'view' || !can('change')"
                >
                  <option :value="null">-- Choisir --</option>
                  <option v-for="t in types" :key="t.id_type_evenement" :value="t.id_type_evenement">{{ t.description }}</option>
                </select>
            </div>
            <div class="w3-quarter form-cell">
                <label>Description</label>
                <textarea
                  v-model="form.description" 
                  :disabled="props.mode === 'view' || !can('change')"
                ></textarea>
            </div>
            <div class="w3-quarter form-cell">
                <label>Type géométrie</label>
              <select
                v-model="geometryType"
                :disabled="props.mode === 'view' || !can('change')"
              >
                <option value="Point">Point</option>
                <option value="LineString">Ligne</option>
                <option value="Polygon">Polygone</option>
              </select>
            </div>
            <div class="w3-quarter form-cell">
                <label>Type sélectionné:</label>
                <div><strong>{{ geometryType || 'aucune' }}</strong></div>
            </div>
        </div>
      <div v-if="props.mode !== 'view'" class="w3-row form-ligne">
          <small>Choisir le type avant de dessiner. Cliquez sur &quot;Éditer&quot; pour dessiner.</small>
      </div>

      <div>
        <label>Géométrie</label>
        <MapEditMultipolygon2 v-model="form.geometry" :geometryType="geometryType" 
          :disabled="props.mode === 'view' || !can('change')" />
      </div>

      <div class="form-actions" style="margin-top:10px;display:flex;gap:8px;">
        <button type="button" class="btn btn-secondary" @click="closeModal">Retour</button>
        <button v-if="props.mode !== 'view'" type="submit" class="btn btn-primary">{{ btTitle }}</button>
      </div>
    </form>
  </div>
</template>
<script setup>
import { reactive, watch, ref, computed, onMounted } from 'vue'
import auth from '../../auth'
import config from '../../config'
import MapEditMultipolygon2 from './MapEditMultipolygon2.vue'
import { usePermissions } from '../composables/usePermissions'

const props = defineProps({
  initialForm: { type: Object, default: () => ({}) },
  mode: { type: String, default: 'view' }, // add | change | view
  itemLabel: { type: String, required: true },
  onSubmit: Function,
  onClose: Function,
})

const { can } = usePermissions('evenement')

const formTitle = computed(() => {
  if (props.mode === 'add') return `Ajouter ${props.itemLabel}`
  if (props.mode === 'change') return `Modifier ${props.itemLabel}`
  if (props.mode === 'view') return `Voir les détails d'${props.itemLabel}`
  return ''
})

const btTitle = computed(() => {
  if (props.mode === 'add') return 'Ajouter'
  if (props.mode === 'change') return 'Enregistrer'
  return ''
})

// Formulaire réactif
const form = reactive({
  id_evenement: null,
  date_evenement: '',
  observateur: '',
  date_observation: '',
  source: '',
  description: '',
  geometry: null,
  unite_pastorale: null,
  type_evenement: null,
})

const geometryType = ref('Point')

watch(
  () => props.initialForm,
  (newVal) => {
    if (newVal) {
      // prefer updating form.geometry from newVal.geometry if present
      Object.assign(form, newVal)
      const t = newVal.geometry?.type || newVal.type
      if (t) geometryType.value = t
      if (newVal.geometry) form.geometry = newVal.geometry
      // ensure geometry shape exists
      if (!form.geometry) form.geometry = { type: geometryType.value, coordinates: [] }
    }
  },
  { immediate: true }
)

// When geometry type changes, reset form.geometry to matching type (empty coords)
watch(
  () => geometryType.value,
  (newType, oldType) => {
    if (!newType) return
    // If current geometry is absent or type differs, reset coordinates for drawing
    if (!form.geometry || form.geometry.type !== newType) {
      form.geometry = { type: newType, coordinates: [] }
    }
  }
)

// Next ID
const nextId = ref(null)
const autoId = ref(true)

const types = ref([])
const ups = ref([])

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

const fetchNextId = async () => {
  try {
    const res = await auth.axiosInstance.get(`${config.API_BASE_URL}/api/evenement/getNextId/`)
    nextId.value = res.data.next_id
    if (autoId.value) form.id_evenement = nextId.value
  } catch (err) {
    console.error('Erreur fetch next id evenement', err)
  }
}

onMounted(() => {
  fetchTypes()
  fetchUps()
  if (props.mode === 'add') fetchNextId()
})

// Submit
const submitForm = () => {
  // Normalize geometry
  if (form.geometry && Array.isArray(form.geometry.coordinates)) {
    const coords = form.geometry.coordinates
    if (form.geometry.type === 'Point' && coords.length === 0) {
      form.geometry = null
    }
  }

  if (props.onSubmit) {
    return props.onSubmit({ ...form })
      .then(() => console.log('Form submitted OK'))
      .catch(err => console.error(err))
  }
  return Promise.resolve()
}

// Close
const closeModal = () => {
  props.onClose?.()
}
</script>

<style scoped>
.event-form-modal { padding: 12px }
.event-form-modal label { display: block; margin-top: 6px }
</style>

