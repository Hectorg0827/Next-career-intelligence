'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, LogOut, User, Crown, Zap } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import Logo from '@/components/Logo';
import HowItWorksSection from '@/components/HowItWorksSection';
import TestimonialsCarousel from '@/components/TestimonialsCarousel';
import { useAuth } from '@/contexts/AuthContext';
import {
  staggerContainerVariants,
  staggerItemVariants,
  buttonVariants,
  fadeInUpVariants,
  scaleInVariants,
} from '@/lib/animations';

const marketPreviewData = [
  { month: 'Aug', value: 138 },
  { month: 'Sep', value: 142 },
  { month: 'Oct', value: 139 },
  { month: 'Nov', value: 151 },
  { month: 'Dec', value: 158 },
  { month: 'Jan', value: 167 },
  { month: 'Feb', value: 185 },
];

const tickerItems = [
  '47K+ careers analyzed',
  '92% match accuracy',
  '+28% avg salary increase',
  'GDPR compliant',
  '500+ company job feeds',
  '3-Layer AI intelligence',
  '47K+ careers analyzed',
  '92% match accuracy',
  '+28% avg salary increase',
  'GDPR compliant',
  '500+ company job feeds',
  '3-Layer AI intelligence',
];

export default function Home() {
  const router = useRouter();
  const { user, isAuthenticated, hasPremiumAccess, logout, isLoading } = useAuth();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [vis, setVis] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVis(true), 100);
    return () => clearTimeout(t);
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;
    setIsAnalyzing(true);
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleSubscriberAccess = () => {
    router.push('/dashboard');
  };

  const makeFade = (d: number) => ({
    opacity: vis ? 1 : 0,
    transform: vis ? 'translateY(0)' : 'translateY(28px)',
    transition: `all 0.8s cubic-bezier(0.16,1,0.3,1) ${d}s`,
  });

  return (
    <div className="min-h-screen bg-nci-bg text-white relative overflow-hidden">
      {/* Skip to main content */}
      <a href="#main-content" className="skip-to-main" aria-label="Skip to main content">
        Skip to main content
      </a>

      {/* Glow Orbs */}
      <div className="absolute -top-[15%] -left-[10%] w-[700px] h-[700px] rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(45,127,249,0.2), transparent 70%)', filter: 'blur(100px)' }} />
      <div className="absolute top-[60%] left-[70%] w-[500px] h-[500px] rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(0,210,182,0.15), transparent 70%)', filter: 'blur(100px)' }} />

      {/* Grid Background */}
      <div className="absolute inset-0 opacity-[0.015] pointer-events-none"
        style={{ backgroundImage: 'linear-gradient(rgba(74,76,94,1) 1px, transparent 1px), linear-gradient(90deg, rgba(74,76,94,1) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

      {/* Hero */}
      <main id="main-content" className="relative z-10 pt-32 pb-20 max-w-[1200px] mx-auto px-4 sm:px-8">
        {/* Subscriber Quick Access */}
        {!isLoading && hasPremiumAccess && (
          <motion.div className="mb-10" variants={fadeInUpVariants} initial="initial" animate="animate">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-nci-accent-dim">
                    <Crown className="w-6 h-6 text-nci-accent" />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-xl">Welcome back, {user?.name || 'Subscriber'}!</h3>
                    <p className="text-g-400 text-sm font-medium">Access your premium features</p>
                  </div>
                </div>
                <button
                  onClick={handleSubscriberAccess}
                  className="px-6 py-3 bg-white text-nci-bg font-bold rounded-xl transition-all flex items-center gap-2 hover:shadow-glass-lg"
                >
                  <Zap className="w-5 h-5" />
                  Go to Dashboard
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-[72px] items-center">
          {/* Left Column */}
          <div>
            {/* Badge */}
            <div style={makeFade(0.1)}>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nci-primary-dim border border-nci-primary/20 text-[11px] font-semibold text-nci-primary uppercase tracking-wide font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-nci-primary inline-block" />
                Live Market Intelligence
              </span>
            </div>

            {/* Logo */}
            <div style={makeFade(0.15)} className="mt-6 mb-4">
              <Logo size="lg" linkTo={undefined} className="" />
            </div>

            {/* Headline */}
            <h1 style={makeFade(0.2)} className="font-serif text-[clamp(2.5rem,5vw,3.625rem)] leading-[1.08] tracking-tight mb-6 font-normal">
              Your Career<br />is a Product.<br />
              <em className="italic text-gradient-primary">Manage It Like One.</em>
            </h1>

            {/* Subheadline */}
            <p style={makeFade(0.3)} className="text-[17px] leading-relaxed text-g-400 max-w-[460px] mb-9 font-light">
              Real-time market valuation, AI displacement analysis, and intelligent career matching — powered by data from 2.3M+ job postings.
            </p>

            {/* Search Form */}
            <form onSubmit={handleAnalyze} style={makeFade(0.35)} className="mb-8" role="search" aria-label="Career analysis search">
              <div className="glass-card flex flex-col sm:flex-row gap-3 p-3">
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Enter your job title (e.g., Software Engineer)"
                  className="input-glass flex-1 text-base"
                  disabled={isAnalyzing}
                  aria-label="Job title input"
                  aria-required="true"
                  id="job-title-input"
                  name="jobTitle"
                  autoComplete="organization-title"
                />
                <button
                  type="submit"
                  disabled={!jobTitle.trim() || isAnalyzing}
                  className="h-12 px-7 rounded-xl bg-white text-nci-bg font-bold text-sm transition-all hover:shadow-glass-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap"
                  aria-label={isAnalyzing ? 'Analyzing your career' : 'Calculate your market value'}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Calculate Market Value'}
                  {!isAnalyzing && <ArrowRight className="w-4 h-4" />}
                </button>
              </div>
            </form>

            {/* CTA Buttons */}
            <div style={makeFade(0.4)} className="flex flex-wrap gap-3">
              <button
                onClick={() => {
                  const section = document.getElementById('how-it-works');
                  section?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="h-12 px-6 rounded-xl bg-transparent text-g-300 border border-nci-border text-sm font-medium transition-all flex items-center gap-2 hover:border-nci-border-hover"
              >
                <span className="text-nci-accent">⚡</span> View Demo
              </button>
            </div>

            {/* Feature badges */}
            <div style={makeFade(0.45)} className="flex flex-wrap items-center gap-6 mt-8 text-g-400 text-sm">
              <div className="flex items-center gap-2 hover:text-white transition-colors">
                <Shield className="w-4 h-4 text-nci-accent" />
                <span>100% Free Analysis</span>
              </div>
              <div className="flex items-center gap-2 hover:text-white transition-colors">
                <Brain className="w-4 h-4 text-nci-primary" />
                <span>AI-Powered</span>
              </div>
              <div className="flex items-center gap-2 hover:text-white transition-colors">
                <TrendingUp className="w-4 h-4 text-nci-amber" />
                <span>Personalized Roadmap</span>
              </div>
            </div>
          </div>

          {/* Right Column - Preview Card */}
          <div style={makeFade(0.35)} className="hidden lg:block">
            <div className="glass-card overflow-hidden shadow-glass-xl">
              {/* Browser dots */}
              <div className="h-10 border-b border-nci-border bg-nci-bg/60 flex items-center px-3.5 gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-nci-red/40" />
                <div className="w-2.5 h-2.5 rounded-full bg-nci-amber/40" />
                <div className="w-2.5 h-2.5 rounded-full bg-nci-accent/40" />
                <span className="ml-3 text-[11px] text-g-600 font-mono">nextci.net/dashboard</span>
              </div>
              <div className="p-5">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <div className="text-[13px] font-semibold text-white">Market Value Pulse</div>
                    <div className="text-[11px] text-g-500">Real-time estimation</div>
                  </div>
                  <span className="text-[11px] font-semibold text-nci-accent bg-nci-accent-dim px-2.5 py-1 rounded-md">+31% Potential</span>
                </div>
                <div className="h-[140px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={marketPreviewData}>
                      <defs>
                        <linearGradient id="heroG" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#2D7FF9" stopOpacity={0.35} />
                          <stop offset="100%" stopColor="#2D7FF9" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <Area type="monotone" dataKey="value" stroke="#2D7FF9" strokeWidth={2.5} fill="url(#heroG)" dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-3 gap-2.5 mt-3">
                  <div className="bg-white/[0.03] rounded-lg p-2.5">
                    <div className="text-[10px] text-g-500 mb-1">Market Value</div>
                    <div className="text-base font-bold font-mono text-nci-accent">$185K</div>
                  </div>
                  <div className="bg-white/[0.03] rounded-lg p-2.5">
                    <div className="text-[10px] text-g-500 mb-1">AI Risk</div>
                    <div className="text-base font-bold font-mono text-nci-accent">Low 18%</div>
                  </div>
                  <div className="bg-white/[0.03] rounded-lg p-2.5">
                    <div className="text-[10px] text-g-500 mb-1">Top Match</div>
                    <div className="text-base font-bold font-mono text-nci-primary">96%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Ticker */}
        <div className="mt-20 border-t border-b border-nci-border py-5 overflow-hidden">
          <div className="flex gap-12 animate-ticker-scroll whitespace-nowrap">
            {tickerItems.map((t, i) => (
              <span key={i} className="text-[13px] text-g-500 flex-shrink-0">{t}</span>
            ))}
          </div>
        </div>
      </main>

      {/* How It Works Section */}
      <HowItWorksSection />

      {/* Testimonials Section */}
      <TestimonialsCarousel />

      {/* Final CTA Section */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="glass-card hover-reflect rounded-3xl p-12 relative overflow-hidden shadow-glass-xl">
            <div className="absolute inset-0 bg-gradient-to-br from-nci-primary/10 to-transparent opacity-50" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 font-serif">
                Ready to Future-Proof Your Career?
              </h2>
              <p className="text-xl md:text-2xl text-g-300 mb-8 max-w-2xl mx-auto leading-relaxed font-light">
                Get your free AI-powered career analysis now. No credit card required.
              </p>
              <button
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                  setTimeout(() => {
                    const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                    input?.focus();
                  }, 500);
                }}
                className="px-8 py-4 bg-white text-nci-bg font-bold text-lg rounded-xl transition-all shadow-glass-lg hover:shadow-glass-xl inline-flex items-center gap-2 group"
              >
                <Sparkles className="w-5 h-5" />
                <span>Start Your Free Analysis</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
