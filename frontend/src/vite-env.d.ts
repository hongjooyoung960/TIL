/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Production/API split: absolute base URL for the FastAPI backend (no trailing slash). Omit in dev to use Vite proxy. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
