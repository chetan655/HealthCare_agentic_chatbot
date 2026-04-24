// import { defineConfig, loadEnv } from "vite";
// import react from "@vitejs/plugin-react";
// import tailwindcss from "@tailwindcss/vite";

// export default defineConfig(({ mode }) => {
//   const env = loadEnv(mode, process.cwd(), "");

//   return {
//     plugins: [react(), tailwindcss()],
//     server: {
//       proxy: {
//         "/chat": {
//           target: env.VITE_API_URL,
//           changeOrigin: true,
//         },
//       },
//     },
//   };
// });

const API_URL = import.meta.env.VITE_API_URL;

const BASE_URL = import.meta.env.DEV
  ? "/chat" // uses Vite proxy in dev (if you add it back)
  : API_URL;

fetch(`${BASE_URL}/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(data),
});
