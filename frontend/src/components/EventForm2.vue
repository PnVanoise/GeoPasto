<template>
  <h3 class="w3-center w3-margin">{{ formTitle }}</h3>

  <form class="event-form" @submit.prevent="submitForm">
    <div class="event-layout">
      <section class="layout-card">
        <h4>Informations événement</h4>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              id="id_evenement"
              type="number"
              v-model.number="form.id_evenement"
              label="ID"
              :readonly="autoId"
              :disabled="props.mode === 'view' || autoId"
              density="compact"
              variant="outlined"
              hide-details
            />
          </div>
          <div class="w3-half form-cell">
            <v-switch
              v-model="autoId"
              label="ID auto"
              color="primary"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              hide-details
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              type="date"
              v-model="form.date_evenement"
              label="Date de l'événement"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
              required
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              type="date"
              v-model="form.date_observation"
              label="Date d'observation"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
              required
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.observateur"
              label="Observateur"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
              required
            />
          </div>
          <div class="w3-half form-cell">
            <v-text-field
              v-model="form.source"
              label="Source"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
              clearable
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              v-model="form.unite_pastorale"
              :items="ups"
              item-title="nom_up"
              item-value="id_unite_pastorale"
              label="Unité pastorale"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
              clearable
            />
          </div>
          <div class="w3-half form-cell">
            <v-select
              v-model="form.type_evenement"
              :items="types"
              item-title="description"
              item-value="id_type_evenement"
              label="Type d'événement"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
              clearable
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="form-cell">
            <v-textarea
              v-model="form.description"
              label="Description"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              rows="2"
              hide-details
              auto-grow
            />
          </div>
        </div>

        <div class="w3-row form-ligne">
          <div class="w3-half form-cell">
            <v-select
              v-model="geometryType"
              :items="geometryTypeOptions"
              label="Type géométrie"
              :disabled="props.mode === 'view' || !can('change')"
              density="compact"
              variant="outlined"
              hide-details
            />
          </div>
          <div class="w3-half form-cell selected-geom-type">
            Type sélectionné: <strong>{{ geometryType || 'aucune' }}</strong>
          </div>
        </div>

        <div v-if="props.mode !== 'view'" class="w3-row form-ligne">
          <small>Choisir le type avant de dessiner. Cliquez sur "Éditer" dans la carte pour dessiner.</small>
        </div>
      </section>

      <section class="layout-card">
        <h4>Géométrie</h4>
        <MapEditMultipolygon2
          v-model="form.geometry"
          :geometryType="geometryType"
          :disabled="props.mode === 'view' || !can('change')"
        />
      </section>
    </div>

    <div class="form-actions">
      <v-btn color="info" @click="closeModal" prepend-icon="mdi-arrow-left-circle">Retour</v-btn>
      <v-btn
        v-if="props.mode !== 'view'"
        color="success"
        type="submit"
        prepend-icon="mdi-content-save"
      >
        {{ btTitle }}
      </v-btn>
    </div>
  </form>
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
const geometryTypeOptions = ['Point', 'LineString', 'Polygon']

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
.form-ligne {
  padding: 4px;
}

.form-cell {
  padding: 4px;
}

.event-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: start;
}

.layout-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.75rem;
  background: #ffffff;
}

.layout-card h4 {
  margin: 0 0 0.6rem 0;
}

.selected-geom-type {
  display: flex;
  align-items: center;
  min-height: 38px;
  color: #334155;
  font-size: 0.88rem;
}

.event-form :deep(.v-input--density-compact .v-field__input) {
  min-height: 38px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.event-form :deep(.v-label.v-field-label) {
  font-size: 0.82rem;
}

.event-form :deep(.v-input),
.event-form :deep(.v-field__input),
.event-form :deep(.v-select__selection-text) {
  font-size: 0.88rem;
}

.form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

@media (max-width: 1100px) {
  .event-layout {
    grid-template-columns: 1fr;
  }
}
</style>

