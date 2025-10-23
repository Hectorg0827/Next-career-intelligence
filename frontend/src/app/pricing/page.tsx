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
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Error Message */}
        {error && (
          <div className="mb-6 max-w-2xl mx-auto p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-200 text-center">
            {error}
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Choose Your Path to
            <span className="block bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              Career Success
            </span>
          </h1>
          <p className="text-xl text-white/80 max-w-2xl mx-auto mb-8">
            Unlock AI-powered career guidance and future-proof your professional journey
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center gap-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full p-2">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-white text-purple-900'
                  : 'text-white hover:text-white/80'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                billingCycle === 'yearly'
                  ? 'bg-white text-purple-900'
                  : 'text-white hover:text-white/80'
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
                className={`relative bg-white/10 backdrop-blur-md border rounded-2xl p-8 transition-all hover:scale-105 ${
                  plan.popular
                    ? 'border-yellow-400/50 shadow-2xl shadow-yellow-400/20'
                    : 'border-white/20'
                }`}
              >
                {/* Popular Badge */}
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-purple-900 px-4 py-1 rounded-full text-sm font-bold">
                      {plan.badge}
                    </div>
                  </div>
                )}

                {/* Plan Header */}
                <div className="text-center mb-6">
                  <Icon className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-white/70 text-sm mb-4">{plan.description}</p>
                  
                  {/* Price */}
                  <div className="mb-4">
                    {plan.price !== null ? (
                      <>
                        <span className="text-5xl font-bold text-white">${plan.price}</span>
                        <span className="text-white/60 ml-2">/{plan.period}</span>
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
                      <span className="text-white/90 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleSelectPlan(plan.name)}
                  disabled={loading === plan.name}
                  className={`w-full py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                    plan.popular
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-purple-900 hover:shadow-xl hover:shadow-yellow-400/30'
                      : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
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
        <div className="max-w-3xl mx-auto bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I switch plans anytime?
              </h3>
              <p className="text-white/70">
                Yes! You can upgrade, downgrade, or cancel your subscription at any time. Changes take effect at the end of your billing period.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-white/70">
                We accept all major credit cards (Visa, MasterCard, American Express) and digital payments through Stripe.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Is there a free trial for Pro?
              </h3>
              <p className="text-white/70">
                Yes! All new Pro subscribers get a 7-day free trial. Cancel anytime during the trial and you won't be charged.
              </p>
            </div>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="text-center mt-12">
          <p className="text-white/50 text-sm mb-4">Trusted by 10,000+ professionals worldwide</p>
          <div className="flex items-center justify-center gap-8 flex-wrap text-white/40 text-sm">
            <span>🔒 Secure Payments</span>
            <span>✓ Cancel Anytime</span>
            <span>💳 Money-back Guarantee</span>
          </div>
        </div>
      </div>
    </div>
  );
}
