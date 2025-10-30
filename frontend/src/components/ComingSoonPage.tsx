'use client';

import { useState } from 'react';
import { Sparkles, ArrowRight, CheckCircle, Clock, Mail } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ComingSoonPageProps {
  feature: {
    title: string;
    subtitle: string;
    icon: string;
    description: string;
    benefits: string[];
    launchTimeline: string;
    previewImage?: string;
  };
}

export default function ComingSoonPage({ feature }: ComingSoonPageProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleWaitlistSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setIsSubmitted(true);
      setIsLoading(false);
      // In production, this would save to waitlist database
      localStorage.setItem(`waitlist_${feature.title}`, email);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900">
      {/* Background Animation */}
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gold-primary rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-royal-blue rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-12">
        <div className="max-w-4xl w-full">
          {/* Back Button */}
          <button
            onClick={() => router.push('/')}
            className="mb-8 px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 rounded-lg text-white/70 hover:text-white transition-all flex items-center gap-2"
          >
            ← Back to Home
          </button>

          {/* Main Card */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 md:p-12 shadow-2xl">
            {/* Header */}
            <div className="text-center mb-12">
              {/* Icon */}
              <div className="text-8xl mb-6 animate-bounce-slow">
                {feature.icon}
              </div>

              {/* Coming Soon Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gold-primary/20 border border-gold-primary/40 rounded-full mb-6">
                <Clock className="w-4 h-4 text-gold-primary" />
                <span className="text-gold-primary text-sm font-semibold">Coming Soon</span>
              </div>

              {/* Title */}
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                {feature.title}
              </h1>

              {/* Subtitle */}
              <p className="text-xl md:text-2xl text-white/80 mb-6">
                {feature.subtitle}
              </p>

              {/* Description */}
              <p className="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed">
                {feature.description}
              </p>
            </div>

            {/* Benefits Section */}
            <div className="mb-12">
              <h2 className="text-2xl font-bold text-white mb-6 text-center">
                What to Expect
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                {feature.benefits.map((benefit, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10 hover:border-gold-primary/50 transition-all group"
                  >
                    <CheckCircle className="w-6 h-6 text-gold-primary flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                    <span className="text-white/90">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Timeline */}
            <div className="mb-12 text-center">
              <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-gold-primary/20 to-gold-accent/20 border border-gold-primary/30 rounded-xl">
                <Sparkles className="w-5 h-5 text-gold-primary" />
                <span className="text-white font-semibold">Expected Launch: {feature.launchTimeline}</span>
              </div>
            </div>

            {/* Waitlist Form */}
            {!isSubmitted ? (
              <div className="max-w-md mx-auto">
                <h3 className="text-xl font-bold text-white mb-4 text-center">
                  Join the Waitlist
                </h3>
                <p className="text-white/70 mb-6 text-center">
                  Be the first to know when we launch. Get exclusive early access!
                </p>
                <form onSubmit={handleWaitlistSignup} className="space-y-4">
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your.email@example.com"
                      className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-primary focus:border-transparent transition-all"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full px-6 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-royal-navy/30 border-t-royal-navy rounded-full animate-spin"></div>
                        <span>Joining...</span>
                      </>
                    ) : (
                      <>
                        <span>Join Waitlist</span>
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </button>
                </form>
                <p className="text-white/50 text-xs text-center mt-4">
                  We&apos;ll only email you about this feature launch. No spam, ever.
                </p>
              </div>
            ) : (
              <div className="max-w-md mx-auto text-center animate-scale-in">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-gold-primary to-gold-accent rounded-full flex items-center justify-center shadow-gold">
                  <CheckCircle className="w-10 h-10 text-royal-navy" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">
                  You&apos;re on the list! 🎉
                </h3>
                <p className="text-white/80 mb-6">
                  We&apos;ll email you at <span className="text-gold-primary font-semibold">{email}</span> when {feature.title} launches.
                </p>
                <button
                  onClick={() => router.push('/')}
                  className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
                >
                  Back to Home
                </button>
              </div>
            )}
          </div>

          {/* Bottom CTA */}
          {!isSubmitted && (
            <div className="text-center mt-8">
              <p className="text-white/60 mb-4">
                Want to explore what&apos;s available now?
              </p>
              <button
                onClick={() => router.push('/analyze?job=Software Engineer')}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 rounded-xl text-white/90 hover:text-white transition-all inline-flex items-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                <span>Try Free Career Analysis</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
