// Configuration de l'API
// En développement, utilise le proxy Vite (/api)
// En production, utilise l'URL complète depuis les variables d'environnement
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export { API_BASE_URL };