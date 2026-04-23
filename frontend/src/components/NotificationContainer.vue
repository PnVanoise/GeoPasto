<template>
  <teleport to="#toast-root">
    <div class="notification-container">
      <div
        v-for="n in notifications"
        :key="n.id"
        class="notification"
        :class="n.type"
      >
        <span>{{ n.message }}</span>
        <button @click="remove(n.id)">×</button>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { useNotification } from "../composables/useNotification";

const { notifications, remove } = useNotification()

console.log("NotificationContainer mounted, notifications:", notifications);
</script>

<style>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;

  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification {
  min-width: 250px;
  padding: 10px 15px;
  border-radius: 6px;
  color: white;
  font-weight: bold;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);

  display: flex;
  justify-content: space-between;
  align-items: center;

  animation: slide-in 0.3s ease;
}

.notification.success {
  background: #4caf50;
}

.notification.error {
  background: #f44336;
}

.notification button {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>