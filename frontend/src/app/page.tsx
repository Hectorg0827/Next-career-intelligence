'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, LogOut, User, Crown, Zap } from 'lucide-react';
import Logo from '@/components/Logo';
import HowItWorksSection from '@/components/HowItWorksSection';
import TestimonialsCarousel from '@/components/TestimonialsCarousel';
import StatsSection from '@/components/StatsSection';
import { useAuth } from '@/contexts/AuthContext';
import {
  staggerContainerVariants,
  staggerItemVariants,
  buttonVariants,
  fadeInUpVariants,
  scaleInVariants,
} from '@/lib/animations';

export default function Home() {
  const router = useRouter();
  const { user, isAuthenticated, hasPremiumAccess, logout, isLoading } = useAuth();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

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

  return (
    <div className="min-h-screen gradient-dark-glass relative overflow-hidden">
      {/* Skip to main content link for keyboard navigation */}
      <a
        href="#main-content"
        className="skip-to-main"
        aria-label="Skip to main content"
      >
        Skip to main content
      </a>

      {/* Top Right - Login/Logout */}
      <nav className="absolute top-6 right-6 z-20 flex items-center gap-4" aria-label="User account navigation">
        {!isLoading && isAuthenticated && user ? (
          <>
            <div
              className="glass-pill"
              role="status"
              aria-label={`Logged in as ${user.email}${hasPremiumAccess ? ', Premium subscriber' : ''}`}
            >
              <User className="w-4 h-4 text-accent-400 inline mr-2" aria-hidden="true" />
              <span className="text-white text-sm font-medium">{user.email}</span>
              {hasPremiumAccess && <Crown className="w-4 h-4 text-accent-400 inline ml-2" aria-label="Premium subscriber" />}
            </div>
            <button
              onClick={handleLogout}
              className="glass-pill hover:bg-glass-edge transition-all group"
              aria-label="Log out of your account"
            >
              <LogOut className="w-4 h-4 text-ink-200 group-hover:text-white inline mr-2" aria-hidden="true" />
              <span className="text-ink-200 group-hover:text-white text-sm font-medium">Logout</span>
            </button>
          </>
        ) : !isLoading ? (
          <button
            onClick={() => router.push('/login')}
            className="primary-btn flex items-center gap-2"
            aria-label="Sign in to your account"
          >
            <User className="w-5 h-5" aria-hidden="true" />
            <span>Sign In</span>
          </button>
        ) : null}
      </nav>

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden opacity-30">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent-500 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-500/60 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-accent-400/40 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <main id="main-content" className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12">
        <motion.div 
          className="max-w-4xl w-full text-center"
          variants={staggerContainerVariants}
          initial="initial"
          animate="animate"
          role="region"
          aria-label="Hero section"
        >
          {/* Subscriber Quick Access Section */}
          {!isLoading && hasPremiumAccess && (
            <motion.div
              className="mb-8"
              variants={fadeInUpVariants}
            >
              <div className="glass-card hover-reflect p-6 shadow-glass-lg">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <motion.div
                      className="p-3 bg-accent-500/20 rounded-full"
                      whileHover={{ rotate: [0, -10, 10, -10, 0], transition: { duration: 0.5 } }}
                    >
                      <Crown className="w-6 h-6 text-accent-400" />
                    </motion.div>
                    <div className="text-left">
                      <h3 className="text-white font-semibold text-lg">Welcome back, {user?.name || 'Subscriber'}!</h3>
                      <p className="text-ink-300 text-sm">Access your premium features</p>
                    </div>
                  </div>
                  <motion.button
                    onClick={handleSubscriberAccess}
                    className="primary-btn flex items-center gap-2"
                    variants={buttonVariants}
                    whileHover="hover"
                    whileTap="tap"
                  >
                    <Zap className="w-5 h-5" />
                    Go to Dashboard
                    <ArrowRight className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}

          {/* NEXT Logo */}
          <motion.div 
            className="mb-8"
            variants={scaleInVariants}
          >
            <Logo size="lg" linkTo={undefined} className="mx-auto" />
          </motion.div>

          <motion.div
            className="glass-pill inline-flex items-center gap-2 mb-8"
            variants={staggerItemVariants}
            role="status"
            aria-label="AI-powered analysis available"
          >
            <Sparkles className="w-4 h-4 text-accent-400" aria-hidden="true" />
            <span className="text-white text-sm font-medium">Powered by AI</span>
          </motion.div>

          <motion.h1 
            className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight"
            variants={staggerItemVariants}
          >
            Is Your Job
            <span className="block bg-gradient-to-r from-accent-500 via-accent-400 to-accent-500 bg-clip-text text-transparent">
              AI-Proof?
            </span>
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-ink-200 mb-12 max-w-2xl mx-auto"
            variants={staggerItemVariants}
          >
            Get a free AI-powered analysis of your career&apos;s automation risk and discover skills that future-proof your career
          </motion.p>

          <motion.form 
            onSubmit={handleAnalyze} 
            className="max-w-2xl mx-auto mb-8"
            variants={staggerItemVariants}
            role="search"
            aria-label="Career analysis search"
          >
            <div className="glass-card flex flex-col sm:flex-row gap-4 p-3 shadow-glass-xl">
              <motion.input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Enter your job title (e.g., Software Engineer)"
                className="input-glass flex-1 text-lg"
                disabled={isAnalyzing}
                whileFocus={{ scale: 1.01 }}
                transition={{ duration: 0.2 }}
                aria-label="Job title input"
                aria-required="true"
                aria-invalid={!jobTitle.trim() && "true"}
                id="job-title-input"
                name="jobTitle"
                autoComplete="organization-title"
              />
              <motion.button
                type="submit"
                disabled={!jobTitle.trim() || isAnalyzing}
                className="primary-btn disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap"
                variants={buttonVariants}
                whileHover="hover"
                whileTap="tap"
                aria-label={isAnalyzing ? 'Analyzing your career' : 'Start free career analysis'}
                aria-disabled={!jobTitle.trim() || isAnalyzing}
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Free'}
                {!isAnalyzing && <ArrowRight className="w-5 h-5" aria-hidden="true" />}
              </motion.button>
            </div>
          </motion.form>

          <motion.div
            className="flex flex-wrap items-center justify-center gap-8 text-ink-300 text-sm mb-16"
            variants={staggerItemVariants}
            role="list"
            aria-label="Key features"
          >
            <motion.div
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              role="listitem"
            >
              <Shield className="w-4 h-4 text-accent-400" aria-hidden="true" />
              <span>100% Free Analysis</span>
            </motion.div>
            <motion.div
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              role="listitem"
            >
              <Brain className="w-4 h-4 text-accent-400" aria-hidden="true" />
              <span>AI-Powered Insights</span>
            </motion.div>
            <motion.div
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              role="listitem"
            >
              <TrendingUp className="w-4 h-4 text-accent-400" aria-hidden="true" />
              <span>Personalized Roadmap</span>
            </motion.div>
          </motion.div>

        </motion.div>

        <motion.nav 
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          aria-label="Secondary navigation"
        >
          <p className="text-ink-400 text-sm mb-4">
            Join thousands of professionals taking control of their careers
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <motion.button
              onClick={() => {
                const section = document.getElementById('how-it-works');
                section?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="text-ink-300 hover:text-white text-sm transition-colors cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Scroll to How It Works section"
            >
              How It Works
            </motion.button>
            <span className="text-ink-500" aria-hidden="true">•</span>
            <motion.button
              onClick={() => router.push('/login')}
              className="text-ink-300 hover:text-white text-sm transition-colors cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Navigate to sign in page"
            >
              Sign In
            </motion.button>
          </div>
        </motion.nav>
      </main>

      {/* How It Works Section */}
      <HowItWorksSection />

      {/* Stats Section */}
      <StatsSection />

      {/* Testimonials Section */}
      <TestimonialsCarousel />

      {/* Final CTA Section */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            className="glass-card hover-reflect rounded-3xl p-12 relative overflow-hidden shadow-glass-xl"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-accent-500/10 to-transparent opacity-50"></div>

            <div className="relative z-10">
              <motion.h2
                className="text-3xl md:text-4xl font-bold text-white mb-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, duration: 0.5 }}
              >
                Ready to Future-Proof Your Career?
              </motion.h2>
              <motion.p
                className="text-xl text-ink-200 mb-8 max-w-2xl mx-auto"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                Get your free AI-powered career analysis now. No credit card required.
              </motion.p>
              <motion.button
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                  setTimeout(() => {
                    const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                    input?.focus();
                  }, 500);
                }}
                className="primary-btn inline-flex items-center gap-2 group"
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4, duration: 0.5 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                <motion.div
                  animate={{
                    rotate: [0, 10, -10, 10, 0],
                    scale: [1, 1.1, 1, 1.1, 1]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 1
                  }}
                >
                  <Sparkles className="w-5 h-5" />
                </motion.div>
                <span>Start Your Free Analysis</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
