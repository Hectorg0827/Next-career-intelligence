/**
 * NEXT Career Intelligence - Accordion Component
 * Super-Premium Design System
 *
 * Expandable accordion component for FAQs, feature lists, and collapsible content.
 * Supports single or multiple open panels, smooth animations, and accessibility.
 */

'use client';

import React, { useState, createContext, useContext } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Plus, Minus } from 'lucide-react';

interface AccordionContextValue {
  openItems: string[];
  toggleItem: (itemId: string) => void;
  allowMultiple: boolean;
}

const AccordionContext = createContext<AccordionContextValue | null>(null);

export interface AccordionProps {
  /** Accordion items */
  children: React.ReactNode;
  /** Allow multiple panels to be open simultaneously */
  allowMultiple?: boolean;
  /** Default open item IDs */
  defaultOpen?: string[];
  /** Controlled open items */
  value?: string[];
  /** Callback when open items change */
  onChange?: (openItems: string[]) => void;
  /** Custom className */
  className?: string;
  /** Visual variant */
  variant?: 'default' | 'bordered' | 'separated' | 'minimal';
}

/**
 * Accordion Container
 *
 * @example
 * ```tsx
 * <Accordion allowMultiple defaultOpen={['item-1']}>
 *   <AccordionItem id="item-1" title="What is NEXT?">
 *     NEXT is an AI-powered career intelligence platform.
 *   </AccordionItem>
 *   <AccordionItem id="item-2" title="How does it work?">
 *     We use advanced AI to analyze job markets and career paths.
 *   </AccordionItem>
 * </Accordion>
 * ```
 */
export const Accordion: React.FC<AccordionProps> = ({
  children,
  allowMultiple = false,
  defaultOpen = [],
  value,
  onChange,
  className = '',
  variant = 'default',
}) => {
  const [internalOpenItems, setInternalOpenItems] = useState<string[]>(defaultOpen);
  const isControlled = value !== undefined;
  const openItems = isControlled ? value : internalOpenItems;

  const toggleItem = (itemId: string) => {
    let newOpenItems: string[];

    if (allowMultiple) {
      newOpenItems = openItems.includes(itemId)
        ? openItems.filter((id) => id !== itemId)
        : [...openItems, itemId];
    } else {
      newOpenItems = openItems.includes(itemId) ? [] : [itemId];
    }

    if (!isControlled) {
      setInternalOpenItems(newOpenItems);
    }
    onChange?.(newOpenItems);
  };

  const variantClasses = {
    default: 'space-y-2',
    bordered: 'border border-gray-200 dark:border-gray-700 rounded-xl divide-y divide-gray-200 dark:divide-gray-700',
    separated: 'space-y-4',
    minimal: 'space-y-1',
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggleItem, allowMultiple }}>
      <div className={`${variantClasses[variant]} ${className}`}>
        {children}
      </div>
    </AccordionContext.Provider>
  );
};

export interface AccordionItemProps {
  /** Unique identifier for this item */
  id: string;
  /** Item title/header */
  title: string;
  /** Item description (shown in header) */
  description?: string;
  /** Item content */
  children: React.ReactNode;
  /** Custom icon */
  icon?: React.ReactNode;
  /** Icon style */
  iconStyle?: 'chevron' | 'plus-minus';
  /** Disable the item */
  disabled?: boolean;
  /** Custom className for item */
  className?: string;
  /** Custom className for content */
  contentClassName?: string;
}

/**
 * Accordion Item
 */
export const AccordionItem: React.FC<AccordionItemProps> = ({
  id,
  title,
  description,
  children,
  icon,
  iconStyle = 'chevron',
  disabled = false,
  className = '',
  contentClassName = '',
}) => {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error('AccordionItem must be used within an Accordion');
  }

  const { openItems, toggleItem } = context;
  const isOpen = openItems.includes(id);

  const renderIcon = () => {
    if (icon) return icon;

    if (iconStyle === 'plus-minus') {
      return isOpen ? (
        <Minus className="w-5 h-5" />
      ) : (
        <Plus className="w-5 h-5" />
      );
    }

    return (
      <motion.div
        animate={{ rotate: isOpen ? 180 : 0 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
      >
        <ChevronDown className="w-5 h-5" />
      </motion.div>
    );
  };

  return (
    <div className={className}>
      {/* Header */}
      <button
        onClick={() => !disabled && toggleItem(id)}
        disabled={disabled}
        className={`
          w-full flex items-center justify-between gap-4
          px-6 py-4
          text-left
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800'}
          transition-colors duration-200
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset
          rounded-lg
        `}
        aria-expanded={isOpen}
        aria-controls={`accordion-content-${id}`}
        id={`accordion-header-${id}`}
      >
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          {description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>

        <div className="text-gray-500 dark:text-gray-400">
          {renderIcon()}
        </div>
      </button>

      {/* Content */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            id={`accordion-content-${id}`}
            role="region"
            aria-labelledby={`accordion-header-${id}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className={`px-6 pb-4 text-gray-700 dark:text-gray-300 ${contentClassName}`}>
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

/**
 * FAQ Accordion - Pre-configured for FAQ sections
 */
export const FAQAccordion: React.FC<{
  faqs: Array<{
    id: string;
    question: string;
    answer: string | React.ReactNode;
  }>;
  className?: string;
}> = ({ faqs, className = '' }) => {
  return (
    <Accordion allowMultiple={false} variant="bordered" className={className}>
      {faqs.map((faq) => (
        <AccordionItem
          key={faq.id}
          id={faq.id}
          title={faq.question}
          iconStyle="plus-minus"
        >
          {typeof faq.answer === 'string' ? (
            <p className="text-base leading-relaxed">{faq.answer}</p>
          ) : (
            faq.answer
          )}
        </AccordionItem>
      ))}
    </Accordion>
  );
};

/**
 * Feature Accordion - Pre-configured for feature showcases
 */
export const FeatureAccordion: React.FC<{
  features: Array<{
    id: string;
    title: string;
    description: string;
    content: React.ReactNode;
    icon?: React.ReactNode;
  }>;
  className?: string;
}> = ({ features, className = '' }) => {
  return (
    <Accordion allowMultiple variant="separated" className={className}>
      {features.map((feature) => (
        <AccordionItem
          key={feature.id}
          id={feature.id}
          title={feature.title}
          description={feature.description}
          icon={feature.icon}
          className="
            bg-white dark:bg-gray-900
            border border-gray-200 dark:border-gray-700
            rounded-xl
            shadow-sm
            hover:shadow-md
            transition-shadow duration-200
          "
        >
          <div className="pt-2">
            {feature.content}
          </div>
        </AccordionItem>
      ))}
    </Accordion>
  );
};

export default Accordion;
