/**
 * NEXT Career Intelligence - Upgrade Modal Component
 * Super-Premium Design System
 *
 * Modal that prompts users to upgrade to a premium plan.
 * Used for feature gates and upgrade prompts throughout the app.
 */

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Crown, Zap, Check, ArrowRight, Sparkles, TrendingUp, Shield } from 'lucide-react';
import { useRouter } from 'next/navigation';

export interface UpgradeModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Feature that triggered the upgrade prompt */
  featureName?: string;
  /** Specific plan to highlight (optional) */
  recommendedPlan?: 'pro' | 'premium';
  /** Custom title */
  title?: string;
  /** Custom description */
  description?: string;
  /** Show benefits list */
  showBenefits?: boolean;
}

const plans = [
  {
    id: 'pro',
    name: 'Pro',
    price: '$29',
    period: '/month',
    description: 'For serious job seekers',
    icon: Zap,
    color: 'from-primary-600 to-primary-500',
    features: [
      'Unlimited AI career analyses',
      'Visual career maps',
      'Industry benchmarking',
      'Interview preparation AI',
      'Skill gap analysis',
    ],
  },
  {
    id: 'premium',
    name: 'Premium',
    price: '$79',
    period: '/month',
    description: 'For professionals',
    icon: Crown,
    color: 'from-amber-500 to-orange-500',
    features: [
      'Everything in Pro',
      'Priority AI processing',
      'Custom career roadmaps',
      'Advanced analytics',
      'Priority support (24/7)',
    ],
  },
];

const benefits = [
  {
    icon: TrendingUp,
    title: 'Accelerate Your Career',
    description: 'AI-powered insights to help you make better career decisions',
  },
  {
    icon: Shield,
    title: 'Stay Ahead of AI',
    description: 'Understand and prepare for AI-driven job market changes',
  },
  {
    icon: Sparkles,
    title: 'Personalized Guidance',
    description: '24/7 AI career coach tailored to your unique goals',
  },
];

/**
 * Upgrade Modal Component
 *
 * @example
 * ```tsx
 * const [showUpgrade, setShowUpgrade] = useState(false);
 *
 * <UpgradeModal
 *   isOpen={showUpgrade}
 *   onClose={() => setShowUpgrade(false)}
 *   featureName="Visual Career Maps"
 *   recommendedPlan="pro"
 * />
 * ```
 */
export const UpgradeModal: React.FC<UpgradeModalProps> = ({
  isOpen,
  onClose,
  featureName,
  recommendedPlan = 'pro',
  title,
  description,
  showBenefits = true,
}) => {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState(recommendedPlan);

  const handleUpgrade = () => {
    // Navigate to pricing page with selected plan
    router.push(`/pricing?plan=${selectedPlan}`);
    onClose();
  };

  const defaultTitle = featureName
    ? `Upgrade to unlock ${featureName}`
    : 'Upgrade to Premium';

  const defaultDescription = featureName
    ? `${featureName} is available on Pro and Premium plans. Upgrade now to access this feature and many more.`
    : 'Get unlimited access to all premium features and accelerate your career growth.';

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 z-modal-backdrop bg-black/60 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-0 z-modal flex items-center justify-center p-4"
          >
            <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-900 rounded-2xl shadow-2xl">
              {/* Close Button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors z-10"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Header */}
              <div className="bg-gradient-to-r from-primary-600 to-primary-500 px-8 py-12 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: 'spring' }}
                  className="w-16 h-16 mx-auto mb-4 bg-white/20 rounded-2xl flex items-center justify-center"
                >
                  <Crown className="w-8 h-8 text-white" />
                </motion.div>
                <h2 className="text-3xl font-bold text-white mb-3">
                  {title || defaultTitle}
                </h2>
                <p className="text-lg text-white/90 max-w-2xl mx-auto">
                  {description || defaultDescription}
                </p>
              </div>

              <div className="p-8">
                {/* Benefits */}
                {showBenefits && (
                  <div className="grid md:grid-cols-3 gap-6 mb-8">
                    {benefits.map((benefit, idx) => {
                      const Icon = benefit.icon;
                      return (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.3 + idx * 0.1 }}
                          className="text-center"
                        >
                          <div className="w-12 h-12 mx-auto mb-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                            <Icon className="w-6 h-6 text-white" />
                          </div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                            {benefit.title}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {benefit.description}
                          </p>
                        </motion.div>
                      );
                    })}
                  </div>
                )}

                {/* Plan Selection */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                  {plans.map((plan, idx) => {
                    const Icon = plan.icon;
                    const isSelected = selectedPlan === plan.id;
                    const isRecommended = recommendedPlan === plan.id;

                    return (
                      <motion.button
                        key={plan.id}
                        initial={{ opacity: 0, x: idx === 0 ? -20 : 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 + idx * 0.1 }}
                        onClick={() => setSelectedPlan(plan.id as 'pro' | 'premium')}
                        className={`
                          relative text-left p-6 rounded-xl border-2 transition-all
                          ${
                            isSelected
                              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-lg'
                              : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
                          }
                        `}
                      >
                        {/* Recommended Badge */}
                        {isRecommended && (
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                            <span className="bg-gradient-to-r from-primary-600 to-primary-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
                              Recommended
                            </span>
                          </div>
                        )}

                        {/* Selection Indicator */}
                        <div
                          className={`absolute top-4 right-4 w-6 h-6 rounded-full border-2 transition-all ${
                            isSelected
                              ? 'border-primary-600 bg-primary-600'
                              : 'border-gray-300 dark:border-gray-600'
                          }`}
                        >
                          {isSelected && (
                            <Check className="w-5 h-5 text-white absolute -top-0.5 -left-0.5" />
                          )}
                        </div>

                        {/* Plan Icon */}
                        <div className={`w-12 h-12 mb-4 bg-gradient-to-br ${plan.color} rounded-xl flex items-center justify-center`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>

                        {/* Plan Name & Price */}
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                          {plan.name}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {plan.description}
                        </p>
                        <div className="flex items-baseline gap-1 mb-4">
                          <span className="text-3xl font-bold text-gray-900 dark:text-white">
                            {plan.price}
                          </span>
                          <span className="text-gray-600 dark:text-gray-400">
                            {plan.period}
                          </span>
                        </div>

                        {/* Features */}
                        <ul className="space-y-2">
                          {plan.features.map((feature, featureIdx) => (
                            <li key={featureIdx} className="flex items-start gap-2">
                              <Check className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                              <span className="text-sm text-gray-700 dark:text-gray-300">
                                {feature}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </motion.button>
                    );
                  })}
                </div>

                {/* CTA Buttons */}
                <div className="flex gap-4">
                  <button
                    onClick={onClose}
                    className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 transition-all"
                  >
                    Maybe Later
                  </button>
                  <button
                    onClick={handleUpgrade}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-lg font-semibold hover:from-primary-700 hover:to-primary-600 transition-all shadow-lg shadow-primary-500/30 flex items-center justify-center gap-2"
                  >
                    Upgrade Now
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>

                {/* Trust Indicators */}
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-center gap-6 text-sm text-gray-600 dark:text-gray-400">
                  <span className="flex items-center gap-1">
                    <Check className="w-4 h-4 text-green-600" />
                    Cancel anytime
                  </span>
                  <span className="flex items-center gap-1">
                    <Check className="w-4 h-4 text-green-600" />
                    14-day trial
                  </span>
                  <span className="flex items-center gap-1">
                    <Check className="w-4 h-4 text-green-600" />
                    Money-back guarantee
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default UpgradeModal;
