/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  safelist: [
    'glass-card',
    'glass-pill',
    'primary-btn',
    'input-glass',
    'gradient-dark-glass',
    'glass-divider',
    'hover-reflect',
    'skeleton-glass',
    'text-nci-white',
    'text-white/80',
    'text-white/70',
    'text-white/60',
    'bg-gradient-to-r',
    'shadow-glass-sm',
    'shadow-glass-md',
    'shadow-glass-lg',
    'shadow-glass-xl',
    'transition-all',
    'duration-300',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",

        // New Design System - Core Palette
        nci: {
          bg: '#0F1115',
          surface: '#1A1D21',
          'surface-hover': '#22252B',
          primary: '#2D7FF9',
          'primary-dim': 'rgba(45,127,249,0.12)',
          accent: '#00D2B6',
          'accent-dim': 'rgba(0,210,182,0.12)',
          amber: '#FFB547',
          'amber-dim': 'rgba(255,181,71,0.10)',
          red: '#FF4D6A',
          'red-dim': 'rgba(255,77,106,0.10)',
          white: '#F0F1F5',
          border: 'rgba(255,255,255,0.07)',
          'border-hover': 'rgba(255,255,255,0.14)',
          glass: 'rgba(26,29,33,0.55)',
        },

        // Gray scale
        g: {
          300: '#C0C2CC',
          400: '#8B8DA0',
          500: '#6B6D80',
          600: '#4A4C5E',
          700: '#33354A',
        },

        // Primary Brand Colors
        primary: {
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          200: 'var(--color-primary-200)',
          300: 'var(--color-primary-300)',
          400: 'var(--color-primary-400)',
          500: '#2D7FF9',
          600: '#2466c7',
          700: 'var(--color-primary-700)',
          800: 'var(--color-primary-800)',
          900: 'var(--color-primary-900)',
          950: 'var(--color-primary-950)',
        },

        // Secondary Colors
        secondary: {
          50: 'var(--color-secondary-50)',
          100: 'var(--color-secondary-100)',
          200: 'var(--color-secondary-200)',
          300: 'var(--color-secondary-300)',
          400: 'var(--color-secondary-400)',
          500: '#00D2B6',
          600: 'var(--color-secondary-600)',
          700: 'var(--color-secondary-700)',
          800: 'var(--color-secondary-800)',
          900: 'var(--color-secondary-900)',
        },

        // Gray Scale
        gray: {
          50: 'var(--color-gray-50)',
          100: 'var(--color-gray-100)',
          200: 'var(--color-gray-200)',
          300: 'var(--color-gray-300)',
          400: 'var(--color-gray-400)',
          500: 'var(--color-gray-500)',
          600: 'var(--color-gray-600)',
          700: 'var(--color-gray-700)',
          800: 'var(--color-gray-800)',
          900: 'var(--color-gray-900)',
          950: 'var(--color-gray-950)',
        },

        // Accent Colors
        accent: {
          500: '#00D2B6',
          400: '#33d7b7',
          cyan: 'var(--color-accent-cyan)',
          teal: '#00D2B6',
          emerald: 'var(--color-accent-emerald)',
          amber: '#FFB547',
          rose: '#FF4D6A',
        },

        // Semantic Colors
        success: {
          500: '#00D2B6',
          DEFAULT: '#00D2B6',
        },
        warning: {
          500: '#FFB547',
          DEFAULT: '#FFB547',
        },
        danger: {
          500: '#FF4D6A',
          DEFAULT: '#FF4D6A',
        },
        error: 'var(--color-error)',
        info: 'var(--color-info)',

        // Premium
        premium: {
          gold: '#FFB547',
          'gold-light': 'rgba(255,181,71,0.10)',
          'gold-dark': '#e6a23f',
        },

        // Legacy colors preserved for backward compatibility
        'gold': {
          'primary': '#FFB547',
          'accent': '#e6a23f',
          'hover': '#ffc76a',
        },
        'royal': {
          'blue': '#2D7FF9',
          'navy': '#0F1115',
        },
        'silver': {
          'light': '#C0C2CC',
          'dark': '#8B8DA0',
          'soft': '#6B6D80',
        },
        'supporting': {
          'charcoal': '#0F1115',
          'steel-blue': '#1A1D21',
        },

        // Glass effect colors
        glass: {
          white: 'rgba(255, 255, 255, 0.03)',
          edge: 'rgba(255, 255, 255, 0.15)',
          line: 'rgba(255, 255, 255, 0.07)',
        },

        // Ink colors
        ink: {
          900: '#0F1115',
          800: '#1A1D21',
          700: '#22252B',
          600: '#4A4C5E',
          500: '#6B6D80',
          400: '#8B8DA0',
          300: '#C0C2CC',
          200: '#F0F1F5',
          100: '#F0F1F5',
        },
      },

      spacing: {
        0: 'var(--space-0)',
        1: 'var(--space-1)',
        2: 'var(--space-2)',
        3: 'var(--space-3)',
        4: 'var(--space-4)',
        5: 'var(--space-5)',
        6: 'var(--space-6)',
        8: 'var(--space-8)',
        10: 'var(--space-10)',
        12: 'var(--space-12)',
        16: 'var(--space-16)',
        20: 'var(--space-20)',
        24: 'var(--space-24)',
        32: 'var(--space-32)',
      },

      fontSize: {
        xs: 'var(--text-xs)',
        sm: 'var(--text-sm)',
        base: 'var(--text-base)',
        lg: 'var(--text-lg)',
        xl: 'var(--text-xl)',
        '2xl': 'var(--text-2xl)',
        '3xl': 'var(--text-3xl)',
        '4xl': 'var(--text-4xl)',
        '5xl': 'var(--text-5xl)',
        '6xl': 'var(--text-6xl)',
        '7xl': 'var(--text-7xl)',
      },

      fontFamily: {
        'sans': ['Outfit', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        'serif': ['Instrument Serif', 'Georgia', 'serif'],
        'display': ['Instrument Serif', 'Georgia', 'serif'],
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'heading': ['Instrument Serif', 'Georgia', 'serif'],
        'body': ['Outfit', '-apple-system', 'sans-serif'],
      },

      fontWeight: {
        light: 'var(--font-weight-light)',
        normal: 'var(--font-weight-normal)',
        medium: 'var(--font-weight-medium)',
        semibold: 'var(--font-weight-semibold)',
        bold: 'var(--font-weight-bold)',
        extrabold: 'var(--font-weight-extrabold)',
      },

      lineHeight: {
        none: 'var(--leading-none)',
        tight: 'var(--leading-tight)',
        snug: 'var(--leading-snug)',
        normal: 'var(--leading-normal)',
        relaxed: 'var(--leading-relaxed)',
        loose: 'var(--leading-loose)',
      },

      letterSpacing: {
        tighter: 'var(--tracking-tighter)',
        tight: 'var(--tracking-tight)',
        normal: 'var(--tracking-normal)',
        wide: 'var(--tracking-wide)',
        wider: 'var(--tracking-wider)',
        widest: 'var(--tracking-widest)',
      },

      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #2D7FF9, #00D2B6)',
        'gradient-primary-intense': 'linear-gradient(135deg, #2D7FF9 0%, #00D2B6 100%)',
        'gradient-primary-subtle': 'linear-gradient(135deg, rgba(45,127,249,0.12), rgba(0,210,182,0.12))',
        'gradient-royal': 'linear-gradient(135deg, #2D7FF9 0%, #00D2B6 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #FF4D6A 0%, #FFB547 100%)',
        'gradient-ocean': 'linear-gradient(135deg, #2D7FF9 0%, #00D2B6 100%)',
        'gradient-forest': 'linear-gradient(135deg, #00D2B6 0%, #10b981 100%)',
        'gradient-premium': 'linear-gradient(135deg, #FFB547 0%, #FF4D6A 100%)',
        'gradient-premium-dark': 'linear-gradient(135deg, #FFB547 0%, #e6a23f 100%)',
        'gradient-dark-subtle': 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
        'gradient-gold': 'linear-gradient(135deg, #FFB547, #e6a23f)',
        'gradient-gold-hover': 'linear-gradient(135deg, #FFB547, #ffc76a)',
      },

      boxShadow: {
        sm: 'var(--shadow-sm)',
        base: 'var(--shadow-base)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
        '2xl': 'var(--shadow-2xl)',
        inner: 'var(--shadow-inner)',
        premium: 'var(--shadow-premium)',
        primary: 'var(--shadow-primary)',
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.25)',
        'glass-md': '0 8px 32px rgba(0, 0, 0, 0.3)',
        'glass-lg': '0 12px 48px rgba(0, 0, 0, 0.35)',
        'glass-xl': '0 20px 80px rgba(0, 0, 0, 0.5)',
        'glow-blue': '0 0 20px rgba(45,127,249,0.3)',
        'glow-accent': '0 0 20px rgba(0,210,182,0.3)',
        'glow-amber': '0 0 20px rgba(255,181,71,0.3)',
      },

      borderRadius: {
        none: 'var(--radius-none)',
        sm: 'var(--radius-sm)',
        base: 'var(--radius-base)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
        '2xl': 'var(--radius-2xl)',
        '3xl': 'var(--radius-3xl)',
        full: 'var(--radius-full)',
      },

      blur: {
        sm: 'var(--blur-sm)',
        base: 'var(--blur-base)',
        md: 'var(--blur-md)',
        lg: 'var(--blur-lg)',
        xl: 'var(--blur-xl)',
        '2xl': 'var(--blur-2xl)',
        '3xl': 'var(--blur-3xl)',
      },

      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '24px',
      },

      opacity: {
        0: 'var(--opacity-0)',
        5: 'var(--opacity-5)',
        10: 'var(--opacity-10)',
        20: 'var(--opacity-20)',
        30: 'var(--opacity-30)',
        40: 'var(--opacity-40)',
        50: 'var(--opacity-50)',
        60: 'var(--opacity-60)',
        70: 'var(--opacity-70)',
        80: 'var(--opacity-80)',
        90: 'var(--opacity-90)',
        100: 'var(--opacity-100)',
      },

      zIndex: {
        base: 'var(--z-base)',
        dropdown: 'var(--z-dropdown)',
        sticky: 'var(--z-sticky)',
        fixed: 'var(--z-fixed)',
        'modal-backdrop': 'var(--z-modal-backdrop)',
        modal: 'var(--z-modal)',
        popover: 'var(--z-popover)',
        tooltip: 'var(--z-tooltip)',
      },

      transitionDuration: {
        instant: 'var(--duration-instant)',
        fast: 'var(--duration-fast)',
        base: 'var(--duration-base)',
        slow: 'var(--duration-slow)',
        slower: 'var(--duration-slower)',
      },

      transitionTimingFunction: {
        linear: 'var(--ease-linear)',
        in: 'var(--ease-in)',
        out: 'var(--ease-out)',
        'in-out': 'var(--ease-in-out)',
        bounce: 'var(--ease-bounce)',
        premium: 'var(--ease-premium)',
      },

      outlineWidth: {
        3: '3px',
      },

      outlineOffset: {
        3: '3px',
      },

      animation: {
        shimmer: 'shimmer 2s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ticker-scroll': 'tickerScroll 25s linear infinite',
      },

      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(45, 127, 249, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(45, 127, 249, 0.6)' },
        },
        tickerScroll: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },

      maxWidth: {
        sm: 'var(--container-sm)',
        md: 'var(--container-md)',
        lg: 'var(--container-lg)',
        xl: 'var(--container-xl)',
        '2xl': 'var(--container-2xl)',
      },
    },
  },
  plugins: [],
};
