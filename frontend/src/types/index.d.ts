// Global type definitions for the Kids Book Generator frontend

/**
 * Environment variables accessible via import.meta.env
 */
interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_CANVA_CLIENT_ID: string;
}

/**
 * Additional globals for Vite projects
 */
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
