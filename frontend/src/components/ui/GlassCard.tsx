/**
 * NEXT Career Intelligence - Glass Card Component
 * Liquid Glass Design System
 *
 * Frosted glass morphism card with subtle borders and backdrop blur.
 * Perfect for modern, polished UI with depth and elegance.
 */

'use client';

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

export interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'className'> {
  /** Additional CSS classes */
  className?: string;
  /** Children elements */
  children: React.ReactNode;
  /** Enable hover effect */
  hover?: boolean;
  /** Enable reflection effect on hover */
  reflection?: boolean;
  /** Padding size */
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  /** Border radius size */
  rounded?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8',
};

const roundedClasses = {
  sm: 'rounded-lg',
  md: 'rounded-xl',
  lg: 'rounded-2xl',
  xl: 'rounded-3xl',
  '2xl': 'rounded-[2rem]',
};

/**
 * Glass Card Component
 *
 * @example
 * ```tsx
 * <GlassCard padding="lg" hover reflection>
 *   <h2 className="text-xl font-bold text-white mb-2">Card Title</h2>
 *   <p className="text-ink-300">Card content goes here</p>
 * </GlassCard>
 * ```
 */
export const GlassCard: React.FC<GlassCardProps> = ({
  className = '',
  children,
  hover = true,
  reflection = false,
  padding = 'lg',
  rounded = 'xl',
  ...motionProps
}) => {
  const baseClasses = 'glass-card';
  const reflectionClass = reflection ? 'hover-reflect' : '';
  const paddingClass = paddingClasses[padding];
  const roundedClass = roundedClasses[rounded];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
      className={`${baseClasses} ${paddingClass} ${roundedClass} ${reflectionClass} ${className}`}
      {...motionProps}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;
