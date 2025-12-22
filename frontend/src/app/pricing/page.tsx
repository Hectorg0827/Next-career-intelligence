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
      name: 'Explorer',
      price: 0,
      period: 'forever',
      description: 'Essential tools for career discovery.',
      features: [
        '2 AI Career Analyses',
        'Basic Market Insights',
        'Public Talent Graph',
        'Standard Support'
      ],
      cta: 'Start Free',
      popular: false,
      icon: Sparkles
    },
    {
      name: 'Professional',
      price: billingCycle === 'monthly' ? 49 : 39,
      period: 'month',
      description: 'The complete career intelligence suite.',
      features: [
        'Unlimited AI Analyses',
        '24/7 AI Career Coach',
        'Unlimited Interview Prep',
        'Resume Intelligence Engine',
        'Salary Negotiation AI',
        'Priority Support'
      ],
      cta: 'Get Pro Access',
      popular: true,
      icon: Zap,
      badge: 'Recommended'
    },
    {
      name: 'Elite',
      price: billingCycle === 'monthly' ? 199 : 159,
      period: 'month',
      description: 'For high-impact leaders and executives.',
      features: [
        'Everything in Pro',
        'Executive Brand Strategy',
        'Board Seat Intelligence',
        'Private Network Access',
        'Dedicated Career Strategist',
        'White-glove Support'
      ],
      cta: 'Go Elite',
      popular: false,
      icon: Crown
    }
  ];

  const handleSelectPlan = async (planName: string) => {
    if (planName === 'Explorer') {
      router.push('/auth/signup');
      return;
    } 
    
    if (planName === 'Elite') {
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
    <div className="min-h-screen bg-premium-bg pt-32 pb-20 px-6">
      {/* Header */}
      <div className="max-w-4xl mx-auto text-center mb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-premium-accent/10 border border-premium-accent/20 text-premium-accent text-sm font-bold mb-6"
        >
          <Star className="w-4 h-4 fill-premium-accent" />
          <span>Investment in your future</span>
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-5xl md:text-6xl font-serif text-white mb-6"
        >
          Choose Your <span className="italic text-premium-accent">Trajectory</span>
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-xl text-premium-text-muted mb-10"
        >
          Unlock the full power of AI-driven career intelligence.
        </motion.p>

        {/* Billing Toggle */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex items-center justify-center gap-4"
        >
          <span className={`text-sm font-medium ${billingCycle === 'monthly' ? 'text-white' : 'text-premium-text-muted'}`}>Monthly</span>
          <button 
            onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
            className="w-14 h-7 rounded-full bg-white/10 p-1 relative transition-colors hover:bg-white/20"
          >
            <div className={`w-5 h-5 rounded-full bg-premium-accent transition-all duration-300 ${billingCycle === 'yearly' ? 'translate-x-7' : 'translate-x-0'}`} />
          </button>
          <span className={`text-sm font-medium ${billingCycle === 'yearly' ? 'text-white' : 'text-premium-text-muted'}`}>
            Yearly <span className="text-premium-accent ml-1">(Save 20%)</span>
          </span>
        </motion.div>
      </div>

      {error && (
        <div className="max-w-md mx-auto mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-center">
          {error}
        </div>
      )}

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan, index) => (
          <motion.div
            key={plan.name}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index }}
            className={`premium-card p-8 flex flex-col relative ${plan.popular ? 'border-premium-accent/40 shadow-[0_0_40px_rgba(0,217,255,0.1)]' : ''}`}
          >
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-premium-accent text-premium-primary px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest">
                {plan.badge}
              </div>
            )}

            <div className="mb-8">
              <plan.icon className={`w-10 h-10 mb-6 ${plan.popular ? 'text-premium-accent' : 'text-white/40'}`} />
              <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
              <p className="text-premium-text-muted text-sm leading-relaxed">{plan.description}</p>
            </div>

            <div className="mb-8">
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-bold text-white">${plan.price}</span>
                {plan.price !== null && (
                  <span className="text-premium-text-muted">/{plan.period}</span>
                )}
              </div>
            </div>

            <ul className="space-y-4 mb-10 flex-1">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-3 text-sm text-premium-text">
                  <Check className="w-5 h-5 text-premium-accent shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>

            <button 
              onClick={() => handleSelectPlan(plan.name)}
              disabled={loading !== null}
              className={`w-full py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2 ${
                plan.popular 
                ? 'bg-premium-accent text-premium-primary hover:shadow-[0_10px_30px_rgba(0,217,255,0.3)] hover:-translate-y-1' 
                : 'bg-white/5 text-white border border-white/10 hover:bg-white/10'
              }`}
            >
              {loading === plan.name ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  {plan.cta}
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </motion.div>
        ))}
      </div>

      {/* Trust Section */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="max-w-4xl mx-auto mt-20 text-center"
      >
        <div className="flex items-center justify-center gap-8 opacity-50 grayscale">
          <ShieldCheck className="w-12 h-12 text-white" />
          <span className="text-white font-serif text-2xl italic">Enterprise Grade Security</span>
        </div>
        <p className="mt-6 text-premium-text-muted text-sm">
          All plans include 256-bit encryption and GDPR compliance. Cancel anytime.
        </p>
      </motion.div>
    </div>
  );
}
}
