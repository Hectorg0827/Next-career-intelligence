'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  Sparkles,
  TrendingUp,
  Shield,
  Brain,
  LogOut,
  User,
  Crown,
  Zap,
  CheckCircle2
} from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import Logo from '@/components/Logo';
import { useAuth } from '@/contexts/AuthContext';
import ParticleBackground from '@/components/ParticleBackground';
import { fadeInUpVariants } from '@/lib/animations';
import ResumeUpload from '@/components/ResumeUpload';

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
  '300M+ Jobs impacted by 2030',
  '44% Core skills disrupted',
  '$15.7T AI Economic contribution',
  '85% of 2030 jobs don\'t exist yet',
  '300M+ Jobs impacted by 2030',
  '44% Core skills disrupted',
  '$15.7T AI Economic contribution',
  '85% of 2030 jobs don\'t exist yet',
];

export default function Home() {
  const router = useRouter();
  const { user, isAuthenticated, hasPremiumAccess, logout, isLoading } = useAuth();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;
    setIsAnalyzing(true);
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  const scrollToFunnel = () => {
    const input = document.getElementById('job-title-input');
    input?.focus();
    input?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  return (
    <div className="min-h-screen bg-nci-bg text-white relative selection:bg-nci-primary/30 overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[80vh] md:min-h-[90vh] flex items-center pt-24 overflow-hidden">
        <ParticleBackground />

        {/* Ambient Glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-full max-w-4xl h-96 bg-nci-primary/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="container relative z-10 mx-auto px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="mb-6 md:mb-10">
                <Logo size="md" linkTo={undefined} className="opacity-90" />
              </div>

              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-nci-primary-dim text-[11px] font-bold text-nci-primary uppercase tracking-widest mb-4 md:mb-8">
                <span className="w-1 h-1 rounded-full bg-nci-primary animate-pulse" />
                AI Career Intelligence 2.0
              </div>

              <h1 className="font-serif text-4xl sm:text-5xl lg:text-[clamp(3.5rem,6vw,5rem)] leading-[0.95] mb-6 md:mb-8 tracking-tighter">
                The Future of Work is Already Here. <br />
                <span className="italic text-gradient-primary">Master It.</span>
              </h1>

              <p className="text-g-400 text-base sm:text-lg md:text-xl max-w-lg mb-8 md:mb-10 font-light leading-relaxed">
                AI is redefining 1.28B roles globally. Don't just watch it happen. Get your displacement risk score and build your data-driven roadmap to the top.
              </p>

              <div className="flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4">
                <button
                  onClick={scrollToFunnel}
                  className="px-6 sm:px-8 py-3 sm:py-4 bg-nci-primary text-white font-bold rounded-xl transition-all hover:scale-[1.02] hover:shadow-glow-blue flex items-center justify-center gap-2 group"
                >
                  Calculate My Risk — Free
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="px-6 sm:px-8 py-3 sm:py-4 bg-white/5 text-white font-bold rounded-xl transition-all hover:bg-white/10 flex items-center justify-center gap-2">
                  <Zap className="w-5 h-5 text-nci-amber" />
                  Watch Demo
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95, rotateY: 10 }}
              animate={{ opacity: 1, scale: 1, rotateY: 0 }}
              transition={{ duration: 1, delay: 0.2 }}
              className="relative hidden lg:block"
            >
              <div className="glass-card p-2 shadow-glass-xl overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-nci-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <img
                  src="/nextci_dashboard_mockup_1770496376961.png"
                  alt="NextCI Dashboard"
                  className="rounded-lg shadow-2xl relative z-10"
                />
              </div>

              {/* Floating Stat Card */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -bottom-6 -left-6 glass-card p-4 bg-nci-bg/80 backdrop-blur-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-nci-accent-dim flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-nci-accent" />
                  </div>
                  <div>
                    <div className="text-[10px] text-g-500 font-bold uppercase tracking-wider">Market Value</div>
                    <div className="text-lg font-bold font-mono">$185,000</div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Ticker */}
      <div className="gradient-trim-y gradient-trim-top gradient-trim-bottom py-4 bg-nci-surface/30 backdrop-blur-sm overflow-hidden">
        <div className="flex gap-12 animate-ticker-scroll whitespace-nowrap px-4">
          {tickerItems.map((item, i) => (
            <div key={i} className="flex items-center gap-3 text-[13px] font-medium text-g-400">
              <span className="w-1 h-1 rounded-full bg-nci-accent" />
              {item}
            </div>
          ))}
        </div>
      </div>

      {/* Data Section */}
      <section className="py-16 sm:py-24 md:py-40 px-4 sm:px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12 md:mb-24">
            <span className="text-nci-primary font-bold uppercase tracking-[0.2em] text-xs mb-4 block">The Global Shift</span>
            <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl lg:text-6xl mb-4 md:mb-6">Data-Driven Career Protection</h2>
            <p className="text-g-400 text-base sm:text-lg max-w-2xl mx-auto font-light">We aggregate labor market data to give you the most accurate career forecast available.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 md:gap-10">
            {[
              { val: '300', label: 'Million Jobs Exposed', sub: 'Roles vulnerable to automation by 2030.' },
              { val: '97', label: 'Million New Roles', sub: 'Opportunities emerging for AI careers.' },
              { val: '12', label: 'Months to Upskill', sub: 'The critical window for future-proofing.' }
            ].map((stat, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -5 }}
                className="glass-card p-6 sm:p-8 md:p-10 flex flex-col items-center text-center"
              >
                <div className="font-serif text-4xl sm:text-5xl md:text-6xl font-bold mb-4">{stat.val}</div>
                <div className="text-nci-primary font-bold mb-3">{stat.label}</div>
                <p className="text-g-500 text-sm font-light leading-relaxed">{stat.sub}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Tool Row 1 */}
      <section className="py-12 sm:py-16 md:py-24 px-4 sm:px-6 overflow-hidden">
        <div className="container mx-auto max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-20 items-center">
            <div>
              <span className="text-nci-accent font-bold text-xs tracking-widest uppercase mb-4 block">Tool 01</span>
              <h3 className="font-serif text-3xl sm:text-4xl md:text-5xl mb-4 md:mb-6">AI Displacement Risk Engine</h3>
              <p className="text-g-400 text-base sm:text-lg mb-6 md:mb-8 font-light leading-relaxed">
                Understand exactly which parts of your role are at risk. Our engine breaks down your job into 15+ core competencies and evaluates them against AI capabilities.
              </p>
              <ul className="space-y-4">
                {['Task-level exposure analysis', 'Industry benchmarking', 'Real-time risk monitoring'].map((feat, i) => (
                  <li key={i} className="flex items-center gap-3 text-g-300">
                    <CheckCircle2 className="w-5 h-5 text-nci-accent flex-shrink-0" />
                    {feat}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-4 sm:rotate-2 hover:rotate-0 transition-transform duration-500">
              <img src="/nextci_risk_meter_1770496391987.png" alt="Risk Meter" className="rounded-xl shadow-2xl" />
            </div>
          </div>
        </div>
      </section>

      {/* Tool Row 2 (Job Matching) */}
      <section className="py-12 sm:py-16 md:py-24 px-4 sm:px-6 bg-nci-surface/20">
        <div className="container mx-auto max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-20 items-center">
            <div className="order-2 lg:order-1">
              <div className="glass-card p-4 sm:p-8 space-y-4 sm:-rotate-2 hover:rotate-0 transition-transform duration-500">
                {[
                  { title: 'AI Operations Lead', co: 'Stripe', pay: '$180k - $240k', score: 98 },
                  { title: 'Automation Strategist', co: 'Scale AI', pay: '$165k - $210k', score: 94 }
                ].map((job, i) => (
                  <div key={i} className="glass-card flex items-center gap-3 sm:gap-6 p-3 sm:p-4">
                    <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-nci-accent-dim flex items-center justify-center font-bold text-nci-accent text-lg sm:text-xl flex-shrink-0">
                      {job.score}
                    </div>
                    <div className="relative z-10 min-w-0">
                      <h4 className="font-bold text-white text-sm sm:text-base">{job.title}</h4>
                      <p className="text-g-500 text-xs sm:text-sm">{job.co} · {job.pay}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <span className="text-nci-primary font-bold text-xs tracking-widest uppercase mb-4 block">Tool 02</span>
              <h3 className="font-serif text-3xl sm:text-4xl md:text-5xl mb-4 md:mb-6">Smart Job Matching</h3>
              <p className="text-g-400 text-base sm:text-lg mb-6 md:mb-8 font-light leading-relaxed">
                Stop applying to the past. Find roles designed for the future. Our matching engine prioritizes AI-augmented roles with long-term stability.
              </p>
              <ul className="space-y-4">
                {['Future-proof stability scoring', 'Hidden market intelligence', 'Salary trajectory forecasting'].map((feat, i) => (
                  <li key={i} className="flex items-center gap-3 text-g-300">
                    <CheckCircle2 className="w-5 h-5 text-nci-primary flex-shrink-0" />
                    {feat}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Final Funnel Section */}
      <section className="py-16 sm:py-24 md:py-40 px-4 sm:px-6">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl lg:text-7xl mb-6 md:mb-8 tracking-tighter">
            The Future Won't Wait. <br />
            <span className="text-gradient-primary italic">Neither Should You.</span>
          </h2>
          <p className="text-g-400 text-base sm:text-lg md:text-xl mb-8 md:mb-12 font-light">Join 50,000+ professionals using NextCI to outpace the AI revolution.</p>

          <div className="glass-card p-6 sm:p-8 md:p-12 relative overflow-hidden transition-all duration-500">
            <div className="absolute inset-0 bg-gradient-to-br from-nci-primary/5 to-transparent pointer-events-none" />
            <div className="relative z-10">
              <h3 className="text-xl sm:text-2xl font-bold mb-2">Calculate Your Risk Score</h3>
              <p className="text-g-500 mb-6 md:mb-8 text-sm sm:text-base">Enter your current role or upload your resume to begin.</p>

              <div className="flex justify-center mb-8 md:mb-12">
                <div className="inline-flex bg-white/5 p-1 rounded-full relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-r from-nci-primary/20 via-nci-accent/20 to-nci-primary/20 opacity-50" />
                  <button
                    onClick={() => setShowUpload(false)}
                    className={`relative z-10 px-4 sm:px-8 py-2.5 sm:py-3 rounded-full text-xs sm:text-sm font-medium transition-all ${!showUpload ? 'bg-nci-primary text-white shadow-lg' : 'text-g-400 hover:text-white hover:bg-white/5'}`}
                  >
                    Enter Job Title
                  </button>
                  <button
                    onClick={() => setShowUpload(true)}
                    className={`relative z-10 px-4 sm:px-8 py-2.5 sm:py-3 rounded-full text-xs sm:text-sm font-medium transition-all ${showUpload ? 'bg-nci-primary text-white shadow-lg' : 'text-g-400 hover:text-white hover:bg-white/5'}`}
                  >
                    Upload Resume
                  </button>
                </div>
              </div>

              {showUpload ? (
                <div className="max-w-xl mx-auto animate-in fade-in zoom-in duration-300">
                  <ResumeUpload
                    onUploadStart={() => setIsAnalyzing(true)}
                    onUploadComplete={(detectedTitle) => {
                      setIsAnalyzing(false);
                      router.push(`/analyze?job=${encodeURIComponent(detectedTitle)}`);
                    }}
                    onError={() => setIsAnalyzing(false)}
                  />
                </div>
              ) : (
                <form onSubmit={handleAnalyze} className="flex flex-col sm:flex-row gap-4 sm:gap-6 max-w-3xl mx-auto animate-in fade-in zoom-in duration-300 items-center">
                  <div className="flex-1 w-full relative group">
                    <input
                      id="job-title-input"
                      type="text"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      placeholder="e.g. Senior Product Manager"
                      className="glass-input w-full h-[52px] sm:h-[60px] text-base sm:text-lg px-4 sm:px-6"
                    />
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-g-500 group-focus-within:text-nci-primary transition-colors">
                      <User className="w-5 h-5" />
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={!jobTitle.trim() || isAnalyzing}
                    className="w-full sm:w-auto px-8 h-[52px] sm:h-[60px] bg-gradient-to-r from-nci-primary to-nci-primary/80 text-white font-bold rounded-xl transition-all hover:scale-105 hover:shadow-glow-blue disabled:opacity-50 whitespace-nowrap sm:min-w-[160px]"
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Now'}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Simple Footer */}
      <footer className="py-12 pb-28 md:pb-12 border-t border-nci-border text-center">
        <div className="mb-6 opacity-60 grayscale hover:grayscale-0 transition-all inline-block">
          <Logo size="sm" />
        </div>
        <p className="text-g-600 text-xs tracking-widest uppercase">© 2026 Next Career Intelligence. All rights reserved.</p>
      </footer>
    </div>
  );
}
