/**
 * NEXT Career Intelligence - Drawer Component
 * Super-Premium Design System
 *
 * A premium slide-out panel component for navigation, settings, filters, etc.
 * Features smooth animations, backdrop blur, and accessibility support.
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export interface DrawerProps {
  /** Whether the drawer is open */
  isOpen: boolean;
  /** Function to call when drawer should close */
  onClose: () => void;
  /** Drawer title */
  title?: string;
  /** Drawer description (for accessibility) */
  description?: string;
  /** Drawer content */
  children: React.ReactNode;
  /** Position of the drawer */
  position?: 'left' | 'right' | 'top' | 'bottom';
  /** Size of the drawer */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Show close button */
  showCloseButton?: boolean;
  /** Close on overlay click */
  closeOnOverlayClick?: boolean;
  /** Close on escape key */
  closeOnEscape?: boolean;
  /** Show backdrop */
  showBackdrop?: boolean;
  /** Custom className for drawer content */
  className?: string;
  /** Footer content (buttons, actions) */
  footer?: React.ReactNode;
}

/**
 * Premium Drawer Component
 *
 * @example
 * ```tsx
 * const [isOpen, setIsOpen] = useState(false);
 *
 * <Drawer
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   title="Filters"
 *   position="right"
 *   size="md"
 * >
 *   <FilterContent />
 * </Drawer>
 * ```
 */
export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  position = 'right',
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showBackdrop = true,
  className = '',
  footer,
}) => {
  const drawerRef = useRef<HTMLDivElement>(null);

  // Size mappings for different positions
  const sizeClasses = {
    horizontal: {
      sm: 'w-64',
      md: 'w-80',
      lg: 'w-96',
      xl: 'w-[32rem]',
      full: 'w-full',
    },
    vertical: {
      sm: 'h-64',
      md: 'h-80',
      lg: 'h-96',
      xl: 'h-[32rem]',
      full: 'h-full',
    },
  };

  const isHorizontal = position === 'left' || position === 'right';
  const sizeClass = isHorizontal
    ? sizeClasses.horizontal[size]
    : sizeClasses.vertical[size];

  // Position-specific styles
  const positionClasses = {
    left: 'top-0 left-0 h-full',
    right: 'top-0 right-0 h-full',
    top: 'top-0 left-0 w-full',
    bottom: 'bottom-0 left-0 w-full',
  };

  // Animation variants based on position
  const slideVariants = {
    left: { x: '-100%' },
    right: { x: '100%' },
    top: { y: '-100%' },
    bottom: { y: '100%' },
  };

  // Handle escape key
  useEffect(() => {
    if (!closeOnEscape || !isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Lock body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Focus trap
  useEffect(() => {
    if (!isOpen || !drawerRef.current) return;

    const drawer = drawerRef.current;
    const focusableElements = drawer.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    drawer.addEventListener('keydown', handleTab as any);
    firstElement?.focus();

    return () => {
      drawer.removeEventListener('keydown', handleTab as any);
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop with blur */}
          {showBackdrop && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              onClick={closeOnOverlayClick ? onClose : undefined}
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
              aria-hidden="true"
            />
          )}

          {/* Drawer panel */}
          <motion.div
            ref={drawerRef}
            initial={slideVariants[position]}
            animate={{ x: 0, y: 0 }}
            exit={slideVariants[position]}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className={`
              fixed z-50 ${positionClasses[position]} ${sizeClass}
              bg-white dark:bg-gray-900
              shadow-2xl
              flex flex-col
              ${className}
            `}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'drawer-title' : undefined}
            aria-describedby={description ? 'drawer-description' : undefined}
          >
            {/* Header */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex-1">
                  {title && (
                    <h2
                      id="drawer-title"
                      className="text-xl font-semibold text-gray-900 dark:text-white"
                    >
                      {title}
                    </h2>
                  )}
                  {description && (
                    <p
                      id="drawer-description"
                      className="mt-1 text-sm text-gray-500 dark:text-gray-400"
                    >
                      {description}
                    </p>
                  )}
                </div>

                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="
                      ml-4 p-2
                      text-gray-400 hover:text-gray-600
                      dark:text-gray-500 dark:hover:text-gray-300
                      rounded-lg
                      hover:bg-gray-100 dark:hover:bg-gray-800
                      transition-all duration-200
                      focus:outline-none focus:ring-2 focus:ring-primary-500
                    "
                    aria-label="Close drawer"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            )}

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                {footer}
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

/**
 * Common drawer footer with action buttons
 */
export const DrawerFooter: React.FC<{
  onCancel?: () => void;
  onConfirm?: () => void;
  cancelText?: string;
  confirmText?: string;
  confirmDisabled?: boolean;
  confirmLoading?: boolean;
}> = ({
  onCancel,
  onConfirm,
  cancelText = 'Cancel',
  confirmText = 'Confirm',
  confirmDisabled = false,
  confirmLoading = false,
}) => {
  return (
    <div className="flex items-center justify-end gap-3">
      {onCancel && (
        <button
          onClick={onCancel}
          className="
            px-4 py-2
            text-gray-700 dark:text-gray-300
            border border-gray-300 dark:border-gray-600
            rounded-lg
            hover:bg-gray-50 dark:hover:bg-gray-800
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-primary-500
          "
        >
          {cancelText}
        </button>
      )}

      {onConfirm && (
        <button
          onClick={onConfirm}
          disabled={confirmDisabled || confirmLoading}
          className="
            px-4 py-2
            bg-gradient-to-r from-primary-600 to-primary-500
            text-white font-medium
            rounded-lg
            hover:from-primary-700 hover:to-primary-600
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-primary-500
            shadow-lg shadow-primary-500/30
          "
        >
          {confirmLoading ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Loading...
            </span>
          ) : (
            confirmText
          )}
        </button>
      )}
    </div>
  );
};

export default Drawer;
