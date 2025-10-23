/**
 * useSubscription Hook
 * Fetches and manages user subscription status
 */

'use client';

import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';

export type SubscriptionTier = 'free' | 'pro' | 'enterprise';

interface SubscriptionData {
  tier: SubscriptionTier;
  freeReportsUsed: number;
  stripeCustomerId: string | null;
  canAnalyze: boolean;
  canUseCoach: boolean;
  canUseInterviewer: boolean;
  canAccessJobs: boolean;
}

const FREE_REPORT_LIMIT = 1;

export function useSubscription() {
  const { user, isAuthenticated } = useAuth();
  const [subscription, setSubscription] = useState<SubscriptionData>({
    tier: 'free',
    freeReportsUsed: 0,
    stripeCustomerId: null,
    canAnalyze: false,
    canUseCoach: false,
    canUseInterviewer: false,
    canAccessJobs: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchSubscription() {
      if (!isAuthenticated || !user) {
        setLoading(false);
        return;
      }

      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/subscription`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch subscription');
        }

        const data = await response.json();
        
        const tier: SubscriptionTier = data.subscription_status || 'free';
        const freeReportsUsed = data.free_reports_used || 0;
        
        setSubscription({
          tier,
          freeReportsUsed,
          stripeCustomerId: data.stripe_customer_id,
          // Free tier: 1 analysis, no pro features
          canAnalyze: tier === 'pro' || tier === 'enterprise' || freeReportsUsed < FREE_REPORT_LIMIT,
          // Pro features
          canUseCoach: tier === 'pro' || tier === 'enterprise',
          canUseInterviewer: tier === 'pro' || tier === 'enterprise',
          canAccessJobs: tier === 'pro' || tier === 'enterprise',
        });
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    }

    fetchSubscription();
  }, [user, isAuthenticated]);

  const isPro = subscription.tier === 'pro' || subscription.tier === 'enterprise';
  const isFree = subscription.tier === 'free';
  const hasUsedFreeReport = subscription.freeReportsUsed >= FREE_REPORT_LIMIT;

  return {
    ...subscription,
    isPro,
    isFree,
    hasUsedFreeReport,
    loading,
    error,
  };
}
