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

fetch(`${API_URL}/chat`, {
  method: "POST",
  body: JSON.stringify(data),
});
