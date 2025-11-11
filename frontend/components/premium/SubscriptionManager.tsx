/**
 * NEXT Career Intelligence - Subscription Manager Component
 * Super-Premium Design System
 *
 * Component for users to view and manage their subscription.
 * Shows current plan, billing details, and upgrade/downgrade options.
 */

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Crown, Zap, Sparkles, Calendar, CreditCard, Check, AlertCircle, ExternalLink } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Modal } from '../ui/Modal';

export interface Subscription {
  plan: 'free' | 'pro' | 'premium';
  status: 'active' | 'cancelled' | 'past_due' | 'trialing';
  billingCycle: 'monthly' | 'annual';
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  trialEnd?: string;
}

export interface SubscriptionManagerProps {
  /** Current subscription data */
  subscription: Subscription;
  /** Callback when user upgrades */
  onUpgrade?: () => void;
  /** Callback when user cancels */
  onCancel?: () => void;
  /** Callback when user updates payment */
  onUpdatePayment?: () => void;
}

const planDetails = {
  free: {
    name: 'Free',
    icon: Sparkles,
    color: 'from-gray-600 to-gray-500',
    features: [
      '2 free career analyses',
      'Basic job search',
      'Community access',
      'Career resources',
    ],
  },
  pro: {
    name: 'Pro',
    icon: Zap,
    color: 'from-primary-600 to-primary-500',
    features: [
      'Unlimited AI career analyses',
      'Visual career maps',
      'Industry benchmarking',
      'Interview preparation AI',
      'Skill gap analysis',
      'Priority support',
    ],
  },
  premium: {
    name: 'Premium',
    icon: Crown,
    color: 'from-amber-500 to-orange-500',
    features: [
      'Everything in Pro',
      'Priority AI processing',
      'Custom career roadmaps',
      'Advanced analytics',
      'Priority support (24/7)',
      'API access',
    ],
  },
};

/**
 * Subscription Manager Component
 *
 * @example
 * ```tsx
 * <SubscriptionManager
 *   subscription={{
 *     plan: 'pro',
 *     status: 'active',
 *     billingCycle: 'monthly',
 *     currentPeriodEnd: '2024-12-31',
 *     cancelAtPeriodEnd: false,
 *   }}
 *   onUpgrade={() => router.push('/pricing')}
 *   onCancel={handleCancel}
 *   onUpdatePayment={handleUpdatePayment}
 * />
 * ```
 */
export const SubscriptionManager: React.FC<SubscriptionManagerProps> = ({
  subscription,
  onUpgrade,
  onCancel,
  onUpdatePayment,
}) => {
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  const plan = planDetails[subscription.plan];
  const Icon = plan.icon;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getStatusBadge = () => {
    switch (subscription.status) {
      case 'active':
        return <Badge variant="success" icon="check">Active</Badge>;
      case 'trialing':
        return <Badge variant="info" icon="sparkles">Trial</Badge>;
      case 'cancelled':
        return <Badge variant="default">Cancelled</Badge>;
      case 'past_due':
        return <Badge variant="error" icon="alert">Payment Due</Badge>;
      default:
        return null;
    }
  };

  const handleCancelConfirm = async () => {
    setIsCancelling(true);
    try {
      await onCancel?.();
      setShowCancelModal(false);
    } catch (error) {
      console.error('Cancel error:', error);
    } finally {
      setIsCancelling(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Current Plan Card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        {/* Plan Header */}
        <div className={`bg-gradient-to-r ${plan.color} px-6 py-8 text-white`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{plan.name} Plan</h2>
                <p className="text-white/80 text-sm">
                  {subscription.billingCycle === 'annual' ? 'Billed annually' : 'Billed monthly'}
                </p>
              </div>
            </div>
            {getStatusBadge()}
          </div>

          {/* Billing Info */}
          <div className="space-y-2 text-sm">
            {subscription.status === 'trialing' && subscription.trialEnd && (
              <div className="flex items-center gap-2 bg-white/10 rounded-lg px-3 py-2">
                <Sparkles className="w-4 h-4" />
                <span>Trial ends {formatDate(subscription.trialEnd)}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>
                {subscription.cancelAtPeriodEnd
                  ? `Access until ${formatDate(subscription.currentPeriodEnd)}`
                  : `Renews on ${formatDate(subscription.currentPeriodEnd)}`}
              </span>
            </div>
          </div>
        </div>

        {/* Plan Features */}
        <div className="p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            What's included:
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {plan.features.map((feature, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <Check className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {feature}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Upgrade Card */}
        {subscription.plan !== 'premium' && subscription.status === 'active' && (
          <motion.button
            onClick={onUpgrade}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 border-2 border-primary-200 dark:border-primary-700 rounded-xl p-6 text-left hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-500 rounded-xl flex items-center justify-center">
                <Crown className="w-6 h-6 text-white" />
              </div>
              <ExternalLink className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-2">
              Upgrade Your Plan
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Unlock more features and accelerate your career growth
            </p>
          </motion.button>
        )}

        {/* Payment Method Card */}
        {subscription.plan !== 'free' && (
          <motion.button
            onClick={onUpdatePayment}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl p-6 text-left hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center">
                <CreditCard className="w-6 h-6 text-gray-600 dark:text-gray-400" />
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-2">
              Payment Method
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Update your billing information
            </p>
          </motion.button>
        )}
      </div>

      {/* Cancel Subscription */}
      {subscription.plan !== 'free' && subscription.status === 'active' && !subscription.cancelAtPeriodEnd && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Cancel Subscription
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                You can cancel your subscription at any time. You'll continue to have access until the end of your billing period.
              </p>
              <button
                onClick={() => setShowCancelModal(true)}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              >
                Cancel Subscription
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Cancelled Notice */}
      {subscription.cancelAtPeriodEnd && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Subscription Cancelled
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your subscription will end on {formatDate(subscription.currentPeriodEnd)}. You'll have access to all {plan.name} features until then.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Cancel Confirmation Modal */}
      <Modal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        title="Cancel Subscription?"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-700 dark:text-gray-300">
            Are you sure you want to cancel your {plan.name} subscription? You'll lose access to:
          </p>
          <ul className="space-y-2">
            {plan.features.slice(0, 4).map((feature, idx) => (
              <li key={idx} className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <span className="text-red-500">×</span>
                {feature}
              </li>
            ))}
          </ul>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            You'll continue to have access until {formatDate(subscription.currentPeriodEnd)}.
          </p>
          <div className="flex gap-3 pt-4">
            <button
              onClick={() => setShowCancelModal(false)}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Keep Subscription
            </button>
            <button
              onClick={handleCancelConfirm}
              disabled={isCancelling}
              className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {isCancelling ? 'Cancelling...' : 'Confirm Cancellation'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SubscriptionManager;
