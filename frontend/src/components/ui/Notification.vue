<!-- components/Notification.vue -->
<template>
    <div v-if="visible" class="notification" :class="type">
        <span>{{ message }}</span>
        <button @click="closeNotification" class="close-button">×</button>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    message: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        default: 'success', // default to success, can also be 'error'
    }
});

const emit = defineEmits(['close']);
const visible = ref(true);

const closeNotification = () => {
    visible.value = false;
    emit('close');
};
</script>

<style scoped>
.notification {
    position: relative;
    padding: 10px;
    margin-bottom: 20px;
    border-radius: 4px;
    font-weight: bold;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    width: 350px; /* Adjust as needed */
    max-width: 100%;
    background-color: #f3f4f6; /* Adjust as needed */
}

.success {
    background-color: #dff0d8;
    border: 1px solid #d6e9c6;
    color: #3c763d;
}

.error {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    padding: 0;
    line-height: 1;
}
</style>
