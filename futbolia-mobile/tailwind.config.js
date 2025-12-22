/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // Primary - Neon Green
        primary: {
          DEFAULT: "#00ff9d",
          50: "#e6fff5",
          100: "#b3ffe0",
          200: "#80ffcc",
          300: "#4dffb8",
          400: "#1affa3",
          500: "#00ff9d",
          600: "#00cc7e",
          700: "#00995e",
          800: "#00663f",
          900: "#00331f",
        },
        // Dark theme colors
        dark: {
          bg: "#0a0f0d",
          card: "#141a17",
          surface: "#1a2320",
          border: "#2d3833",
        },
        // Light theme colors
        light: {
          bg: "#f8faf9",
          card: "#ffffff",
          surface: "#f0f5f3",
          border: "#e5e8e6",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
