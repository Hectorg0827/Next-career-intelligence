/**
 * Premium Feature Gate Component
 * Blocks premium features and shows elegant upgrade prompts
 */

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Crown, Lock, Sparkles, Zap, X } from 'lucide-react';
import { Modal } from '../ui/Modal';

interface FeatureGateProps {
  /** Is the user on a premium plan? */
  isPremium: boolean;
  /** Feature name to display in upgrade prompt */
  featureName: string;
  /** Feature description */
  featureDescription?: string;
  /** Children to render (blurred if not premium) */
  children: React.ReactNode;
  /** Blur intensity (0-20) */
  blurAmount?: number;
  /** Show overlay with lock icon */
  showOverlay?: boolean;
  /** Custom upgrade CTA text */
  upgradeText?: string;
  /** Callback when upgrade is clicked */
  onUpgrade?: () => void;
  /** Show inline prompt instead of modal */
  inline?: boolean;
  /** Custom className */
  className?: string;
}

export const FeatureGate: React.FC<FeatureGateProps> = ({
  isPremium,
  featureName,
  featureDescription,
  children,
  blurAmount = 8,
  showOverlay = true,
  upgradeText = 'Upgrade to Premium',
  onUpgrade,
  inline = false,
  className = '',
}) => {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  // If premium, just render children
  if (isPremium) {
    return <>{children}</>;
  }

  const handleUpgradeClick = () => {
    if (onUpgrade) {
      onUpgrade();
    } else {
      setShowUpgradeModal(true);
    }
  };

  const UpgradePrompt = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center space-y-4"
    >
      {/* Icon */}
      <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg">
        <Crown className="w-8 h-8 text-white" />
      </div>

      {/* Title */}
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
        Unlock {featureName}
      </h3>

      {/* Description */}
      {featureDescription && (
        <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
          {featureDescription}
        </p>
      )}

      {/* Benefits */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 text-left space-y-3">
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          Premium Benefits
        </div>
        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
          <li className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary-500" />
            Unlimited AI-powered features
          </li>
          <li className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary-500" />
            Priority support
          </li>
          <li className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary-500" />
            Export to PDF/Word
          </li>
          <li className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary-500" />
            Advanced analytics
          </li>
        </ul>
      </div>

      {/* CTA */}
      <button
        onClick={handleUpgradeClick}
        className="
          w-full py-3 px-6 rounded-xl font-semibold text-lg
          bg-gradient-to-r from-primary-600 to-primary-500
          hover:from-primary-700 hover:to-primary-600
          text-white shadow-lg hover:shadow-xl
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
        "
      >
        {upgradeText} - $29/month
      </button>

      {/* Learn More */}
      <button
        className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
        onClick={() => {/* Navigate to pricing page */}}
      >
        View all plans →
      </button>
    </motion.div>
  );

  // Inline version - no modal
  if (inline) {
    return (
      <div className={`relative ${className}`}>
        <div
          className="relative"
          style={{ filter: `blur(${blurAmount}px)`, pointerEvents: 'none' }}
        >
          {children}
        </div>

        <div className="absolute inset-0 flex items-center justify-center bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm">
          <div className="max-w-md p-8">
            <UpgradePrompt />
          </div>
        </div>
      </div>
    );
  }

  // Overlay version with modal
  return (
    <>
      <div className={`relative ${className}`}>
        {/* Blurred content */}
        <div
          className="relative"
          style={{
            filter: `blur(${blurAmount}px)`,
            pointerEvents: 'none',
            userSelect: 'none',
          }}
        >
          {children}
        </div>

        {/* Overlay */}
        {showOverlay && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm cursor-pointer"
            onClick={handleUpgradeClick}
          >
            {/* Lock Icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
              className="relative"
            >
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-xl">
                <Lock className="w-10 h-10 text-white" />
              </div>
              {/* Crown badge */}
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                <Crown className="w-5 h-5 text-white" />
              </div>
            </motion.div>

            {/* Text */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-6 text-center"
            >
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Premium Feature
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Upgrade to unlock {featureName}
              </p>
              <button
                className="
                  px-6 py-2 rounded-lg font-semibold
                  bg-gradient-to-r from-primary-600 to-primary-500
                  hover:from-primary-700 hover:to-primary-600
                  text-white shadow-lg
                  transition-all duration-200
                "
              >
                Upgrade Now
              </button>
            </motion.div>
          </motion.div>
        )}
      </div>

      {/* Upgrade Modal */}
      <Modal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        size="lg"
      >
        <UpgradePrompt />
      </Modal>
    </>
  );
};

/**
 * Usage Examples:
 *
 * // Basic usage - blur content and show overlay
 * <FeatureGate
 *   isPremium={user.plan === 'premium'}
 *   featureName="Unlimited AI Sessions"
 *   featureDescription="Get unlimited access to our AI interviewer and resume generator"
 *   onUpgrade={() => router.push('/pricing')}
 * >
 *   <AIInterviewer />
 * </FeatureGate>
 *
 * // Inline version - embedded in the page
 * <FeatureGate
 *   isPremium={isPremium}
 *   featureName="Export to PDF"
 *   inline={true}
 * >
 *   <ResumeExport />
 * </FeatureGate>
 *
 * // Light blur - content partially visible
 * <FeatureGate
 *   isPremium={isPremium}
 *   featureName="Advanced Analytics"
 *   blurAmount={4}
 *   showOverlay={false}
 * >
 *   <AnalyticsDashboard />
 * </FeatureGate>
 *
 * // With custom upgrade handler
 * <FeatureGate
 *   isPremium={isPremium}
 *   featureName="Custom Branding"
 *   upgradeText="Contact Sales"
 *   onUpgrade={() => {
 *     trackEvent('upgrade_intent', { feature: 'custom_branding' });
 *     router.push('/contact-sales');
 *   }}
 * >
 *   <BrandingSettings />
 * </FeatureGate>
 */
