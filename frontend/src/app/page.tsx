'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, Crown, Zap } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import Logo from '@/components/Logo';
import HowItWorksSection from '@/components/HowItWorksSection';
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

export default function Home() {
  const router = useRouter();
  const { user, hasPremiumAccess, isLoading } = useAuth();
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

      {/* Minimal Header */}
      <header className="fixed top-0 inset-x-0 z-20 border-b border-white/5 backdrop-blur-xl bg-nci-bg/80">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-8 h-16 flex items-center justify-between">
          <Logo size="sm" linkTo="/" />
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push('/login')}
              className="text-sm font-medium text-g-300 hover:text-white transition-colors"
            >
              Sign in
            </button>
            <button
              onClick={() => {
                const input = document.getElementById('job-title-input') as HTMLInputElement | null;
                input?.focus();
              }}
              className="px-4 py-2 rounded-lg bg-white text-nci-bg text-sm font-semibold hover:shadow-glass-lg transition-all"
            >
              Get my free analysis
            </button>
          </div>
        </div>
      </header>

      {/* Glow Orbs */}
      <div className="absolute -top-[15%] -left-[10%] w-[700px] h-[700px] rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(45,127,249,0.2), transparent 70%)', filter: 'blur(100px)' }} />
      <div className="absolute top-[60%] left-[70%] w-[500px] h-[500px] rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(0,210,182,0.15), transparent 70%)', filter: 'blur(100px)' }} />

      {/* Grid Background */}
      <div className="absolute inset-0 opacity-[0.015] pointer-events-none"
        style={{ backgroundImage: 'linear-gradient(rgba(74,76,94,1) 1px, transparent 1px), linear-gradient(90deg, rgba(74,76,94,1) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

      {/* Hero */}
      <main id="main-content" className="relative z-10 pt-28 pb-20 max-w-[1200px] mx-auto px-4 sm:px-8">
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

            {/* Headline */}
            <h1 style={makeFade(0.2)} className="font-serif text-[clamp(2.4rem,4.6vw,3.4rem)] leading-[1.08] tracking-tight mb-6 font-semibold">
              Know your market value.<br />Reduce AI risk.<br />
              <span className="text-gradient-primary">Get a 90-day career plan.</span>
            </h1>

            {/* Subheadline */}
            <p style={makeFade(0.3)} className="text-[17px] leading-relaxed text-g-400 max-w-[520px] mb-6 font-light">
              Free analysis in 60 seconds using live job-market signals and skill demand data.
            </p>

            {/* Value bullets */}
            <div style={makeFade(0.32)} className="space-y-3 mb-8 text-sm text-g-300">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-4 h-4 text-nci-accent" />
                <span>Market value estimate with confidence range</span>
              </div>
              <div className="flex items-center gap-3">
                <Shield className="w-4 h-4 text-nci-primary" />
                <span>AI displacement risk with key drivers</span>
              </div>
              <div className="flex items-center gap-3">
                <Brain className="w-4 h-4 text-nci-amber" />
                <span>Next-best moves: skills, roles, and salary targets</span>
              </div>
            </div>

            {/* Search Form */}
            <form onSubmit={handleAnalyze} style={makeFade(0.35)} className="mb-4" role="search" aria-label="Career analysis search">
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
                  aria-label={isAnalyzing ? 'Analyzing your career' : 'Start free analysis'}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Start free analysis'}
                  {!isAnalyzing && <ArrowRight className="w-4 h-4" />}
                </button>
              </div>
            </form>
            <p style={makeFade(0.37)} className="text-xs text-g-500 mb-6">
              No credit card required. Takes ~60 seconds.
            </p>

            {/* CTA Buttons */}
            <div style={makeFade(0.4)} className="flex flex-wrap gap-3 items-center">
              <button
                onClick={() => {
                  const section = document.getElementById('how-it-works');
                  section?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="text-sm font-medium text-g-300 hover:text-white transition-colors inline-flex items-center gap-2"
              >
                Watch 60s demo <ArrowRight className="w-4 h-4" />
              </button>
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
                    <div className="text-[13px] font-semibold text-white">Career Intelligence Report</div>
                    <div className="text-[11px] text-g-500">Snapshot preview</div>
                  </div>
                  <span className="text-[11px] font-semibold text-nci-accent bg-nci-accent-dim px-2.5 py-1 rounded-md">Updated today</span>
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
      </main>

      {/* What You Get */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-semibold text-white text-center mb-10">
            Everything you need to make the next move
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                title: 'Market Value Pulse',
                description: 'Salary range, confidence, and demand trends tailored to your role.',
                icon: <TrendingUp className="w-5 h-5 text-nci-accent" />,
              },
              {
                title: 'AI Risk Breakdown',
                description: 'Clear risk level with the factors impacting your role.',
                icon: <Shield className="w-5 h-5 text-nci-primary" />,
              },
              {
                title: 'Personalized Roadmap',
                description: 'Skills, roles, and timelines to move you forward in 90 days.',
                icon: <Brain className="w-5 h-5 text-nci-amber" />,
              },
            ].map((card) => (
              <div key={card.title} className="glass-card p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center">
                    {card.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-white">{card.title}</h3>
                </div>
                <p className="text-sm text-g-400 leading-relaxed">{card.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <HowItWorksSection />

      {/* Proof Section */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <div className="glass-card p-8">
            <p className="text-lg text-white leading-relaxed mb-4">
              “NextCI gave me a precise market value and a plan I could execute in days. I landed two interviews in
              three weeks and negotiated a 22% increase.”
            </p>
            <p className="text-sm text-g-400">— Product Manager, Series B SaaS</p>
          </div>
          <div className="space-y-4">
            <div className="glass-card p-5 text-sm text-g-300">
              Privacy-first by design. GDPR-ready data handling and zero spam.
            </div>
            <div className="grid grid-cols-3 gap-3 text-xs text-g-500 uppercase tracking-wide">
              <div className="glass-card p-4 text-center">2.3M+ Jobs</div>
              <div className="glass-card p-4 text-center">92% Match</div>
              <div className="glass-card p-4 text-center">47K+ Reports</div>
            </div>
          </div>
        </div>
      </section>

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
