/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}", // Premium UI components
  ],
  // Safelist: Protect critical custom classes from being purged
  safelist: [
    'glass-card',
    'glass-pill',
    'primary-btn',
    'input-glass',
    'gradient-dark-glass',
    'glass-divider',
    'hover-reflect',
    'skeleton-glass',
    'text-gold-primary',
    'text-white/80',
    'text-white/70',
    'text-white/60',
    'bg-gradient-to-r',
    'from-gold-primary',
    'to-gold-accent',
    'hover:from-gold-accent',
    'hover:to-gold-hover',
  ],
  darkMode: 'class', // Enable dark mode via class
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",

        // Liquid Glass Design System - Ink Colors (main palette)
        ink: {
          900: '#0a0a0f',    // Almost black
          800: '#1a1a2e',    // Deep navy
          700: '#2d2d44',    // Dark slate
          600: '#4a4a66',    // Medium slate
          500: '#6b6b88',    // Light slate
          400: '#9090aa',    // Muted purple-gray
          300: '#b5b5cc',    // Light gray-purple
          200: '#d4d4e4',    // Very light gray
          100: '#ebebf5',    // Near white
        },

        // Liquid Glass Design System - Glass Effect Colors
        glass: {
          white: 'rgba(255, 255, 255, 0.03)',  // Subtle white glass
          edge: 'rgba(255, 255, 255, 0.15)',   // Edge highlight
          line: 'rgba(255, 255, 255, 0.1)',    // Border line
        },

        // Liquid Glass Design System - Accent Colors
        accent: {
          500: '#8b5cf6',    // Vibrant purple
          400: '#a78bfa',    // Light purple
        },

        // Premium Design System - Primary Colors (iOS-style)
        primary: {
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          200: 'var(--color-primary-200)',
          300: 'var(--color-primary-300)',
          400: 'var(--color-primary-400)',
          500: '#007AFF',  // iOS Blue
          600: '#0051D5',  // iOS Blue Dark
          700: 'var(--color-primary-700)',
          800: 'var(--color-primary-800)',
          900: 'var(--color-primary-900)',
          950: 'var(--color-primary-950)',
        },

        // Premium Design System - Secondary Colors
        secondary: {
          50: 'var(--color-secondary-50)',
          100: 'var(--color-secondary-100)',
          200: 'var(--color-secondary-200)',
          300: 'var(--color-secondary-300)',
          400: 'var(--color-secondary-400)',
          500: 'var(--color-secondary-500)',
          600: 'var(--color-secondary-600)',
          700: 'var(--color-secondary-700)',
          800: 'var(--color-secondary-800)',
          900: 'var(--color-secondary-900)',
        },

        // Premium Design System - Gray Scale
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

        // Premium Design System - Accent Colors
        accent: {
          cyan: 'var(--color-accent-cyan)',
          teal: 'var(--color-accent-teal)',
          emerald: 'var(--color-accent-emerald)',
          amber: 'var(--color-accent-amber)',
          rose: 'var(--color-accent-rose)',
        },

        // Premium Design System - Semantic Colors (iOS-style)
        success: {
          500: '#34C759',  // iOS Green
          DEFAULT: '#34C759',
        },
        warning: {
          500: '#FF9500',  // iOS Orange
          DEFAULT: '#FF9500',
        },
        danger: {
          500: '#FF3B30',  // iOS Red
          DEFAULT: '#FF3B30',
        },
        error: 'var(--color-error)',
        info: 'var(--color-info)',

        // Premium Design System - Premium Gold
        premium: {
          gold: 'var(--color-premium-gold)',
          'gold-light': 'var(--color-premium-gold-light)',
          'gold-dark': 'var(--color-premium-gold-dark)',
        },

        // NEXT Royal Prestige Palette - Official Brand Colors (Legacy)
        'royal': {
          'blue': '#1150A3',
          'blue-deep': '#103D86',
          'blue-gradient-start': '#1150A3',
          'blue-gradient-end': '#0B2C6B',
          'navy': '#0A1F5A',
        },
        'gold': {
          'primary': '#E5B73B',
          'accent': '#D49F25',
          'hover': '#F5D264',
        },
        'silver': {
          'light': '#E6E6E6',
          'dark': '#A7A7A7',
          'soft': '#D9D9D9',
        },
        'supporting': {
          'charcoal': '#121212',
          'steel-blue': '#1E3F73',
        },
        // Legacy NEXT colors (for backward compatibility)
        'next-deep-blue': '#0B1D45',
        'next-royal-blue': '#1E3C78',
        'next-gold': '#CBA135',
        'next-gold-light': '#E5C158',
        'next-bg-light': '#F4F6F8',
        'next-bg-dark': '#081835',
        'next-text-muted': '#B0B6C1',
      },
      // Premium Design System - Spacing
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

      // Premium Design System - Typography
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
        'sans': 'var(--font-sans)',
        'display': 'var(--font-display)',
        'mono': 'var(--font-mono)',
        // Legacy fonts (backward compatibility)
        'heading': ['Poppins', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
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
        // Premium Design System - Gradients
        'gradient-primary': 'var(--gradient-primary)',
        'gradient-primary-intense': 'var(--gradient-primary-intense)',
        'gradient-primary-subtle': 'var(--gradient-primary-subtle)',
        'gradient-royal': 'var(--gradient-royal)',
        'gradient-sunset': 'var(--gradient-sunset)',
        'gradient-ocean': 'var(--gradient-ocean)',
        'gradient-forest': 'var(--gradient-forest)',
        'gradient-premium': 'var(--gradient-premium)',
        'gradient-premium-dark': 'var(--gradient-premium-dark)',
        'gradient-dark-subtle': 'var(--gradient-dark-subtle)',
        // Legacy gradients (backward compatibility)
        'gradient-next': 'linear-gradient(135deg, #1E3C78, #0B1D45)',
        'gradient-next-gold': 'linear-gradient(135deg, #CBA135, #E5C158)',
        'gradient-next-hero': 'linear-gradient(180deg, #0B1D45 0%, #1E3C78 100%)',
        'gradient-gold': 'linear-gradient(135deg, #E5B73B, #D49F25)',
        'gradient-silver': 'linear-gradient(135deg, #E6E6E6, #A7A7A7)',
        'gradient-gold-hover': 'linear-gradient(135deg, #E5B73B, #F5D264)',
      },

      boxShadow: {
        // Premium Design System - Shadows
        sm: 'var(--shadow-sm)',
        base: 'var(--shadow-base)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
        '2xl': 'var(--shadow-2xl)',
        inner: 'var(--shadow-inner)',
        premium: 'var(--shadow-premium)',
        primary: 'var(--shadow-primary)',
        // Liquid Glass Design System - Glass Shadows
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.15)',
        'glass-md': '0 8px 32px rgba(0, 0, 0, 0.2)',
        'glass-lg': '0 12px 48px rgba(0, 0, 0, 0.25)',
        'glass-xl': '0 20px 64px rgba(0, 0, 0, 0.3)',
        // Legacy shadows (backward compatibility)
        'next-sm': '0 2px 4px rgba(11, 29, 69, 0.1)',
        'next-md': '0 4px 6px rgba(11, 29, 69, 0.15)',
        'next-lg': '0 10px 15px rgba(11, 29, 69, 0.2)',
        'next-xl': '0 20px 25px rgba(11, 29, 69, 0.25)',
        'next-gold': '0 4px 20px rgba(203, 161, 53, 0.3)',
        'focus-royal': '0 0 0 3px rgba(17, 80, 163, 0.5)',
        'focus-gold': '0 0 0 3px rgba(229, 183, 59, 0.5)',
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
        // Premium Design System - Animations
        shimmer: 'shimmer 2s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        // Legacy animations (backward compatibility)
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-gold': 'pulse-gold 2s ease-in-out infinite',
        'rotate-slow': 'rotate-slow 3s linear infinite',
        'swoosh': 'swoosh-slide 1.2s ease-out forwards',
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
          '0%, 100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(99, 102, 241, 0.6)' },
        },
      },

      // Premium Design System - Containers
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
