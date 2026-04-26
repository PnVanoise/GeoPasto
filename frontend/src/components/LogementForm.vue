<template>
    <div class="w3-bar w3-black">
        <button class="w3-bar-item w3-button" @click="openTab('tab1')">Onglet 1<span
                v-if="!visitedTabs.tab1">*</span></button>
        <button class="w3-bar-item w3-button" @click="openTab('tab2')">Onglet 2<span
                v-if="!visitedTabs.tab2">*</span></button>
        <button class="w3-bar-item w3-button" @click="openTab('tab3')">Onglet 3<span
                v-if="!visitedTabs.tab3">*</span></button>
    </div>
    <form @submit.prevent="submitForm">
        <!-- Champs de l'enquête SEA 73 -->
        <div id="tab1" :class="{ 'w3-show': activeTab === 'tab1', 'w3-hide': activeTab !== 'tab1' }">
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="logement_code">ID Logement:</label>
                    <input class="w3-input w3-border" v-model="form.properties.logement_code" id="logement_code"></input>
                </div>
                <div class="w3-third form-cell">
                    <label for="nom_logement">Nom:</label>
                    <input class="w3-input w3-border" v-model="form.properties.nom_logement" id="nom_logement"></input>
                </div>
                <div class="w3-third form-cell">
                    <label for="statut">Statut:</label>
                    <select class="w3-input w3-border" v-model="form.properties.statut" id="statut">
                        <option v-for="choice in choices.statut" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-half form-cell">
                    <label for="unitepastorale">Unité pastorale:</label>
                    <select
                        class="w3-input w3-border"
                        v-model="form.properties.unite_pastorale"
                        id="unitepastorale"
                    >
                        <option :value="null">-- Choisir une UP --</option>
                        <option v-for="up in ups.features" :key="up.id" :value="up.id">
                        {{ up.properties.nom_up }}
                        </option>
                    </select>
                </div>
            </div>
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="acces_final">Accès final:</label>
                    <select class="w3-input w3-border" v-model="form.properties.acces_final" id="acces_final">
                        <option v-for="choice in choices.acces_final" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="propriete">Propriété:</label>
                    <select class="w3-input w3-border" v-model="form.properties.propriete" id="propriete">
                        <option v-for="choice in choices.propriete" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="type_logement">Type de logement:</label>
                    <select class="w3-input w3-border" v-model="form.properties.type_logement" id="type_logement">
                        <option v-for="choice in choices.type_logement" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
            </div>
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="multiusage">Multiusage:</label>
                    <select class="w3-input w3-border" v-model="form.properties.multiusage" id="multiusage">
                        <option v-for="choice in choices.multiusage" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="activite_laitiere">Activité laitière (sur l'UP):</label>
                    <div class="select-container">
                        <select class="w3-input w3-border" v-model="form.properties.activite_laitiere" id="activite_laitiere">
                            <option v-for="choice in choices.activite_laitiere" :key="choice.value"
                                :value="choice.value">
                                {{ choice.display }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="w3-third form-cell">
                    <label for="etat_batiment">Etat structurel du bâtiment:</label>
                    <div class="select-container">
                        <select class="w3-input w3-border" v-model="form.properties.etat_batiment" id="etat_batiment">
                            <option v-for="choice in choices.etat_batiment" :key="choice.value" :value="choice.value">
                                {{ choice.display }}
                            </option>
                        </select>
                        <span class="tooltip-container">
                            <i class="icon">ℹ️</i>
                            <span class="tooltip-text">toit, gros oeuvre, isolation</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div id="tab2" :class="{ 'w3-show': activeTab === 'tab2', 'w3-hide': activeTab !== 'tab2' }">
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="accueil_public">Accueil public:</label>
                    <select class="w3-input w3-border" v-model="form.properties.accueil_public" id="accueil_public">
                        <option v-for="choice in choices.accueil_public" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="mixite_possible">Mixité possible:</label>
                    <select class="w3-input w3-border" v-model="form.properties.mixite_possible" id="mixite_possible">
                        <option v-for="choice in choices.mixite_possible" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="surface_logement">Surface logement:</label>
                    <div class="select-container">
                        <select class="w3-input w3-border" v-model="form.properties.surface_logement" id="surface_logement">
                            <option v-for="choice in choices.surface_logement" :key="choice.value"
                                :value="choice.value">
                                {{ choice.display }}
                            </option>
                        </select>
                        <span class="tooltip-container">
                            <i class="icon">ℹ️</i>
                            <span class="tooltip-text">Seules les surfaces habitables sont comptabilisées</span>
                        </span>
                    </div>
                </div>
            </div>
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="presence_douche">Douche:</label>
                    <select class="w3-input w3-border" v-model="form.properties.presence_douche" id="presence_douche">
                        <option v-for="choice in choices.presence_douche" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="type_wc">WC:</label>
                    <select class="w3-input w3-border" v-model="form.properties.type_wc" id="type_wc">
                        <option v-for="choice in choices.type_wc" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="alim_elec">Alimentation électrique:</label>
                    <select class="w3-input w3-border" v-model="form.properties.alim_elec" id="alim_elec">
                        <option v-for="choice in choices.alim_elec" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
            </div>
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="alim_eau">Alimentation en eau:</label>
                    <select class="w3-input w3-border" v-model="form.properties.alim_eau" id="alim_eau">
                        <option v-for="choice in choices.alim_eau" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="origine_eau">Origine eau:</label>
                    <select class="w3-input w3-border" v-model="form.properties.origine_eau" id="origine_eau">
                        <option v-for="choice in choices.origine_eau" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
            </div>
        </div>
        <div id="tab3" :class="{ 'w3-show': activeTab === 'tab3', 'w3-hide': activeTab !== 'tab3' }">
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="qualite_eau">Qualité eau:</label>
                    <select class="w3-input w3-border" v-model="form.properties.qualite_eau" id="qualite_eau">
                        <option v-for="choice in choices.qualite_eau" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="dispo_eau">Disponibilité eau:</label>
                    <select class="w3-input w3-border" v-model="form.properties.dispo_eau" id="dispo_eau">
                        <option v-for="choice in choices.dispo_eau" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="assainissement">Assainissement:</label>
                    <select class="w3-input w3-border" v-model="form.properties.assainissement" id="assainissement">
                        <option v-for="choice in choices.assainissement" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
            </div>
            <div class="w3-row form-ligne">
                <div class="w3-third form-cell">
                    <label for="chauffe_eau">Chauffe-eau:</label>
                    <select class="w3-input w3-border" v-model="form.properties.chauffe_eau" id="chauffe_eau">
                        <option v-for="choice in choices.chauffe_eau" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="chauffage">Chauffage:</label>
                    <select class="w3-input w3-border" v-model="form.properties.chauffage" id="chauffage">
                        <option v-for="choice in choices.chauffage" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
                <div class="w3-third form-cell">
                    <label for="stockage_indep">Stockage indépendant:</label>
                    <select class="w3-input w3-border" v-model="form.properties.stockage_indep" id="stockage_indep">
                        <option v-for="choice in choices.stockage_indep" :key="choice.value" :value="choice.value">
                            {{ choice.display }}
                        </option>
                    </select>
                </div>
            </div>
        </div>
        <div class="grid-container">
            <label>Commodités :</label>
            <Grid
            :data="commodites"
            :columns="commGridColumns"
            :bgColor="'#f7ba0b'"
            :columnLabels="commColumnLabels"
            @edit="commOnEdit"
            @delete="commOnDelete"
            >
            </Grid>
        </div>
        <div class="form-cell">
            <button type="button" @click="goToAddCommodite" class="w3-button w3-blue">
          Ajouter une commodité
        </button>
        </div>
        <div class="form-cell">
          Géométrie:
          <MapEditMultipolygon2
            :key="form.geometry.coordinates"
            v-model="form.geometry"
            :geometryType="'Point'"
          />
        </div>
        <button type="submit" :disabled="!allTabsVisited">Éditer</button>
    </form>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';

import auth from "../../auth";

import { useRouter } from 'vue-router';

import Grid from './Grid.vue';
import MapEditMultipolygon2 from './MapEditMultipolygon2.vue';

import config from '../../config';

const props = defineProps({
    initialForm: Object,
    isEdit: Boolean,
    onSubmit: Function,
});

const fetchCommodites = () => {
    if (!form.value.id) return;
    console.log(`${config.API_BASE_URL}/api/logementCommodite/?logementId=${form.value.id}`);
  auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/logementCommodite/?logementId=${form.value.id}`)
    .then((response) => {
      commodites.value = response.data;
      console.log("list response data:", response.data);
      console.log("commodites.value:", commodites.value);
    })
    .catch((error) => {
      console.error("There was an error!", error);
    })
    .finally(() => {
      console.log("fetchCommodites done");
    });
};

const form = ref({ ...props.initialForm });

console.log('form : ', form.value);
const choices = ref({});
const activeTab = ref('tab1');
const visitedTabs = ref({
    tab1: false,
    tab2: false,
    tab3: false
}); // Suivre les onglets visités
const router = useRouter();

const commodites = ref([]);
const commGridColumns = ref(['logement_code', 'commodite_desc', 'etat', 'quantite']);
const commColumnLabels = ref({
    logement_code: 'Logement',
    commodite_desc: 'Commodité',
    etat: 'État',
    quantite: 'Quantité',
});

const ups = ref([]);

const goToAddCommodite = () => {
  // Utilisation de l'ID de l'UP pour la navigation
  if (form.value.id) {
    console.log('form.value.id : ', form.value.id);
    router.push({ name: 'addLogementCommoditeWithLogementId', params: { logementId: form.value.id } });
  } else {
    console.warn("L'ID de l'UP n'est pas défini !");
  }
};

const fetchChoices = () => {
    auth.axiosInstance.get(`${config.API_BASE_URL}/choices_logement/`)
        .then(response => {
            choices.value = response.data; 
        })
        .catch(error => {
            console.error('There was an error !');
        });
};

const submitForm = () => {
    props.onSubmit(form.value)
        .then(() => {
            router.push('/Logements');
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
}

const openTab = (tab) => {
    activeTab.value = tab;
    visitedTabs.value[tab] = true;
};

const allTabsVisited = computed(() => {
    return Object.values(visitedTabs.value).every(visited => visited);
});

onMounted(() => {
    fetchChoices();
    openTab('tab1');
    auth.axiosInstance
    .get(`${config.API_BASE_URL}/api/unitePastorale/`)
    .then((response) => {
      ups.value = response.data;
      console.log("ups:", ups.value);
    })
    .catch((error) => {
      console.error(
        "Erreur lors de la récupération de la liste des unités pastorales",
        error
      );
    });
});

watch(() => props.initialForm, (newForm) => {
    form.value = { ...newForm };
    fetchCommodites();
}, { deep: true });

// Méthode pour gérer l'édition
function commOnEdit(entry) {
  console.log("Éditer:", entry.id_logement_commodite);
  router.push(`/LogementCommodite/edit/${entry.id_logement_commodite}`);
}

// Méthode pour gérer la suppression
function commOnDelete(entry) {
  console.log("Supprimer:", entry.id_logement_commodite);
  deleteLCommodite(entry.id_logement_commodite);
}

const deleteLCommodite = (id) => {
  auth.axiosInstance
    .delete(`${config.API_BASE_URL}/api/logementCommodite/${id}/`)
    .then((response) => {
      fetchCommodites();
      mainStore.setSuccessMessage("Logement / commodité supprimé!");
    })
    .catch((error) => {
      console.error("There was an error!", error);
    });
};

</script>

<style>
.w3-hide {
    display: none;
}

.w3-show {
    display: block;
}

.form-ligne {
    padding: 8px;
}

.form-cell {
    padding: 8px;
}


.tooltip-container {
    position: relative;
    display: inline-block;
}

.tooltip-text {
    visibility: hidden;
    width: 200px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 5px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    /* Positionne l'infobulle au-dessus de l'icône */
    left: 50%;
    margin-left: -100px;
    /* Utilisé pour centrer l'infobulle */
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip-container .tooltip-text::after {
    content: "";
    position: absolute;
    top: 100%;
    /* Positionne la flèche en bas de l'infobulle */
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: black transparent transparent transparent;
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

.icon {
    cursor: pointer;
    margin-left: 5px;
}

.select-container {
    position: relative;
    display: flex;
    align-items: center;
}
</style>