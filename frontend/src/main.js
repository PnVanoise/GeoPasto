import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';

import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

import '@mdi/font/css/materialdesignicons.css';

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faEdit, faTrash, faEye, faSearch, faPlus } from '@fortawesome/free-solid-svg-icons';

library.add(faEdit, faTrash, faEye, faSearch, faPlus);

export default {
  components: {
    FontAwesomeIcon
  }
};

const app = createApp(App);
const pinia = createPinia();

const vuetify = createVuetify({
  components,
  directives,
});

app.use(pinia);
app.use(router);
app.use(vuetify);

app.component('font-awesome-icon', FontAwesomeIcon);

app.mount('#app');