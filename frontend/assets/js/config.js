/**
 * Funeraria Rancier — Configuración de entorno (producción)
 * Este archivo se carga ANTES que api.js en producción.
 * En desarrollo (localhost/127.0.0.1) api.js usa http://127.0.0.1:8000 directamente.
 */
window.APP_CONFIG = {
  apiUrl: "https://api.funerariarancier.com", // URL del backend en producción
};
