import axios from 'axios';
import config from '../../config';

const API_URL = `${config.API_BASE_URL}/api`;

const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

function getAccessToken() {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.access || null;
}

function getRefreshToken() {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.refresh || null;
}

function setAccessToken(newAccessToken) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
        user.access = newAccessToken;
        localStorage.setItem('user', JSON.stringify(user));
    }
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = '/login';
}

async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) return null;

    try {
        const response = await axios.post(`${API_URL}/token/refresh/`, { refresh });
        const newAccess = response.data.access;
        setAccessToken(newAccess);
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${newAccess}`;
        return newAccess;
    } catch (error) {
        console.error('Erreur lors du rafraîchissement du token :', error);
        logout();
        return null;
    }
}

axiosInstance.interceptors.request.use(
    (cfg) => {
        const token = getAccessToken();
        if (token) {
            cfg.headers.Authorization = `Bearer ${token}`;
        }
        return cfg;
    },
    (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            getRefreshToken()
        ) {
            originalRequest._retry = true;
            const newAccessToken = await refreshAccessToken();
            if (newAccessToken) {
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
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
