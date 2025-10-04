import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        neutral: {
          950: '#030712',
        },
      },
      boxShadow: {
        glow: '0 0 35px rgba(16, 185, 129, 0.15)',
      },
    },
  },
  plugins: [],
};

export default config;
