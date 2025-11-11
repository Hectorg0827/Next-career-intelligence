/**
 * Premium Tooltip Component
 * Accessible, animated tooltip with smart positioning
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  className?: string;
  contentClassName?: string;
  disabled?: boolean;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  delay = 200,
  className = '',
  contentClassName = '',
  disabled = false,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState(position);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Smart positioning - adjust if tooltip goes off-screen
  useEffect(() => {
    if (!isVisible || !triggerRef.current || !tooltipRef.current) return;

    const trigger = triggerRef.current.getBoundingClientRect();
    const tooltip = tooltipRef.current.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };

    let newPosition = position;

    // Check if tooltip goes off-screen and adjust
    if (position === 'top' && trigger.top - tooltip.height < 10) {
      newPosition = 'bottom';
    } else if (position === 'bottom' && trigger.bottom + tooltip.height > viewport.height - 10) {
      newPosition = 'top';
    } else if (position === 'left' && trigger.left - tooltip.width < 10) {
      newPosition = 'right';
    } else if (position === 'right' && trigger.right + tooltip.width > viewport.width - 10) {
      newPosition = 'left';
    }

    setTooltipPosition(newPosition);
  }, [isVisible, position]);

  const showTooltip = () => {
    if (disabled) return;
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900 dark:border-t-gray-700',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900 dark:border-b-gray-700',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900 dark:border-l-gray-700',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-gray-900 dark:border-r-gray-700',
  };

  const animationVariants = {
    top: { initial: { opacity: 0, y: 5 }, animate: { opacity: 1, y: 0 } },
    bottom: { initial: { opacity: 0, y: -5 }, animate: { opacity: 1, y: 0 } },
    left: { initial: { opacity: 0, x: 5 }, animate: { opacity: 1, x: 0 } },
    right: { initial: { opacity: 0, x: -5 }, animate: { opacity: 1, x: 0 } },
  };

  return (
    <div
      ref={triggerRef}
      className={`relative inline-block ${className}`}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}

      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={tooltipRef}
            initial={animationVariants[tooltipPosition].initial}
            animate={animationVariants[tooltipPosition].animate}
            exit={animationVariants[tooltipPosition].initial}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={`
              absolute z-50 pointer-events-none
              ${positionClasses[tooltipPosition]}
            `}
            role="tooltip"
          >
            {/* Tooltip content */}
            <div
              className={`
                px-3 py-2 text-sm text-white
                bg-gray-900 dark:bg-gray-700
                rounded-lg shadow-lg
                max-w-xs
                ${contentClassName}
              `}
            >
              {content}
            </div>

            {/* Arrow */}
            <div
              className={`
                absolute w-0 h-0
                border-4 border-transparent
                ${arrowClasses[tooltipPosition]}
              `}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

/**
 * Usage Examples:
 *
 * // Basic tooltip
 * <Tooltip content="Click to edit your profile">
 *   <button>Edit Profile</button>
 * </Tooltip>
 *
 * // Premium feature tooltip
 * <Tooltip
 *   content={
 *     <div>
 *       <div className="font-semibold">Premium Feature</div>
 *       <div className="text-xs mt-1">Upgrade to access unlimited AI sessions</div>
 *     </div>
 *   }
 *   position="right"
 * >
 *   <button className="flex items-center gap-2">
 *     AI Interviewer <Crown className="w-4 h-4 text-yellow-500" />
 *   </button>
 * </Tooltip>
 *
 * // Disabled state
 * <Tooltip content="Coming soon!" disabled={!showTooltips}>
 *   <button disabled>Export PDF</button>
 * </Tooltip>
 */
