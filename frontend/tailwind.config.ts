import type { Config } from "tailwindcss";

export default {
	content: [
		"./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/components/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/features/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/app/**/*.{js,ts,jsx,tsx,mdx}",
	],
	theme: {
		extend: {
			colors: {
				background: "var(--background)",
				foreground: "var(--foreground)",
				primary: "#5c7f70",
				darkGreen: "#B2D8BB",
				lightGreen: "#73a692",
				topCardBg: "#f06e6c",
				topCardBgSecond: "#AEB71D",
				topCardTextSecond: "#627035",
				topCardBgLast: "#00927E",
			},
			letterSpacing: {
				wide: "0.04em",
			},
		},
	},
	plugins: [],
} satisfies Config;
