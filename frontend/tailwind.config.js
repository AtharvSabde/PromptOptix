/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Dark theme colors
        dark: {
          bg: '#0A0A0F',        // Main background
          card: '#1E1B2E',      // Card background
          cardHover: '#252233', // Card hover state
          border: '#2D2A3D',    // Subtle borders
          lighter: '#2F2B3A',   // Lighter variant
        },
        // Primary gradient colors (purple-pink)
        primary: {
          from: '#A855F7',      // Purple
          via: '#C026D3',       // Fuchsia
          to: '#EC4899',        // Pink
          light: '#D946EF',
          dark: '#9333EA',
        },
        // Accent colors
        accent: {
          cyan: '#06B6D4',      // Cyan
          blue: '#3B82F6',      // Blue
          teal: '#14B8A6',      // Teal
        },
        // Status colors (kept for defect severity)
        critical: '#EF4444',   // Red
        high: '#F97316',       // Orange
        medium: '#EAB308',     // Yellow
        low: '#10B981',        // Green (changed from blue to green for success)
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
        'gradient-text': 'linear-gradient(135deg, #06B6D4 0%, #A855F7 50%, #EC4899 100%)',
        'gradient-card': 'linear-gradient(145deg, #1E1B2E 0%, #252233 100%)',
        'gradient-radial': 'radial-gradient(circle at center, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(168, 85, 247, 0.3)',
        'glow': '0 0 20px rgba(168, 85, 247, 0.4)',
        'glow-lg': '0 0 30px rgba(168, 85, 247, 0.5)',
        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.4)',
        'glow-pink': '0 0 20px rgba(236, 72, 153, 0.4)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gradient': 'gradient 8s ease infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
