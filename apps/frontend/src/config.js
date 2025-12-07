// This file centralizes the backend API URL for easy configuration.

// Folosește variabila de mediu injectată de Vite la build, cu un fallback pentru dezvoltare locală.
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default API_URL;