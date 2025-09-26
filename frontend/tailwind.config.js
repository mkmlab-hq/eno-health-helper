/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'neon-cyan': '#00d4ff',
        'neon-sky': '#0ea5e9',
        'glass': 'rgba(17, 25, 40, 0.75)',
        'glass-dark': 'rgba(255, 255, 255, 0.08)',
        'bg-glass': 'rgba(17, 25, 40, 0.8)',
        // 기본 색상들 추가
        'gray': {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        'blue': {
          500: '#3b82f6',
          600: '#2563eb',
        },
        'cyan': {
          500: '#06b6d4',
        },
        'green': {
          500: '#22c55e',
          600: '#16a34a',
        },
        'red': {
          500: '#ef4444',
          900: '#7f1d1d',
        },
        'white': '#ffffff',
      },
      fontFamily: {
        'orbitron': ['Orbitron', 'monospace'],
        'noto': ['Noto Sans KR', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'neon-glow': 'neonGlow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        neonGlow: {
          '0%': { textShadow: '0 0 10px rgba(0, 212, 255, 0.8), 0 0 20px rgba(0, 212, 255, 0.6)' },
          '100%': { textShadow: '0 0 15px rgba(0, 212, 255, 1), 0 0 25px rgba(0, 212, 255, 0.8)' },
        },
      },
      backdropBlur: {
        'xs': '2px',
      },
      boxShadow: {
        'neon': '0 0 20px rgba(0, 212, 255, 0.5)',
        'neon-lg': '0 0 30px rgba(0, 212, 255, 0.7)',
      }
    },
  },
  plugins: [],
} 