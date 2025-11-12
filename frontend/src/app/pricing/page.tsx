'use client';

import { useState } from 'react';
import { Check, Sparkles, Zap, Crown, ArrowRight, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api';

export default function PricingPage() {
  const router = useRouter();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Stripe Price IDs (you'll need to create these in Stripe Dashboard)
  const PRICE_IDS = {
    monthly: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_MONTHLY || 'price_monthly',
    yearly: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_PRO_YEARLY || 'price_yearly',
  };

  const plans = [
    {
      name: 'Free',
      price: 0,
      period: 'forever',
      description: 'Perfect for exploring career options',
      features: [
        '2 free career analyses',
        'Basic job search',
        'Community access',
        'Career resources',
        'Email support'
      ],
      cta: 'Get Started Free',
      popular: false,
      icon: Sparkles
    },
    {
      name: 'Pro',
      price: billingCycle === 'monthly' ? 29 : 290,
      period: billingCycle === 'monthly' ? 'month' : 'year',
      description: 'For serious career advancement',
      features: [
        'Unlimited AI career analyses',
        'AI Coach - 24/7 personalized guidance',
        'AI Interview Practice - unlimited sessions',
        'Advanced job matching',
        'Resume optimization tools',
        'Salary negotiation guides',
        'Priority support',
        'Monthly skill assessments'
      ],
      cta: 'Start Pro Trial',
      popular: true,
      icon: Zap,
      badge: 'Most Popular'
    },
    {
      name: 'Enterprise',
      price: null,
      period: 'custom',
      description: 'For teams and organizations',
      features: [
        'Everything in Pro',
        'Team management dashboard',
        'Custom training programs',
        'Dedicated account manager',
        'API access',
        'Advanced analytics',
        'SSO & security controls',
        '24/7 phone support'
      ],
      cta: 'Contact Sales',
      popular: false,
      icon: Crown
    }
  ];

  const handleSelectPlan = async (planName: string) => {
    if (planName === 'Free') {
      router.push('/auth/signup');
      return;
    } 
    
    if (planName === 'Enterprise') {
      router.push('/contact');
      return;
    }
    
    // Pro plan - create Stripe checkout session
    try {
      setLoading(planName);
      setError(null);
      
      const priceId = billingCycle === 'monthly' ? PRICE_IDS.monthly : PRICE_IDS.yearly;
      
      const { url } = await apiClient.createCheckoutSession({
        price_id: priceId,
        success_url: `${window.location.origin}/checkout/success`,
        cancel_url: `${window.location.origin}/checkout/cancel`
      });
      
      // Redirect to Stripe checkout
      window.location.href = url;
    } catch (err: any) {
      console.error('Checkout error:', err);
      setError(err.message || 'Failed to create checkout session');
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen gradient-dark-glass py-12 px-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden opacity-30">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent-500 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-500/60 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-accent-400/40 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Error Message */}
        {error && (
          <div className="mb-6 max-w-2xl mx-auto glass-card p-4 bg-red-500/10 border border-red-400/50 rounded-xl text-red-300 text-center">
            {error}
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Choose Your Path to
            <span className="block bg-gradient-to-r from-accent-500 via-accent-400 to-accent-500 bg-clip-text text-transparent">
              Career Success
            </span>
          </h1>
          <p className="text-xl text-ink-200 max-w-2xl mx-auto mb-8">
            Unlock AI-powered career guidance and future-proof your professional journey
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center gap-4 glass-card p-2 rounded-full">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-gradient-to-r from-accent-500 to-accent-400 text-white'
                  : 'text-white hover:text-ink-200'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                billingCycle === 'yearly'
                  ? 'bg-gradient-to-r from-accent-500 to-accent-400 text-white'
                  : 'text-white hover:text-ink-200'
              }`}
            >
              Yearly
              <span className="ml-2 text-sm text-green-400">Save 17%</span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan) => {
            const Icon = plan.icon;
            return (
              <div
                key={plan.name}
                className={`relative glass-card hover-reflect rounded-2xl p-8 transition-all hover:scale-105 ${
                  plan.popular
                    ? 'border-accent-400/50 shadow-glass-xl shadow-accent-400/20'
                    : 'border-glass-line'
                }`}
              >
                {/* Popular Badge */}
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <div className="bg-gradient-to-r from-accent-500 to-accent-400 text-white px-4 py-1 rounded-full text-sm font-bold shadow-glass-md">
                      {plan.badge}
                    </div>
                  </div>
                )}

                {/* Plan Header */}
                <div className="text-center mb-6">
                  <Icon className="w-12 h-12 text-accent-400 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-ink-300 text-sm mb-4">{plan.description}</p>
                  
                  {/* Price */}
                  <div className="mb-4">
                    {plan.price !== null ? (
                      <>
                        <span className="text-5xl font-bold text-white">${plan.price}</span>
                        <span className="text-ink-400 ml-2">/{plan.period}</span>
                        {billingCycle === 'yearly' && plan.price > 0 && (
                          <div className="text-sm text-green-400 mt-1">
                            ${Math.round(plan.price / 12)}/month billed annually
                          </div>
                        )}
                      </>
                    ) : (
                      <span className="text-4xl font-bold text-white">Custom</span>
                    )}
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      <span className="text-ink-200 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleSelectPlan(plan.name)}
                  disabled={loading === plan.name}
                  className={`w-full py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                    plan.popular
                      ? 'primary-btn hover:shadow-glass-xl'
                      : 'glass-card text-white hover:bg-glass-edge border border-glass-line'
                  }`}
                >
                  {loading === plan.name ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    <>
                      {plan.cta}
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto glass-card hover-reflect rounded-2xl shadow-glass-lg p-8">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I switch plans anytime?
              </h3>
              <p className="text-ink-200">
                Yes! You can upgrade, downgrade, or cancel your subscription at any time. Changes take effect at the end of your billing period.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-ink-200">
                We accept all major credit cards (Visa, MasterCard, American Express) and digital payments through Stripe.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Is there a free trial for Pro?
              </h3>
              <p className="text-ink-200">
                Yes! All new Pro subscribers get a 7-day free trial. Cancel anytime during the trial and you won't be charged.
              </p>
            </div>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="text-center mt-12">
          <p className="text-ink-400 text-sm mb-4">Trusted by 10,000+ professionals worldwide</p>
          <div className="flex items-center justify-center gap-8 flex-wrap text-ink-300 text-sm">
            <span>🔒 Secure Payments</span>
            <span>✓ Cancel Anytime</span>
            <span>💳 Money-back Guarantee</span>
          </div>
        </div>
      </div>
    </div>
  );
}
