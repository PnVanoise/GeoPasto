import axios from "axios";
import config from "./config";

// 🔧 URL de base de ton API Django
const API_URL = `${config.API_BASE_URL}/api`;

// 🧠 Instance Axios partagée
const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// 🔐 Récupère le token d’accès depuis le localStorage
function getAccessToken() {
    const user = JSON.parse(localStorage.getItem("user"));
    return user?.access || null;
}

// 🔐 Récupère le token de refresh depuis le localStorage
function getRefreshToken() {
    const user = JSON.parse(localStorage.getItem("user"));
    return user?.refresh || null;
}

// 💾 Met à jour le token d’accès dans le localStorage
function setAccessToken(newAccessToken) {
    const user = JSON.parse(localStorage.getItem("user"));
    if (user) {
        user.access = newAccessToken;
        localStorage.setItem("user", JSON.stringify(user));
    }
}

// 🔁 Rafraîchit le token d’accès expiré
async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) {
        console.warn("Aucun token de rafraîchissement disponible");
        return null;
    }

    try {
        const response = await axios.post(`${API_URL}/token/refresh/`, {
            refresh: refresh,
        });

        const newAccess = response.data.access;
        setAccessToken(newAccess);
        axiosInstance.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;
        return newAccess;
    } catch (error) {
        console.error("Erreur lors du rafraîchissement du token :", error);
        logout();
        return null;
    }
}

// 🚪 Déconnexion
function logout() {
    localStorage.removeItem("user");
    window.location.href = "/login";
}

// 🧩 Intercepteur Axios pour gérer le token automatiquement
axiosInstance.interceptors.request.use(
    async (config) => {
        const token = getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Si le token est expiré → on tente un refresh une seule fois
        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            getRefreshToken()
        ) {
            originalRequest._retry = true;
            const newAccessToken = await refreshAccessToken();
            if (newAccessToken) {
                originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
                return axiosInstance(originalRequest);
            }
        }

        return Promise.reject(error);
    }
);

export default {
    axiosInstance,
    getAccessToken,
    getRefreshToken,
    refreshAccessToken,
    logout,
};
