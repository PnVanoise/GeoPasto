<template>
    <form @submit.prevent="submitForm">
        <div class="w3-row form-ligne">
            <div class="w3-half form-cell">
                <label for="nom">Nom:</label>
                <input class="w3-input w3-border" type="text" id="nom" v-model="form.nom" required>
            </div>
            <div class="w3-half form-cell">
                <label for="description">Description:</label>
                <input class="w3-input w3-border" type="text" id="description" v-model="form.description" required>
            </div>
        </div>
        <button type="submit">Enregistrer</button>
    </form>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
    initialForm: Object,
    isEdit: Boolean,
    onSubmit: Function,
});

const form = ref({ ...props.initialForm });

const submitForm = () => {
    console.log("Form submitted with:", form.value);
    props.onSubmit(form.value)
        .then(() => {
            console.log("Form submission then block executed");
        })
        .catch(error => {
            console.error('There was an error in form submission!', error);
        });
}

watch(() => props.initialForm, (newForm) => {
    form.value = { ...newForm };
}, { deep: true });

// Hooks de cycle de vie pour déboguer
onMounted(() => {
    console.log("TypeEquipementAlpageForm component mounted");
});

onBeforeUnmount(() => {
    console.log("TypeEquipementAlpageForm component before unmount");
});
</script>

<style scoped>
.form-ligne {
    padding: 8px;
}

.form-cell {
    padding: 8px;
}
</style>
