import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import legacy from '@vitejs/plugin-legacy'
import { resolve } from 'node:path'

// https://vitejs.dev/config/
export default defineConfig({
    base: '/packet_info/',
    plugins: [
        vue(),
        legacy()
    ],
    build: {
        rollupOptions: {
            input: {
                packtInfo: resolve(__dirname, 'packet_main.html')
            }
        }
    },
    server: {
        open: "/packet_info/packet_main.html",
        proxy: {
            '/nmas': {
                target: 'http://【Your_ip_addr_main】:8080/',
                changeOrigin: true,
                rewrite: (url) => url.replace(/^\/nmas/, '')
            }
        }
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
            'ws': 'isomorphic-ws'
        }
    }
})
