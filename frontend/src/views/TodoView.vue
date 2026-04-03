<template>
    <h3> My ToDo List {{ count }}</h3>
    <div>
        <input v-model="newItemText" v-on:keyup.enter="addNewTodo" />
        <button v-on:click="addNewTodo">Add</button>
        <button v-on:click="removeTodo">Remove</button>
        <button v-on:click="removeAllTodos">Remove All</button>
        <transition-group name="list" tag="ul">
            <li v-for="task in tasks" v-bind:key="task">{{ task }}</li>
        </transition-group>
    </div>
</template>

<!-- Composition API -->
<script>
import { ref, onMounted } from 'vue';
import useCounter from '../composables/UseCounter.js'

export default {
    setup() {
        const tasks = ref(["Rédiger des spécifications", "Etudier le modèle bâti / usage / logement", "Peaufiner l'ensemble du modèle / Retours autres parcs", "Faire un petit coup de figma"]);
        const newItemText = ref("");

        const { count, increment, decrement, set, reset } = useCounter();

        onMounted(() => set(tasks.value.length));

        function addNewTodo() {
            if (newItemText.value != "") {
                tasks.value.unshift(newItemText.value)
                increment();
            }
            newItemText.value = ""
        }

        function removeTodo() {
            tasks.value.pop();
            decrement();
        }

        function removeAllTodos() {
            tasks.value = [];
            reset();
        }

        return {
            count,
            tasks,
            newItemText,
            addNewTodo,
            removeTodo,
            removeAllTodos
        }
    }
}
</script>



<style>
button {
    margin: 5px;
}

ul {
    margin: 30px 0 0 0;
    padding: 0;
    text-align: left;
}

li {
    font-size: 1.2em;
    list-style: none;
}

.list-enter-active {
    animation: add-item 1s;
}

.list-leave-active {
    position: absolute;
    animation: add-item 1s reverse;
}

.list-move {
    transition: transform 1s;
}

@keyframes add-item {
    0% {
        opacity: 0;
        transform: translateX(150px);
    }

    50% {
        opacity: 0.5;
        transform: translateX(-10px) skewX(20deg);
    }

    100% {
        opacity: 1;
        transform: translateX(0px);
    }
}
</style>