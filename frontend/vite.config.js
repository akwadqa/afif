import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			jinjaBootData: true,
			lucideIcons: true,
			buildConfig: {
				outDir: "../afif/public/frontend",
				indexHtmlPath: "../afif/www/frontend.html",
				emptyOutDir: true,
				sourcemap: true,
			},
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: "../afif/public/frontend",
		emptyOutDir: true,
		target: "es2015",
		sourcemap: true,
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
		},
	},
	optimizeDeps: {
		include: ["feather-icons", "highlight.js/lib/core", "interactjs"],
		exclude: ["frappe-ui"],
	},
	server: {
		proxy: {
			"/api": {
			target: "https://afif.akwad.qa/",
			changeOrigin: true,
			secure: true
			},
			"/files": {
			target: "https://afif.akwad.qa/",
			changeOrigin: true,
			secure: true
			},
		},
	},
})
