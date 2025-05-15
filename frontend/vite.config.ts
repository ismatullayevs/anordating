import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd());

  return defineConfig({
    plugins: [tailwindcss(), sveltekit()],
    server: {
      allowedHosts: [env.VITE_DOMAIN],
    },
  });
};
