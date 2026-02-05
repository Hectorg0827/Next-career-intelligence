import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Sparkles, ArrowRight, TrendingUp, Shield, Brain, Zap } from 'lucide-react';

export const EnhancedHeroSection = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <section className="relative min-h-screen bg-white flex items-center justify-center overflow-hidden pt-20 pb-20">

      <div className="container mx-auto px-4 max-w-6xl relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left column: Text & CTAs */}
          <div className="space-y-8">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 border border-gray-200 rounded-full text-slate-700 transition-shadow">
              <Sparkles className="w-4 h-4 text-blue-500" />
              <span className="text-sm">Powered by Advanced AI Intelligence</span>
            </div>

            {/* Main headline */}
            <div>
              <h1 className="text-5xl font-bold tracking-tight text-slate-900 mb-4">
                AI won&apos;t replace you — if you evolve with it
              </h1>
              
              <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                Next analyzes your career path, detects automation risks, and builds a custom roadmap to your next opportunity.
              </p>
            </div>

            {/* Trust indicators */}
            <div className="space-y-3 bg-white border border-gray-200 rounded-xl p-6">
              <p className="text-sm text-slate-700">✓ Free AI Career Risk Scan</p>
              <p className="text-sm text-slate-700">✓ Personalized job recommendations</p>
              <p className="text-sm text-slate-700">✓ Real-time market intelligence</p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Link 
                href="/dashboard" 
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-lg font-semibold transition-all shadow-md hover:shadow-lg"
              >
                Find My Future
                <ArrowRight className="w-5 h-5" />
              </Link>
              
              <Link 
                href="/voice-coach" 
                className="inline-flex items-center justify-center gap-2 px-8 py-4 text-slate-600 hover:text-slate-900 rounded-lg text-lg font-semibold transition-colors"
              >
                Try AI Coach
              </Link>
            </div>
          </div>


        </div>

        {/* Bottom social proof */}
        <div className="mt-20 pt-12 border-t border-gray-200">
          <p className="text-center text-sm text-slate-500 mb-8">
            Trusted by professionals from leading companies:
          </p>
          <div className="flex justify-center items-center gap-8 flex-wrap">
            {[
              { name: 'Google' },
              { name: 'Amazon' },
              { name: 'Deloitte' },
              { name: 'Microsoft' }
            ].map((company) => (
              <div 
                key={company.name}
                className="text-slate-400 font-semibold text-sm hover:text-slate-700 transition-colors"
              >
                {company.name}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default EnhancedHeroSection;
