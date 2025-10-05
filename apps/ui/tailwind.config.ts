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
        onyx: '#050505',
        silver: {
          DEFAULT: '#C0C0C0',
          light: '#D9D9D9',
          dark: '#A6A6A6',
        },
      },
      boxShadow: {
        glow: '0 0 35px rgba(192, 192, 192, 0.12)',
      },
    },
  },
  plugins: [],
};

export default config;
