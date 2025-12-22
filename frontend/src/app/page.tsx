'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, useScroll, useTransform } from 'framer-motion';
import { 
  ArrowRight, 
  Sparkles, 
  TrendingUp, 
  Shield, 
  Brain, 
  Crown, 
  Zap, 
  CheckCircle2, 
  BarChart3, 
  Users, 
  Target, 
  Briefcase,
  Cpu,
  LineChart,
  Map,
  Quote
} from 'lucide-react';
import Logo from '@/components/Logo';
import { useAuth } from '@/contexts/AuthContext';
import {
  staggerContainerVariants,
  staggerItemVariants,
  fadeInUpVariants,
  scaleInVariants,
} from '@/lib/animations';

export default function Home() {
  const router = useRouter();
  const { user, isAuthenticated, hasPremiumAccess, isLoading } = useAuth();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;

    setIsAnalyzing(true);
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  const handleSubscriberAccess = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-premium-bg text-premium-text font-sans selection:bg-premium-accent/30 selection:text-premium-accent">
      {/* Background Effects */}
      <div className="premium-bg-gradient" />
      <div className="premium-grid-overlay" />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-[1.2fr_1fr] gap-12 items-center">
          <motion.div
            variants={staggerContainerVariants}
            initial="initial"
            animate="animate"
            className="relative z-10"
          >
            {/* Premium Badge */}
            {!isLoading && hasPremiumAccess && (
              <motion.div
                variants={fadeInUpVariants}
                className="mb-8 inline-block"
              >
                <div className="premium-card p-4 border-premium-accent/40 bg-premium-accent/5 flex items-center gap-4">
                  <div className="p-2 bg-premium-accent/20 rounded-full">
                    <Crown className="w-5 h-5 text-premium-accent" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">Welcome back, {user?.name || 'Subscriber'}!</p>
                    <button 
                      onClick={handleSubscriberAccess}
                      className="text-xs text-premium-accent hover:underline font-medium flex items-center gap-1"
                    >
                      Go to Premium Dashboard <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            <motion.div variants={fadeInUpVariants} className="inline-flex items-center gap-2 px-4 py-2 bg-premium-accent/10 border border-premium-accent/20 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-premium-accent" />
              <span className="text-[10px] font-bold tracking-[0.2em] uppercase text-premium-accent">Enterprise-Grade Career Intelligence</span>
            </motion.div>

            <motion.h1 
              variants={fadeInUpVariants}
              className="premium-heading text-5xl md:text-7xl mb-6"
            >
              Navigate Your Career <br />
              <span className="text-white">in the Age of AI</span>
            </motion.h1>

            <motion.p 
              variants={fadeInUpVariants}
              className="text-xl text-premium-text-muted mb-10 max-w-2xl leading-relaxed"
            >
              Enterprise-grade career intelligence powered by adaptive AI. Get data-driven insights on automation risk, skill gaps, and strategic career moves.
            </motion.p>

            <motion.div variants={fadeInUpVariants} className="flex flex-wrap gap-4 mb-10">
              {[
                { icon: Shield, text: 'Enterprise Security' },
                { icon: CheckCircle2, text: 'Research-Backed' },
                { icon: Brain, text: 'Privacy First' }
              ].map((badge, i) => (
                <div key={i} className="flex items-center gap-2 bg-premium-accent/5 border border-premium-accent/10 px-4 py-2 rounded-full">
                  <badge.icon className="w-4 h-4 text-premium-accent" />
                  <span className="text-sm font-medium text-premium-text-muted">{badge.text}</span>
                </div>
              ))}
            </motion.div>

            <motion.form 
              variants={fadeInUpVariants}
              onSubmit={handleAnalyze}
              className="flex flex-col sm:flex-row gap-4 max-w-xl"
            >
              <input 
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Enter your job title..."
                className="flex-1 bg-premium-secondary/40 border border-premium-accent/20 rounded-xl px-6 py-4 text-white placeholder:text-premium-text-muted focus:outline-none focus:border-premium-accent transition-all"
              />
              <button 
                type="submit"
                disabled={isAnalyzing || !jobTitle.trim()}
                className="premium-btn-primary flex items-center justify-center gap-2 whitespace-nowrap disabled:opacity-50"
              >
                {isAnalyzing ? 'Analyzing...' : 'Get Free Analysis'}
                {!isAnalyzing && <ArrowRight className="w-5 h-5" />}
              </button>
            </motion.form>
          </motion.div>

          {/* Analysis Card Preview */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="relative hidden lg:block"
          >
            <div className="premium-card p-8 animate-float relative z-10">
              <div className="flex justify-between items-center mb-8">
                <h3 className="font-serif text-2xl text-premium-accent">Live Career Analysis</h3>
                <div className="px-3 py-1 bg-premium-accent/10 border border-premium-accent/20 rounded-full text-[10px] font-bold text-premium-accent uppercase tracking-wider">Real-time Data</div>
              </div>

              <div className="mb-8">
                <div className="flex justify-between text-sm mb-3">
                  <span className="text-premium-text-muted">Automation Risk Assessment</span>
                  <span className="font-bold text-premium-warning">67% Medium Risk</span>
                </div>
                <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-premium-success via-premium-warning to-premium-danger animate-fill-risk" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'Skills at Risk', value: '8', color: 'text-premium-danger' },
                  { label: 'Growth Skills', value: '12', color: 'text-premium-success' },
                  { label: 'Salary Potential', value: '+35%', color: 'text-premium-accent' },
                  { label: 'Years to Master', value: '4.2', color: 'text-premium-text' }
                ].map((stat, i) => (
                  <div key={i} className="bg-premium-accent/5 border border-premium-accent/10 p-4 rounded-xl">
                    <div className={`font-serif text-3xl font-bold ${stat.color} mb-1`}>{stat.value}</div>
                    <div className="text-xs text-premium-text-muted uppercase tracking-wider">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Decorative elements */}
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-premium-accent/20 rounded-full blur-[80px]" />
            <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-premium-accent-warm/10 rounded-full blur-[80px]" />
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-4 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="premium-heading text-4xl md:text-6xl mb-6"
            >
              Career Intelligence <br />
              <span className="text-white">That Adapts</span>
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-xl text-premium-text-muted"
            >
              Our multi-agent AI system analyzes thousands of labor market signals, automation trends, and skill dynamics to deliver actionable career intelligence.
            </motion.p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Cpu,
                title: 'Automation Risk Scoring',
                desc: 'Proprietary algorithms analyze your role against 15,000+ automation patterns. Get granular task-level risk assessment.'
              },
              {
                icon: Target,
                title: 'Skill Gap Analysis',
                desc: 'Real-time comparison of your skillset against emerging market demands. Prioritized learning paths with ROI calculations.'
              },
              {
                icon: Map,
                title: 'Career Path Simulation',
                desc: 'Model different career trajectories with salary projections, stability scores, and market demand forecasts.'
              },
              {
                icon: LineChart,
                title: 'Market Intelligence',
                desc: 'Live tracking of 2.3M+ job postings, salary trends, and skill demand shifts across all major industries.'
              },
              {
                icon: Brain,
                title: 'AI Skills Optimization',
                desc: 'Learn which AI tools amplify your role vs. automate it. Personalized recommendations on AI literacy.'
              },
              {
                icon: Zap,
                title: 'Personalized Roadmaps',
                desc: '90-day action plans with concrete milestones, resource recommendations, and progress tracking.'
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="premium-card p-8 group hover:border-premium-accent transition-all duration-500"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-premium-accent to-[#0099CC] rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                  <feature.icon className="w-7 h-7 text-premium-primary" />
                </div>
                <h3 className="font-serif text-2xl mb-4 text-white">{feature.title}</h3>
                <p className="text-premium-text-muted leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-32 px-4 bg-premium-primary/30 relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <h2 className="premium-heading text-4xl md:text-6xl mb-6">From Analysis to Action</h2>
            <p className="text-xl text-premium-text-muted">Our multi-agent system delivers comprehensive career intelligence in minutes, not months.</p>
          </div>

          <div className="relative max-w-4xl mx-auto">
            {/* Timeline Line */}
            <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-premium-accent to-transparent hidden md:block" />

            {[
              {
                step: '1',
                title: 'Role Analysis Agent',
                desc: 'Input your job title and industry. Our system decomposes your role into 50+ discrete tasks, analyzing each for automation susceptibility.'
              },
              {
                step: '2',
                title: 'Market Intelligence Agent',
                desc: 'Real-time scanning of job market dynamics, salary trajectories, and skill demand signals across 2.3M+ active postings.'
              },
              {
                step: '3',
                title: 'Skills Assessment Agent',
                desc: 'Identifies critical skill gaps and growth opportunities. Calculates ROI for each learning path based on market value.'
              },
              {
                step: '4',
                title: 'Strategic Planning Agent',
                desc: 'Synthesizes insights into actionable roadmaps. Generates multiple career scenarios with probability-weighted outcomes.'
              }
            ].map((item, i) => (
              <div key={i} className={`flex flex-col md:flex-row items-center gap-8 mb-16 ${i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}>
                <div className="flex-1 w-full">
                  <motion.div 
                    initial={{ opacity: 0, x: i % 2 === 0 ? -50 : 50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    className="premium-card p-8"
                  >
                    <h3 className="font-serif text-2xl text-premium-accent mb-4">{item.title}</h3>
                    <p className="text-premium-text-muted leading-relaxed">{item.desc}</p>
                  </motion.div>
                </div>
                <div className="relative z-10">
                  <div className="w-16 h-16 bg-gradient-to-br from-premium-accent to-[#0099CC] rounded-full flex items-center justify-center font-serif text-2xl font-bold text-premium-primary shadow-[0_0_30px_rgba(0,217,255,0.3)]">
                    {item.step}
                  </div>
                </div>
                <div className="flex-1 hidden md:block" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-32 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { label: 'Careers Analyzed', value: '47K+' },
              { label: 'Identify New Opportunities', value: '92%' },
              { label: 'Average Salary Increase', value: '+28%' },
              { label: 'Platform Rating', value: '4.8/5' }
            ].map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="premium-card p-8 text-center"
              >
                <div className="font-serif text-4xl md:text-5xl font-bold bg-gradient-to-br from-premium-accent to-premium-accent-warm bg-clip-text text-transparent mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-premium-text-muted uppercase tracking-widest font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-32 px-4 bg-premium-primary/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <h2 className="premium-heading text-4xl md:text-6xl mb-6">Real Impact, Real Careers</h2>
            <p className="text-xl text-premium-text-muted">See how professionals are using NextCI to stay ahead.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "NextCI's automation risk analysis was eye-opening. I pivoted to ML engineering before my data analyst role became commoditized.",
                author: "Sarah Chen",
                role: "ML Engineer, Tech Corp",
                initials: "SC"
              },
              {
                quote: "The skill gap analysis was incredibly precise. Instead of random courses, I focused on high-ROI skills. Transitioned in 8 months.",
                author: "Marcus Rodriguez",
                role: "Growth Strategist, Startup",
                initials: "MR"
              },
              {
                quote: "As a finance professional, I was skeptical about AI impact. NextCI showed me exactly which tasks were at risk. Game changer.",
                author: "Aisha Patel",
                role: "Senior Financial Analyst",
                initials: "AP"
              }
            ].map((t, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="premium-card p-8 relative"
              >
                <Quote className="w-12 h-12 text-premium-accent opacity-20 mb-4" />
                <p className="text-lg text-white mb-8 leading-relaxed italic">"{t.quote}"</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-premium-accent to-premium-accent-warm rounded-full flex items-center justify-center font-bold text-premium-primary">
                    {t.initials}
                  </div>
                  <div>
                    <div className="font-bold text-white">{t.author}</div>
                    <div className="text-sm text-premium-text-muted">{t.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section id="analyze" className="py-32 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="premium-card p-12 md:p-20 text-center relative overflow-hidden border-2 border-premium-accent"
          >
            {/* Rotating background glow */}
            <div className="absolute inset-0 -z-10 animate-rotate-slow opacity-20">
              <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle,rgba(0,217,255,0.3)_0%,transparent_70%)]" />
            </div>

            <h2 className="premium-heading text-4xl md:text-6xl mb-8">Start Your Career <br /> Intelligence Analysis</h2>
            <p className="text-xl text-premium-text-muted mb-12 max-w-2xl mx-auto">
              Get a comprehensive report on automation risk, skill gaps, and strategic career moves. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button 
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="premium-btn-primary"
              >
                Analyze My Career Free
              </button>
              <button 
                onClick={() => router.push('/pricing')}
                className="premium-btn-secondary"
              >
                View Enterprise Plans
              </button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
