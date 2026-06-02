import frappeUIPreset from "frappe-ui/tailwind"
import colors from "tailwindcss/colors"

export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				sky: colors.sky,
				gray: colors.gray,
			},
		},
	},
	plugins: [],
}
