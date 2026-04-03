// src/services/axios.js
import axios from 'axios';



// Crée une instance Axios
const axiosInstance = axios.create({
    baseURL: 'http://151.80.250.138/api/',  // Remplace par l'URL de ton API
});

// Intercepteur de requêtes pour ajouter le token JWT
axiosInstance.interceptors.request.use(
    config => {
        // Récupère le token du localStorage
        const userData = localStorage.getItem('user');
        const token = userData ? JSON.parse(userData).access : null;

        // Si un token est disponible, ajoute-le au header de la requête
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// Intercepteur pour gérer les réponses
axiosInstance.interceptors.response.use(
    response => response, // Si la réponse est réussie, la retourner
    async error => {
        const originalRequest = error.config;

        // Si on reçoit un statut 401 et que ce n'est pas une tentative de renouvellement du token
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            // Renouveler le token d'accès
            const newAccessToken = await refreshAccessToken();

            if (newAccessToken) {
                // Met à jour le header de la requête originale avec le nouveau token
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                // Réessaye la requête originale
                return axiosInstance(originalRequest);
            } else {
                // Si le renouvellement du token échoue, on peut rediriger vers la page de login
                // ou déconnecter l'utilisateur
                console.error('Le token de rafraîchissement a expiré. Redirection vers la page de login.');
                // Optionnel : window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);


export default axiosInstance;

