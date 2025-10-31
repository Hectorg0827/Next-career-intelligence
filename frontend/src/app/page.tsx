'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, LogOut, User, Crown, Zap } from 'lucide-react';
import Logo from '@/components/Logo';
import HowItWorksSection from '@/components/HowItWorksSection';
import TestimonialsCarousel from '@/components/TestimonialsCarousel';
import StatsSection from '@/components/StatsSection';
import {
  staggerContainerVariants,
  staggerItemVariants,
  buttonVariants,
  fadeInUpVariants,
  scaleInVariants,
} from '@/lib/animations';

export default function Home() {
  const router = useRouter();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubscriber, setIsSubscriber] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  // Check if user is logged in (subscriber)
  useEffect(() => {
    const email = localStorage.getItem('userEmail');
    const subscriptionTier = localStorage.getItem('subscriptionTier');
    if (email) {
      setUserEmail(email);
      setIsSubscriber(subscriptionTier === 'premium' || subscriptionTier === 'enterprise');
    }
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;

    setIsAnalyzing(true);
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('userEmail');
    localStorage.removeItem('subscriptionTier');
    localStorage.removeItem('authToken');
    setUserEmail(null);
    setIsSubscriber(false);
    router.refresh();
  };

  const handleSubscriberAccess = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-blue via-royal-blue-deep to-royal-navy relative overflow-hidden">
      {/* Top Right - Login/Logout */}
      <div className="absolute top-6 right-6 z-20 flex items-center gap-4">
        {userEmail ? (
          <>
            <div className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20">
              <User className="w-4 h-4 text-gold-primary" />
              <span className="text-white text-sm font-medium">{userEmail}</span>
              {isSubscriber && <Crown className="w-4 h-4 text-gold-primary" />}
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-full border border-white/20 transition-all group"
            >
              <LogOut className="w-4 h-4 text-white/70 group-hover:text-white" />
              <span className="text-white/70 group-hover:text-white text-sm font-medium">Logout</span>
            </button>
          </>
        ) : (
          <button
            onClick={() => router.push('/login')}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl"
          >
            <User className="w-5 h-5" />
            <span>Sign In</span>
          </button>
        )}
      </div>

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gold-primary rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-royal-blue rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-supporting-steel-blue rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12">
        <motion.div 
          className="max-w-4xl w-full text-center"
          variants={staggerContainerVariants}
          initial="initial"
          animate="animate"
        >
          {/* Subscriber Quick Access Section */}
          {isSubscriber && (
            <motion.div 
              className="mb-8"
              variants={fadeInUpVariants}
            >
              <div className="bg-gradient-to-r from-gold-primary/20 to-gold-accent/20 backdrop-blur-md border border-gold-primary/30 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <motion.div 
                      className="p-3 bg-gold-primary/20 rounded-full"
                      whileHover={{ rotate: [0, -10, 10, -10, 0], transition: { duration: 0.5 } }}
                    >
                      <Crown className="w-6 h-6 text-gold-primary" />
                    </motion.div>
                    <div className="text-left">
                      <h3 className="text-white font-semibold text-lg">Welcome back, Subscriber!</h3>
                      <p className="text-white/70 text-sm">Access your premium features</p>
                    </div>
                  </div>
                  <motion.button
                    onClick={handleSubscriberAccess}
                    className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all flex items-center gap-2 shadow-lg hover:shadow-xl"
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
            className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-gold-primary/30 rounded-full mb-8"
            variants={staggerItemVariants}
          >
            <Sparkles className="w-4 h-4 text-gold-primary" />
            <span className="text-white/90 text-sm font-medium">Powered by AI</span>
          </motion.div>

          <motion.h1 
            className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight"
            variants={staggerItemVariants}
          >
            Is Your Job
            <span className="block bg-gradient-to-r from-gold-primary via-gold-hover to-gold-accent bg-clip-text text-transparent">
              AI-Proof?
            </span>
          </motion.h1>

          <motion.p 
            className="text-xl md:text-2xl text-white/80 mb-12 max-w-2xl mx-auto"
            variants={staggerItemVariants}
          >
            Get a free AI-powered analysis of your career&apos;s automation risk and discover skills that future-proof your career
          </motion.p>

          <motion.form 
            onSubmit={handleAnalyze} 
            className="max-w-2xl mx-auto mb-8"
            variants={staggerItemVariants}
          >
            <div className="flex flex-col sm:flex-row gap-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-3 shadow-2xl">
              <motion.input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Enter your job title (e.g., Software Engineer)"
                className="flex-1 px-6 py-4 bg-white/90 border-0 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gold-primary text-lg"
                disabled={isAnalyzing}
                whileFocus={{ scale: 1.01 }}
                transition={{ duration: 0.2 }}
              />
              <motion.button
                type="submit"
                disabled={!jobTitle.trim() || isAnalyzing}
                className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap shadow-lg hover:shadow-xl"
                variants={buttonVariants}
                whileHover="hover"
                whileTap="tap"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Free'}
                {!isAnalyzing && <ArrowRight className="w-5 h-5" />}
              </motion.button>
            </div>
          </motion.form>

          <motion.div 
            className="flex flex-wrap items-center justify-center gap-8 text-white/60 text-sm mb-16"
            variants={staggerItemVariants}
          >
            <motion.div 
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05, color: 'rgba(255, 255, 255, 0.9)' }}
            >
              <Shield className="w-4 h-4" />
              <span>100% Free Analysis</span>
            </motion.div>
            <motion.div 
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05, color: 'rgba(255, 255, 255, 0.9)' }}
            >
              <Brain className="w-4 h-4" />
              <span>AI-Powered Insights</span>
            </motion.div>
            <motion.div 
              className="flex items-center gap-2"
              whileHover={{ scale: 1.05, color: 'rgba(255, 255, 255, 0.9)' }}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Personalized Roadmap</span>
            </motion.div>
          </motion.div>

        </motion.div>

        <motion.div 
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <p className="text-white/50 text-sm mb-4">
            Join thousands of professionals taking control of their careers
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <motion.button 
              onClick={() => {
                const section = document.getElementById('how-it-works');
                section?.scrollIntoView({ behavior: 'smooth' });
              }} 
              className="text-white/60 hover:text-white text-sm transition-colors cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              How It Works
            </motion.button>
            <span className="text-white/30">•</span>
            <motion.button 
              onClick={() => router.push('/login')} 
              className="text-white/60 hover:text-white text-sm transition-colors cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Sign In
            </motion.button>
          </div>
        </motion.div>
      </div>

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
            className="bg-gradient-to-br from-gold-primary/20 to-gold-accent/20 backdrop-blur-md border border-gold-primary/30 rounded-3xl p-12 relative overflow-hidden"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{ 
              boxShadow: "0 0 50px rgba(229, 183, 59, 0.3)",
              transition: { duration: 0.3 }
            }}
          >
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-gold-primary/10 to-transparent opacity-50"></div>
            
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
                className="text-xl text-white/80 mb-8 max-w-2xl mx-auto"
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
                className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-2 group"
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
