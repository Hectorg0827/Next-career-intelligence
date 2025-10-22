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
    <section className="relative min-h-screen bg-gradient-next-hero flex items-center justify-center overflow-hidden pt-20 pb-20">
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        {/* Gradient orbs */}
        <div className="absolute top-1/4 left-10 w-72 h-72 bg-next-gold/15 rounded-full blur-3xl animate-pulse-gold"></div>
        <div className="absolute bottom-1/3 right-10 w-96 h-96 bg-next-royal-blue/10 rounded-full blur-3xl"></div>
        
        {/* Animated gradient mesh */}
        <svg 
          className="absolute inset-0 w-full h-full opacity-20"
          style={{ transform: `translateY(${scrollY * 0.5}px)` }}
        >
          <defs>
            <linearGradient id="meshGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#CBA135" stopOpacity="0.3" />
              <stop offset="50%" stopColor="#1E3C78" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#0B1D45" stopOpacity="0.1" />
            </linearGradient>
          </defs>
          <circle cx="20%" cy="30%" r="300" fill="url(#meshGradient)" opacity="0.4" />
          <circle cx="80%" cy="70%" r="250" fill="url(#meshGradient)" opacity="0.3" />
        </svg>
      </div>

      <div className="container mx-auto px-4 max-w-6xl relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left column: Text & CTAs */}
          <div className="space-y-8">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-white/90 shadow-next-md hover:shadow-next-lg transition-shadow">
              <Sparkles className="w-4 h-4 text-next-gold animate-pulse-gold" />
              <span className="text-sm font-body">Powered by Advanced AI Intelligence</span>
            </div>

            {/* Main headline */}
            <div>
              <h1 className="text-6xl lg:text-7xl font-heading font-bold mb-4 text-white leading-tight">
                AI won&apos;t replace you
                <span className="block mt-2 bg-gradient-next-gold bg-clip-text text-transparent">
                  — if you evolve with it
                </span>
              </h1>
              
              <p className="text-xl text-white/80 font-body leading-relaxed max-w-2xl">
                Next analyzes your career path, detects automation risks, and builds a custom roadmap to your next opportunity.
              </p>
            </div>

            {/* Trust indicators */}
            <div className="space-y-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <p className="text-sm text-white/70 font-body">✓ Free AI Career Risk Scan</p>
              <p className="text-sm text-white/70 font-body">✓ Personalized job recommendations</p>
              <p className="text-sm text-white/70 font-body">✓ Real-time market intelligence</p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Link 
                href="/dashboard" 
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-next-gold hover:bg-next-gold-light text-next-deep-blue rounded-lg text-lg font-heading font-semibold transition-all shadow-next-gold hover:shadow-next-xl transform hover:scale-105 active:scale-95"
              >
                Find My Future
                <ArrowRight className="w-5 h-5" />
              </Link>
              
              <Link 
                href="/voice-coach" 
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white border border-white/30 rounded-lg text-lg font-heading font-semibold transition-all hover:shadow-next-md"
              >
                Try AI Coach
              </Link>
            </div>
          </div>

          {/* Right column: Visual/Animation */}
          <div className="relative h-96 lg:h-full hidden lg:block">
            {/* Animated silhouette with data visualization */}
            <div className="absolute inset-0 flex items-center justify-center">
              {/* Career transformation visualization */}
              <svg 
                viewBox="0 0 400 400" 
                className="w-full h-full max-w-md"
              >
                {/* Background circle */}
                <circle 
                  cx="200" 
                  cy="200" 
                  r="180" 
                  fill="none" 
                  stroke="url(#gradientStroke)" 
                  strokeWidth="2"
                  opacity="0.3"
                />
                
                {/* Gradient definition */}
                <defs>
                  <linearGradient id="gradientStroke" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#CBA135" stopOpacity="1" />
                    <stop offset="100%" stopColor="#1E3C78" stopOpacity="1" />
                  </linearGradient>
                  <linearGradient id="silhouetteGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#E5C158" stopOpacity="1" />
                    <stop offset="100%" stopColor="#CBA135" stopOpacity="0.7" />
                  </linearGradient>
                </defs>

                {/* Animated data lines */}
                <g opacity="0.4" className="animate-spin-slow">
                  <line x1="200" y1="30" x2="200" y2="100" stroke="#CBA135" strokeWidth="1" />
                  <line x1="200" y1="300" x2="200" y2="370" stroke="#CBA135" strokeWidth="1" />
                  <line x1="30" y1="200" x2="100" y2="200" stroke="#CBA135" strokeWidth="1" />
                  <line x1="300" y1="200" x2="370" y2="200" stroke="#CBA135" strokeWidth="1" />
                </g>

                {/* Central silhouette */}
                <g>
                  {/* Head */}
                  <circle cx="200" cy="120" r="30" fill="url(#silhouetteGradient)" />
                  
                  {/* Body */}
                  <rect 
                    x="175" 
                    y="155" 
                    width="50" 
                    height="60" 
                    rx="5"
                    fill="url(#silhouetteGradient)" 
                  />
                  
                  {/* Arms */}
                  <line x1="175" y1="170" x2="140" y2="180" stroke="url(#silhouetteGradient)" strokeWidth="6" strokeLinecap="round" />
                  <line x1="225" y1="170" x2="260" y2="180" stroke="url(#silhouetteGradient)" strokeWidth="6" strokeLinecap="round" />
                  
                  {/* Legs */}
                  <line x1="185" y1="215" x2="180" y2="280" stroke="url(#silhouetteGradient)" strokeWidth="6" strokeLinecap="round" />
                  <line x1="215" y1="215" x2="220" y2="280" stroke="url(#silhouetteGradient)" strokeWidth="6" strokeLinecap="round" />
                </g>

                {/* Animated ascending paths (career progression) */}
                <g className="animate-swoosh-slide opacity-0">
                  <path 
                    d="M 150 250 Q 180 200 220 150" 
                    fill="none" 
                    stroke="#CBA135" 
                    strokeWidth="2"
                  />
                  <circle cx="220" cy="150" r="8" fill="#CBA135" />
                </g>

                {/* Skill badges floating around */}
                <g opacity="0.6" className="animate-pulse-gold">
                  <rect x="280" y="100" width="80" height="30" rx="15" fill="#CBA135" opacity="0.2" />
                  <text x="320" y="120" textAnchor="middle" fill="#CBA135" fontSize="12" fontWeight="bold">
                    Leadership
                  </text>
                </g>

                <g opacity="0.5" className="animate-pulse-gold" style={{ animationDelay: '0.5s' }}>
                  <rect x="80" y="200" width="80" height="30" rx="15" fill="#1E3C78" opacity="0.3" />
                  <text x="120" y="220" textAnchor="middle" fill="#1E3C78" fontSize="12" fontWeight="bold">
                    Problem Solving
                  </text>
                </g>
              </svg>

              {/* Floating elements */}
              <div className="absolute top-8 right-8 bg-next-gold/10 backdrop-blur-sm rounded-lg p-4 border border-next-gold/20 animate-bounce" style={{ animationDuration: '3s' }}>
                <TrendingUp className="w-6 h-6 text-next-gold" />
              </div>

              <div className="absolute bottom-12 left-8 bg-next-royal-blue/10 backdrop-blur-sm rounded-lg p-4 border border-next-royal-blue/20 animate-bounce" style={{ animationDuration: '3.5s' }}>
                <Brain className="w-6 h-6 text-next-royal-blue" />
              </div>
            </div>
          </div>
        </div>

        {/* Bottom social proof */}
        <div className="mt-20 pt-12 border-t border-white/10">
          <p className="text-center text-sm text-white/60 font-body mb-8">
            Trusted by professionals from leading companies:
          </p>
          <div className="flex justify-center items-center gap-8 flex-wrap">
            {[
              { name: 'Google', opacity: 'opacity-70' },
              { name: 'Amazon', opacity: 'opacity-70' },
              { name: 'Deloitte', opacity: 'opacity-70' },
              { name: 'Microsoft', opacity: 'opacity-70' }
            ].map((company) => (
              <div 
                key={company.name}
                className={`text-white/50 font-body font-semibold text-sm ${company.opacity} hover:opacity-100 transition-opacity`}
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
