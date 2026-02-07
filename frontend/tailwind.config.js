/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        critical: '#EF4444',   // Red
        high: '#F97316',       // Orange
        medium: '#EAB308',     // Yellow
        low: '#3B82F6',        // Blue
      }
    }
  },
  plugins: [],
}
