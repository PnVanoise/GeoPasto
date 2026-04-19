<template>
  <Teleport to="body">
    <div v-if="isShown" class="modal-overlay" @click.self="handleOverlayClick">
      <div class="modal-content">
        <button class="modal-close" @click="close">x</button>
        <slot></slot>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, unref } from 'vue'

const props = defineProps({
  show: [Boolean, Object],
  closeOnOverlay: { type: Boolean, default: false }
});
const emit = defineEmits(["update:show", "close"]);

// Support cases where `show` is passed as a ref (unwrapped) or as a boolean
const isShown = computed(() => unref(props.show));

const close = () => {
  // standard v-model update
  emit("update:show", false);
  // also emit a semantic close event
  emit("close");
};

const handleOverlayClick = () => {
  if (props.closeOnOverlay) close();
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  min-width: 400px;
  max-width: 90%;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

:global(.eqpt-select-menu-overlay) {
  z-index: 2600 !important;
}
</style>
