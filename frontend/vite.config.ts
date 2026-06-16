import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El frontend habla con el backend FastAPI. En desarrollo se usa un proxy para
// evitar problemas de CORS; en producción se configura VITE_API_BASE.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
