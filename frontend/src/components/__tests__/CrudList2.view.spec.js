import { render, fireEvent, screen } from '@testing-library/vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { ref, defineComponent, markRaw } from 'vue'

// Mock useCrud composable used by CrudList2
vi.mock('../../composables/useCrud', () => {
  const { ref } = require('vue')
  return {
    useCrud: (modelName, apiRouteName, idField) => {
      const items = ref([
        { id_abri_urgence_commodite: 1, abri_urgence: 1, commodite: 2, etat: 'Bon', quantite: 3 }
      ])
      const showModal = ref(false)
      const selectedItem = ref(null)
      const mode = ref('')
      const can = () => true
      const actionsFor = () => ({ add: true, view: true, edit: true, delete: true })

      const openView = (item) => {
        mode.value = 'view'
        selectedItem.value = { ...item }
        showModal.value = true
      }

      return {
        items,
        showModal,
        selectedItem,
        mode,
        can,
        actions: actionsFor(),
        fetchAll: () => {},
        createItem: async () => {},
        updateItem: async () => {},
        deleteItem: async () => {},
        openAdd: () => { mode.value = 'add'; selectedItem.value = {}; showModal.value = true },
        openEdit: (it) => { mode.value = 'change'; selectedItem.value = { ...it }; showModal.value = true },
        openView,
        closeModal: () => { showModal.value = false; selectedItem.value = null },
      }
    }
  }
})

// Stub Grid3 to emit a 'view' event when its button is clicked
vi.mock('../../components/Grid3.vue', () => {
  const { defineComponent } = require('vue')
  return {
    default: defineComponent({
      props: ['data'],
      template: `<div><button data-testid="grid-view" @click="$emit('view', data[0])">view</button></div>`
    })
  }
})

// Stub Modal to directly render slot when show is true
vi.mock('../../components/Modal.vue', () => {
  const { defineComponent } = require('vue')
  return {
    default: defineComponent({
      props: ['show'],
      template: `<div v-if="show"><slot /></div>`
    })
  }
})

// Import the component under test (after mocks)
import CrudList2 from '../../components/CrudList2.vue'

describe('CrudList2 view-only flow', () => {
  it('opens embedded form in view mode and shows fields disabled / no save / no next id', async () => {
    // Dummy child form that mirrors behavior we expect from real form
    const DummyForm = defineComponent({
      props: ['initialForm', 'mode'],
      template: `
        <div>
          <input data-testid="field-abri" :disabled="mode === 'view'" />
          <button data-testid="save" v-if="mode !== 'view'">Save</button>
          <span data-testid="nextid" v-if="mode === 'add'">Next</span>
        </div>
      `
    })

    render(CrudList2, {
      props: {
        title: 'Commodités',
        modelName: 'abridurgencecommodite',
        apiRouteName: 'abriDUrgenceCommodite',
        itemLabel: "une commodité d'abri",
        idField: 'id_abri_urgence_commodite',
        columns: [],
        formComponent: markRaw(DummyForm),
        showHeader: true,
        showSearch: false,
        showFilters: false,
        showAddButton: true,
        forceAdd: false,
      }
    })

    // Click the grid view button that our Grid3 stub renders
    const btn = await screen.findByTestId('grid-view')
    await fireEvent.click(btn)

    // After clicking, the mocked useCrud.openView sets mode='view' and showModal=true
    // The Modal stub will render the child component; assert child is rendered in view mode
    const input = await screen.findByTestId('field-abri')
    expect(input).toBeDisabled()

    // Save button should not be present
    const save = screen.queryByTestId('save')
    expect(save).toBeNull()

    // Next ID should not be present
    const next = screen.queryByTestId('nextid')
    expect(next).toBeNull()
  })
})
