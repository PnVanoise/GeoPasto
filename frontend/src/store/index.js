// store/index.js
import { defineStore } from 'pinia';

import auth from '../../auth';

export const useMainStore = defineStore("main", {
    state: () => ({
        user: JSON.parse(localStorage.getItem("user")) || null,
        successMessage: '',
        errorMessage: '',
        username: null,
        userPermissions: {},
    }),

    getters: {
        isAuthenticated: (state) => !!state.user?.access,
    },

    actions: {
        setUser(userData) {
            this.user = userData;
            console.log("Utilisateur connecté :", this.user);
            localStorage.setItem("user", JSON.stringify(userData));
        },
        logout() {
            this.user = null;
            localStorage.removeItem("user");
        },
        setSuccessMessage(message) {
            this.successMessage = message;
            setTimeout(() => {
                this.successMessage = '';
            }, 5000); // Effacer le message après 5 secondes
        },
        setErrorMessage(message) {
            this.errorMessage = message;
            setTimeout(() => {
                this.errorMessage = '';
            }, 5000); // Effacer le message après 5 secondes
        },
        async fetchUserPermissions() {
            try {
                const response = await auth.axiosInstance.get("/userpermissions/");
                // console.log("FetchPermissions : Réponse API permissions :", response.data);
                this.username = response.data.username;
                this.userPermissions = response.data.permissions_by_model;

                // console.log("Stocké dans le store :", this);

            } catch (error) {
                console.error("Erreur lors du chargement des permissions :", error);
                // this.setErrorMessage("Impossible de charger les permissions.");
            }
        },
        hasPermission(model, actionOrFullPermission) {
            // actionOrFullPermission peut être 'add' ou 'add_abridurgence'
            if (!this.userPermissions) return false

            // si on reçoit l'action courte (add|view|change|delete)
            if (!actionOrFullPermission.includes('_')) {
                const full = `${actionOrFullPermission}_${model}`
                const perms = this.userPermissions[model] || []
                return perms.includes(full)
            }

            // si on reçoit la permission complète
            const perms = this.userPermissions[model] || []
            return perms.includes(actionOrFullPermission)
        },
    },
});
