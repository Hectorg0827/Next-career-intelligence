'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, LogOut, User, Crown, Zap } from 'lucide-react';
import Logo from '@/components/Logo';
import HowItWorksSection from '@/components/HowItWorksSection';
import BenefitsSection from '@/components/BenefitsSection';
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
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-full"
              role="status"
              aria-label={`Logged in as ${user.email}${hasPremiumAccess ? ', Premium subscriber' : ''}`}
            >
              <User className="w-4 h-4 text-gold-primary inline mr-2" aria-hidden="true" />
              <span className="text-white text-sm font-semibold">{user.email}</span>
              {hasPremiumAccess && <Crown className="w-4 h-4 text-gold-primary inline ml-2" aria-label="Premium subscriber" />}
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-full hover:bg-slate-700 hover:border-gold-primary/50 transition-all group"
              aria-label="Log out of your account"
            >
              <LogOut className="w-4 h-4 text-white/70 group-hover:text-white inline mr-2" aria-hidden="true" />
              <span className="text-white/70 group-hover:text-white text-sm font-semibold">Logout</span>
            </button>
          </>
        ) : !isLoading ? (
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-bold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
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
              <div className="glass-card hover-reflect p-6 shadow-glass-lg border-gold-primary/30">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <motion.div
                      className="p-3 bg-gradient-to-br from-gold-primary/20 to-gold-accent/20 rounded-full"
                      whileHover={{ rotate: [0, -10, 10, -10, 0], transition: { duration: 0.5 } }}
                    >
                      <Crown className="w-6 h-6 text-gold-primary" />
                    </motion.div>
                    <div className="text-left">
                      <h3 className="text-white font-bold text-xl">Welcome back, {user?.name || 'Subscriber'}!</h3>
                      <p className="text-white/70 text-sm font-medium">Access your premium features</p>
                    </div>
                  </div>
                  <motion.button
                    onClick={handleSubscriberAccess}
                    className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-bold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
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
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 border border-gold-primary/30 rounded-full mb-8"
            variants={staggerItemVariants}
            role="status"
            aria-label="AI-powered analysis available"
          >
            <Sparkles className="w-4 h-4 text-gold-primary" aria-hidden="true" />
            <span className="text-white/90 text-sm font-semibold">Powered by AI</span>
          </motion.div>

          <motion.h1
            className="text-4xl md:text-6xl font-bold mb-6 leading-tight"
            variants={staggerItemVariants}
          >
            <span className="text-white">Know Your Next Move</span>
            <span className="block text-white mt-2">
              Before You Make It
            </span>
          </motion.h1>

          <motion.p
            className="text-lg md:text-xl text-white/70 mb-12 max-w-2xl mx-auto leading-relaxed font-normal"
            variants={staggerItemVariants}
          >
            Your AI-powered career companion
          </motion.p>

          <motion.form
            onSubmit={handleAnalyze}
            className="max-w-2xl mx-auto mb-4"
            variants={staggerItemVariants}
            role="search"
            aria-label="Career analysis search"
          >
            <div className="relative group">
              {/* Google-style search bar */}
              <div className="bg-white rounded-full flex items-center px-6 py-4 shadow-md hover:shadow-lg transition-all duration-300 border border-gray-200">
                {/* Search Icon */}
                <svg className="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>

                {/* Input */}
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Describe your career move or upload resume..."
                  className="flex-1 text-base text-gray-700 placeholder:text-gray-500 bg-transparent outline-none"
                  disabled={isAnalyzing}
                  aria-label="Job title or career query input"
                  aria-required="true"
                  id="job-title-input"
                  name="jobTitle"
                  autoComplete="off"
                />

                {/* Upload Button */}
                <button
                  type="button"
                  className="ml-3 w-10 h-10 rounded-full hover:bg-gray-100 flex items-center justify-center transition-all duration-200 group/upload"
                  aria-label="Upload resume"
                  onClick={(e) => {
                    e.preventDefault();
                    // TODO: Implement upload functionality
                  }}
                >
                  <svg className="w-5 h-5 text-gray-500 group-hover/upload:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </button>

                {/* Submit on Enter - hidden button */}
                <button type="submit" className="hidden" disabled={!jobTitle.trim() || isAnalyzing}>
                  Submit
                </button>
              </div>
            </div>
          </motion.form>

          {/* Example Searches */}
          <motion.div
            className="max-w-2xl mx-auto mb-12 text-center"
            variants={staggerItemVariants}
          >
            <span className="text-white/60 text-sm mr-3">Try:</span>
            {['Software engineer to product manager', 'Should I pursue an MBA?', 'Pivot from finance to tech'].map((example, idx) => (
              <button
                key={idx}
                onClick={() => setJobTitle(example)}
                className="inline-block bg-white/10 hover:bg-white/20 text-white/80 hover:text-white text-sm px-4 py-1.5 rounded-full mr-2 mb-2 transition-all duration-200"
              >
                {example}
              </button>
            ))}
          </motion.div>

          <motion.div
            className="flex flex-wrap items-center justify-center gap-8 text-white/70 text-sm mb-16 font-medium"
            variants={staggerItemVariants}
            role="list"
            aria-label="Key features"
          >
            <motion.div
              className="flex items-center gap-2 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              role="listitem"
            >
              <Shield className="w-5 h-5 text-gold-primary" aria-hidden="true" />
              <span>100% Free Analysis</span>
            </motion.div>
            <motion.div
              className="flex items-center gap-2 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              role="listitem"
            >
              <Brain className="w-5 h-5 text-gold-primary" aria-hidden="true" />
              <span>AI-Powered Insights</span>
            </motion.div>
            <motion.div
              className="flex items-center gap-2 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              role="listitem"
            >
              <TrendingUp className="w-5 h-5 text-gold-primary" aria-hidden="true" />
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
          <p className="text-white/60 text-base mb-4 font-medium">
            Join thousands of professionals taking control of their careers
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <motion.button
              onClick={() => {
                const section = document.getElementById('how-it-works');
                section?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="text-white/70 hover:text-gold-primary text-sm font-medium transition-colors cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Scroll to How It Works section"
            >
              How It Works
            </motion.button>
            <span className="text-white/30" aria-hidden="true">•</span>
            <motion.button
              onClick={() => router.push('/login')}
              className="text-white/70 hover:text-gold-primary text-sm font-medium transition-colors cursor-pointer"
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

      {/* Benefits Section */}
      <BenefitsSection />

      {/* Testimonials Section */}
      <TestimonialsCarousel />

      {/* Final CTA Section */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            className="p-12"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="relative z-10">
              <motion.h2
                className="text-3xl md:text-4xl font-bold text-white mb-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, duration: 0.5 }}
              >
                Ready to Make Your Next Move?
              </motion.h2>
              <motion.p
                className="text-lg md:text-xl text-white/70 mb-8 max-w-2xl mx-auto"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                Get your free career analysis in under 60 seconds
              </motion.p>
              <motion.button
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                  setTimeout(() => {
                    const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                    input?.focus();
                  }, 500);
                }}
                className="px-10 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold text-lg rounded-xl transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-2 group hover:-translate-y-0.5"
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4, duration: 0.5 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                style={{ boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)' }}
              >
                <span>Get Started Free</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
