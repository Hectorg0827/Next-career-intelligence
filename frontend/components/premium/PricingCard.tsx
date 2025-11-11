/**
 * Premium Pricing Card Component
 * Beautiful pricing cards for subscription tiers
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Check, Crown, Sparkles, Zap } from 'lucide-react';

interface PricingFeature {
  text: string;
  included: boolean;
  highlight?: boolean;
}

interface PricingCardProps {
  name: string;
  description: string;
  price: number | string;
  billingPeriod?: string;
  features: PricingFeature[];
  isPopular?: boolean;
  isCurrent?: boolean;
  ctaText?: string;
  ctaAction?: () => void;
  badge?: string;
  icon?: React.ReactNode;
  annualSavings?: string;
  className?: string;
}

export const PricingCard: React.FC<PricingCardProps> = ({
  name,
  description,
  price,
  billingPeriod = 'month',
  features,
  isPopular = false,
  isCurrent = false,
  ctaText = 'Get Started',
  ctaAction,
  badge,
  icon,
  annualSavings,
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`
        relative flex flex-col h-full
        bg-white dark:bg-gray-800
        border-2
        ${isPopular ? 'border-primary-500 shadow-2xl shadow-primary-500/20' : 'border-gray-200 dark:border-gray-700 shadow-lg'}
        rounded-2xl overflow-hidden
        ${className}
      `}
    >
      {/* Popular Badge */}
      {isPopular && (
        <div className="absolute top-0 right-0 bg-gradient-to-r from-primary-600 to-primary-500 text-white px-4 py-1 rounded-bl-xl font-semibold text-sm flex items-center gap-1">
          <Sparkles className="w-4 h-4" />
          Most Popular
        </div>
      )}

      {/* Current Plan Badge */}
      {isCurrent && (
        <div className="absolute top-0 left-0 bg-green-500 text-white px-4 py-1 rounded-br-xl font-semibold text-sm flex items-center gap-1">
          <Check className="w-4 h-4" />
          Current Plan
        </div>
      )}

      <div className="p-8 flex-1">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            {icon && (
              <div className={`
                p-3 rounded-xl
                ${isPopular ? 'bg-gradient-to-br from-primary-500 to-primary-600' : 'bg-gray-100 dark:bg-gray-700'}
              `}>
                {icon}
              </div>
            )}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {name}
              </h3>
              {badge && (
                <span className="inline-block mt-1 px-2 py-0.5 text-xs font-semibold rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                  {badge}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          {description}
        </p>

        {/* Price */}
        <div className="mb-6">
          <div className="flex items-baseline gap-2">
            {typeof price === 'number' ? (
              <>
                <span className="text-5xl font-bold text-gray-900 dark:text-white">
                  ${price}
                </span>
                <span className="text-gray-600 dark:text-gray-400">
                  /{billingPeriod}
                </span>
              </>
            ) : (
              <span className="text-5xl font-bold text-gray-900 dark:text-white">
                {price}
              </span>
            )}
          </div>

          {annualSavings && (
            <div className="mt-2 inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg text-sm font-medium">
              <Zap className="w-4 h-4" />
              Save {annualSavings} annually
            </div>
          )}
        </div>

        {/* CTA Button */}
        <button
          onClick={ctaAction}
          disabled={isCurrent}
          className={`
            w-full py-3 px-6 rounded-xl font-semibold text-lg
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
            ${
              isPopular
                ? 'bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white shadow-lg hover:shadow-xl'
                : isCurrent
                ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-gray-900 dark:bg-white hover:bg-gray-800 dark:hover:bg-gray-100 text-white dark:text-gray-900'
            }
          `}
        >
          {isCurrent ? 'Current Plan' : ctaText}
        </button>

        {/* Features */}
        <div className="mt-8 space-y-4">
          <div className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">
            What's Included
          </div>
          <ul className="space-y-3">
            {features.map((feature, index) => (
              <li
                key={index}
                className={`
                  flex items-start gap-3
                  ${feature.included ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400 dark:text-gray-500'}
                `}
              >
                <div
                  className={`
                    mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center
                    ${
                      feature.included
                        ? feature.highlight
                          ? 'bg-gradient-to-br from-primary-500 to-primary-600'
                          : 'bg-green-500'
                        : 'bg-gray-200 dark:bg-gray-700'
                    }
                  `}
                >
                  {feature.included ? (
                    <Check className="w-3 h-3 text-white" />
                  ) : (
                    <span className="text-gray-400 text-xs">×</span>
                  )}
                </div>
                <span className={feature.highlight ? 'font-semibold' : ''}>
                  {feature.text}
                  {feature.highlight && (
                    <span className="ml-2 inline-flex items-center gap-1 px-1.5 py-0.5 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-xs font-semibold rounded">
                      <Crown className="w-3 h-3" />
                      Premium
                    </span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Usage Example:
 *
 * <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto px-4">
 *   <PricingCard
 *     name="Free"
 *     description="Perfect for getting started with AI career tools"
 *     price={0}
 *     features={[
 *       { text: '3 AI resume generations per month', included: true },
 *       { text: '1 AI interview session per month', included: true },
 *       { text: 'Basic career health score', included: true },
 *       { text: 'Job search (limited results)', included: true },
 *       { text: 'Unlimited AI sessions', included: false },
 *       { text: 'Priority support', included: false },
 *     ]}
 *     icon={<Sparkles className="w-6 h-6 text-gray-600" />}
 *     ctaText="Current Plan"
 *     isCurrent={true}
 *   />
 *
 *   <PricingCard
 *     name="Premium"
 *     description="Unlimited AI-powered career advancement"
 *     price={29}
 *     features={[
 *       { text: 'Unlimited AI resume generations', included: true, highlight: true },
 *       { text: 'Unlimited AI interview sessions', included: true, highlight: true },
 *       { text: 'Advanced career health score', included: true },
 *       { text: 'Full job search access', included: true },
 *       { text: 'Priority support', included: true },
 *       { text: 'Export to PDF/Word', included: true },
 *       { text: 'Custom branding', included: false },
 *     ]}
 *     isPopular={true}
 *     icon={<Crown className="w-6 h-6 text-white" />}
 *     badge="Best Value"
 *     annualSavings="$100"
 *     ctaText="Upgrade to Premium"
 *     ctaAction={() => console.log('Upgrade clicked')}
 *   />
 *
 *   <PricingCard
 *     name="Enterprise"
 *     description="For teams and organizations"
 *     price="Custom"
 *     features={[
 *       { text: 'Everything in Premium', included: true },
 *       { text: 'Custom branding', included: true, highlight: true },
 *       { text: 'Team collaboration', included: true, highlight: true },
 *       { text: 'Admin dashboard', included: true },
 *       { text: 'SSO / SAML', included: true },
 *       { text: 'Dedicated support', included: true },
 *       { text: 'Custom integrations', included: true },
 *     ]}
 *     icon={<Zap className="w-6 h-6 text-gray-600" />}
 *     ctaText="Contact Sales"
 *     ctaAction={() => console.log('Contact sales clicked')}
 *   />
 * </div>
 */
