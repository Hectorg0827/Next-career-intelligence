/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // NEXT Royal Prestige Palette - Official Brand Colors
        'royal': {
          'blue': '#1150A3',           // Primary brand blue
          'blue-deep': '#103D86',      // Logo X accent
          'blue-gradient-start': '#1150A3',
          'blue-gradient-end': '#0B2C6B',
          'navy': '#0A1F5A',           // CTA button text
        },
        'gold': {
          'primary': '#E5B73B',        // Main gold accent
          'accent': '#D49F25',         // Gold streak
          'hover': '#F5D264',          // Gold hover state
        },
        'silver': {
          'light': '#E6E6E6',          // Silver gradient start
          'dark': '#A7A7A7',           // Silver gradient end
          'soft': '#D9D9D9',           // Borders/separators
        },
        'supporting': {
          'charcoal': '#121212',       // Footer/overlays
          'steel-blue': '#1E3F73',     // Background sections
        },
        // Legacy colors (for backward compatibility)
        'next-deep-blue': '#0B1D45',
        'next-royal-blue': '#1E3C78',
        'next-gold': '#CBA135',
        'next-gold-light': '#E5C158',
        'next-bg-light': '#F4F6F8',
        'next-bg-dark': '#081835',
        'next-text-muted': '#B0B6C1',
      },
      backgroundImage: {
        'gradient-next': 'linear-gradient(135deg, #1E3C78, #0B1D45)',
        'gradient-next-gold': 'linear-gradient(135deg, #CBA135, #E5C158)',
        'gradient-next-hero': 'linear-gradient(180deg, #0B1D45 0%, #1E3C78 100%)',
        // Royal Prestige Gradients
        'gradient-royal': 'linear-gradient(135deg, #1150A3, #0B2C6B)',
        'gradient-gold': 'linear-gradient(135deg, #E5B73B, #D49F25)',
        'gradient-silver': 'linear-gradient(135deg, #E6E6E6, #A7A7A7)',
        'gradient-gold-hover': 'linear-gradient(135deg, #E5B73B, #F5D264)',
      },
      boxShadow: {
        'next-sm': '0 2px 4px rgba(11, 29, 69, 0.1)',
        'next-md': '0 4px 6px rgba(11, 29, 69, 0.15)',
        'next-lg': '0 10px 15px rgba(11, 29, 69, 0.2)',
        'next-xl': '0 20px 25px rgba(11, 29, 69, 0.25)',
        'next-gold': '0 4px 20px rgba(203, 161, 53, 0.3)',
      },
      fontFamily: {
        'heading': ['Poppins', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-gold': 'pulse-gold 2s ease-in-out infinite',
        'rotate-slow': 'rotate-slow 3s linear infinite',
        'swoosh': 'swoosh-slide 1.2s ease-out forwards',
      },
    },
  },
  plugins: [],
};
