/**
 * Framer Motion Animation Variants Library
 * Royal Prestige Design System
 */

import { Variants } from 'framer-motion';

// Page Transitions
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1], // Custom easing
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
    },
  },
};

// Staggered Children Container
export const staggerContainerVariants: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const staggerItemVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

// Button Interactions
export const buttonVariants: Variants = {
  initial: { scale: 1 },
  hover: {
    scale: 1.02,
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
  tap: {
    scale: 0.98,
    transition: {
      duration: 0.1,
      ease: 'easeIn',
    },
  },
};

export const buttonRippleVariants: Variants = {
  initial: {
    scale: 0,
    opacity: 0.5,
  },
  animate: {
    scale: 2.5,
    opacity: 0,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

// Card Interactions
export const cardVariants: Variants = {
  initial: {
    y: 0,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
  hover: {
    y: -8,
    boxShadow: '0 20px 25px -5px rgba(17, 80, 163, 0.3)',
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

export const cardScaleVariants: Variants = {
  initial: { scale: 1 },
  hover: {
    scale: 1.03,
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
};

// Icon Animations
export const iconBounceVariants: Variants = {
  initial: { scale: 1 },
  hover: {
    scale: [1, 1.2, 1],
    transition: {
      duration: 0.4,
      ease: 'easeInOut',
    },
  },
};

export const iconRotateVariants: Variants = {
  initial: { rotate: 0 },
  hover: {
    rotate: 360,
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
    },
  },
};

export const iconPulseVariants: Variants = {
  initial: { scale: 1 },
  animate: {
    scale: [1, 1.1, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Input Focus Animations
export const inputFocusVariants: Variants = {
  initial: {
    scale: 1,
    borderColor: 'rgb(229, 231, 235)', // gray-200
  },
  focus: {
    scale: 1.01,
    borderColor: 'rgb(17, 80, 163)', // royal-blue
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
};

// Modal Animations
export const modalBackdropVariants: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

export const modalContentVariants: Variants = {
  initial: {
    opacity: 0,
    scale: 0.9,
    y: 20,
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.22, 1, 0.36, 1],
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    y: 20,
    transition: {
      duration: 0.2,
    },
  },
};

// Loading Animations
export const loadingSpinnerVariants: Variants = {
  initial: { rotate: 0 },
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

export const loadingDotsVariants: Variants = {
  initial: { y: 0 },
  animate: {
    y: [-10, 0, -10],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Badge/Pill Animations
export const badgeVariants: Variants = {
  initial: {
    scale: 0,
    opacity: 0,
  },
  animate: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

// Success/Error Animations
export const successCheckVariants: Variants = {
  initial: {
    scale: 0,
    rotate: -180,
    opacity: 0,
  },
  animate: {
    scale: 1,
    rotate: 0,
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

export const errorShakeVariants: Variants = {
  initial: { x: 0 },
  animate: {
    x: [-10, 10, -10, 10, 0],
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
    },
  },
};

// Scroll Reveal Animations
export const fadeInUpVariants: Variants = {
  initial: {
    opacity: 0,
    y: 40,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

export const fadeInLeftVariants: Variants = {
  initial: {
    opacity: 0,
    x: -40,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

export const fadeInRightVariants: Variants = {
  initial: {
    opacity: 0,
    x: 40,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

// Scale Animations
export const scaleInVariants: Variants = {
  initial: {
    opacity: 0,
    scale: 0.8,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

// Gold Glow Effect (for premium elements)
export const goldGlowVariants: Variants = {
  initial: {
    boxShadow: '0 0 0 rgba(229, 183, 59, 0)',
  },
  hover: {
    boxShadow: '0 0 30px rgba(229, 183, 59, 0.5)',
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

// Notification Slide In
export const notificationVariants: Variants = {
  initial: {
    x: 400,
    opacity: 0,
  },
  animate: {
    x: 0,
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: [0.22, 1, 0.36, 1],
    },
  },
  exit: {
    x: 400,
    opacity: 0,
    transition: {
      duration: 0.3,
      ease: 'easeIn',
    },
  },
};
