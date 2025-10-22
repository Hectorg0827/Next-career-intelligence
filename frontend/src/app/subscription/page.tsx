'use client';

import { useState } from 'react';
import { Check, X, ArrowRight, Zap, CreditCard, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface Plan {
  id: string;
  name: string;
  price: number;
  period: 'monthly' | 'yearly';
  description: string;
  features: { included: string[]; excluded: string[] };
  cta: string;
  highlighted?: boolean;
}

interface Subscription {
  planId: string;
  status: 'active' | 'canceled' | 'expired';
  startDate: string;
  nextBillingDate: string;
  price: number;
}

export default function SubscriptionPage() {
  const [currentSubscription, setCurrentSubscription] = useState<Subscription>({
    planId: 'pro',
    status: 'active',
    startDate: '2025-09-20',
    nextBillingDate: '2025-11-20',
    price: 29.99,
  });

  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const plans: Plan[] = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      period: 'monthly',
      description: 'Get started with essential features',
      features: {
        included: [
          '5 career analyses per month',
          'Basic job search',
          '2 interview practice sessions',
          'Career coach access (limited)',
          'Community access',
        ],
        excluded: ['Advanced analytics', 'Priority support', 'Unlimited interviews', 'API access'],
      },
      cta: 'Your Current Plan',
      highlighted: currentSubscription.planId === 'free',
    },
    {
      id: 'pro',
      name: 'Pro',
      price: billingCycle === 'monthly' ? 29.99 : 299.99,
      period: billingCycle,
      description: 'Perfect for serious job seekers',
      features: {
        included: [
          'Unlimited career analyses',
          'Advanced job search with AI matching',
          'Unlimited interview practice',
          '24/7 career coach access',
          'Monthly skill assessment',
          'Priority email support',
          'Resume optimization tool',
          'Salary negotiation guide',
        ],
        excluded: ['Phone support', 'Custom training plans'],
      },
      cta: currentSubscription.planId === 'pro' ? 'Current Plan' : 'Upgrade',
      highlighted: currentSubscription.planId === 'pro',
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 99.99,
      period: billingCycle,
      description: 'For teams and organizations',
      features: {
        included: [
          'Everything in Pro',
          'Team management',
          'Custom training programs',
          'Dedicated account manager',
          '24/7 phone support',
          'API access',
          'Advanced analytics',
          'Custom integrations',
          'SSO & security controls',
        ],
        excluded: [],
      },
      cta: 'Contact Sales',
      highlighted: currentSubscription.planId === 'enterprise',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 p-8">
      {/* Header */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold text-white mb-3">Subscription Plans</h1>
        <p className="text-xl text-slate-400">Choose the perfect plan for your career journey</p>
      </div>

      {/* Current Subscription */}
      {currentSubscription.status === 'active' && (
        <Card className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border-blue-500/30 mb-12">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Check className="w-5 h-5 text-green-400" />
                  <p className="text-white font-semibold">Active Subscription</p>
                </div>
                <p className="text-slate-300">
                  Your Pro plan renews on {new Date(currentSubscription.nextBillingDate).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-white">${currentSubscription.price}</p>
                <p className="text-slate-400 text-sm">per month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Billing Cycle Toggle */}
      <div className="flex justify-center mb-12">
        <Tabs value={billingCycle} onValueChange={(v) => setBillingCycle(v as 'monthly' | 'yearly')}>
          <TabsList className="bg-slate-800 border border-slate-700">
            <TabsTrigger value="monthly" className="data-[state=active]:bg-blue-600">
              Monthly Billing
            </TabsTrigger>
            <TabsTrigger value="yearly" className="data-[state=active]:bg-blue-600">
              Yearly Billing
              <Badge className="ml-2 bg-green-600 text-white">Save 17%</Badge>
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        {plans.map((plan) => (
          <Card
            key={plan.id}
            className={`border-2 transition ${
              plan.highlighted ? 'border-blue-500 bg-slate-800 shadow-lg shadow-blue-500/20' : 'border-slate-700 bg-slate-800'
            }`}
          >
            {plan.highlighted && (
              <div className="bg-blue-600 text-white px-6 py-2 text-center text-sm font-semibold">
                ⭐ Most Popular
              </div>
            )}

            <CardHeader>
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Price */}
              <div>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-white">${plan.price}</span>
                  <span className="text-slate-400">
                    /{plan.period === 'monthly' ? 'month' : 'year'}
                  </span>
                </div>
              </div>

              {/* CTA */}
              <Button
                className={`w-full ${
                  plan.highlighted
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                }`}
                disabled={currentSubscription.planId === plan.id}
              >
                {plan.cta}
                {plan.id !== currentSubscription.planId && <ArrowRight className="w-4 h-4 ml-2" />}
              </Button>

              {/* Features */}
              <div className="space-y-3">
                <p className="text-sm font-semibold text-slate-300 mb-3">What's included:</p>
                {plan.features.included.map((feature) => (
                  <div key={feature} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}

                {plan.features.excluded.length > 0 && (
                  <>
                    <p className="text-sm font-semibold text-slate-400 mt-4 mb-3">Not included:</p>
                    {plan.features.excluded.map((feature) => (
                      <div key={feature} className="flex items-start gap-3">
                        <X className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-500">{feature}</span>
                      </div>
                    ))}
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* FAQ */}
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Frequently Asked Questions</h2>

        <div className="space-y-4">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-lg">Can I change my plan anytime?</CardTitle>
            </CardHeader>
            <CardContent className="text-slate-300">
              Yes! You can upgrade or downgrade your plan at any time. Changes take effect at your next billing cycle.
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-lg">Is there a free trial?</CardTitle>
            </CardHeader>
            <CardContent className="text-slate-300">
              Yes! Start with our Free plan to explore all features. Upgrade to Pro anytime to unlock premium features.
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-lg">What payment methods do you accept?</CardTitle>
            </CardHeader>
            <CardContent className="text-slate-300">
              We accept all major credit cards, PayPal, and bank transfers for enterprise plans.
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-lg">Do you offer refunds?</CardTitle>
            </CardHeader>
            <CardContent className="text-slate-300">
              We offer a 14-day money-back guarantee. If you're not satisfied, we'll refund your payment.
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Billing Management */}
      <div className="mt-12 max-w-2xl mx-auto">
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="w-5 h-5" />
              Billing Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-slate-400 text-sm mb-1">Payment Method</p>
              <p className="text-white">Visa ending in 4242</p>
              <Button variant="link" className="text-blue-400 p-0 h-auto">
                Update Payment Method
              </Button>
            </div>

            <div className="pt-4 border-t border-slate-700">
              <p className="text-slate-400 text-sm mb-2">Actions</p>
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  Download Invoice
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  Cancel Subscription
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
