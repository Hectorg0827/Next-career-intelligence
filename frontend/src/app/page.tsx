'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, User, Crown, Zap, Search, Upload } from 'lucide-react';
import Logo from '@/components/Logo';
import HowItWorksSection from '@/components/HowItWorksSection';
import BenefitsSection from '@/components/BenefitsSection';
import TestimonialsCarousel from '@/components/TestimonialsCarousel';
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
  const [uploadError, setUploadError] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;

    setIsAnalyzing(true);
    setUploadError('');

    // Simulate network delay for better UX
    await new Promise(resolve => setTimeout(resolve, 300));
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type)) {
      setUploadError('Please upload a PDF, DOC, DOCX, or TXT file');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('File size must be less than 5MB');
      return;
    }

    setUploadError('');
    setIsAnalyzing(true);

    // Store file in sessionStorage for Resume Studio to pick up
    try {
      const reader = new FileReader();
      reader.onload = (event) => {
        const fileData = {
          name: file.name,
          type: file.type,
          size: file.size,
          content: event.target?.result, // Base64 encoded content
          lastModified: file.lastModified,
        };
        sessionStorage.setItem('pendingResumeUpload', JSON.stringify(fileData));
        router.push('/resume-studio/upload');
      };
      reader.readAsDataURL(file); // Convert to base64
    } catch (error) {
      setUploadError('Failed to process file. Please try again.');
      setIsAnalyzing(false);
    }
  };

  const handleSubscriberAccess = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-900 relative overflow-hidden">
      {/* Skip to main content link for keyboard navigation */}
      <a
        href="#main-content"
        className="skip-to-main"
        aria-label="Skip to main content"
      >
        Skip to main content
      </a>

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 rounded-full blur-[120px] animate-pulse"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-600/10 rounded-full blur-[120px] animate-pulse"></div>
      </div>

      <main id="main-content" className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 pt-32 pb-20">
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
              className="mb-12 inline-flex"
              variants={fadeInUpVariants}
            >
              <div
                onClick={handleSubscriberAccess}
                className="cursor-pointer group flex items-center gap-4 px-6 py-3 bg-slate-800/50 hover:bg-slate-800 backdrop-blur-md border border-white/5 rounded-full hover:border-blue-500/30 transition-all duration-300"
              >
                <div className="p-1.5 bg-gradient-to-br from-amber-400 to-amber-600 rounded-full shadow-lg">
                  <Crown className="w-4 h-4 text-white" />
                </div>
                <div className="text-left">
                  <p className="text-white font-semibold text-sm group-hover:text-blue-200 transition-colors">
                    Welcome back, {user?.name || 'Subscriber'}
                  </p>
                </div>
                <ArrowRight className="w-4 h-4 text-white/50 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </div>
            </motion.div>
          )}

          {/* Tagline Badge */}
          {!hasPremiumAccess && (
            <motion.div
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 rounded-full mb-12 shadow-lg"
              variants={staggerItemVariants}
            >
              <Sparkles className="w-4 h-4 text-amber-400 fill-amber-400" />
              <span className="text-slate-200 text-sm font-medium">AI-Powered Career Intelligence</span>
            </motion.div>
          )}

          <motion.h1
            className="text-5xl sm:text-6xl md:text-7xl font-bold mb-8 leading-tight tracking-tight px-4"
            variants={staggerItemVariants}
          >
            <span className="text-white drop-shadow-xl">Know Your Next Move</span>
            <span className="block text-white/40 mt-2 font-semibold text-4xl sm:text-5xl md:text-6xl">
              Before You Make It
            </span>
          </motion.h1>

          <motion.p
            className="text-lg sm:text-xl text-white/60 mb-16 max-w-2xl mx-auto leading-relaxed font-normal px-4"
            variants={staggerItemVariants}
          >
            Join thousands of professionals using AI to predict career risks, discover hidden opportunities, and build future-proof roadmaps.
          </motion.p>

          <motion.form
            onSubmit={handleAnalyze}
            className="max-w-3xl mx-auto mb-6 px-4 relative z-20"
            variants={staggerItemVariants}
            role="search"
          >
            <div className={`relative group transition-all duration-300 ${isFocused ? 'scale-[1.02]' : ''}`}>
              {/* Google-style search bar */}
              <div
                className={`
                  bg-white rounded-full flex items-center px-6 py-5 shadow-2xl transition-all duration-300
                  ${isFocused ? 'shadow-blue-500/20 ring-4 ring-blue-500/10' : 'shadow-black/20'}
                `}
              >
                {/* Search Icon */}
                <Search className={`w-6 h-6 mr-4 transition-colors ${isFocused ? 'text-blue-600' : 'text-slate-400'}`} />

                {/* Input */}
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  placeholder={isAnalyzing ? 'Analyzing...' : 'Enter your job title or career goal...'}
                  className="flex-1 text-lg text-slate-800 placeholder:text-slate-400 bg-transparent outline-none disabled:opacity-50 min-w-0 font-medium"
                  disabled={isAnalyzing}
                  autoComplete="off"
                />

                {/* Loading Spinner */}
                {isAnalyzing && (
                  <div className="mr-4 animate-spin">
                    <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  </div>
                )}

                {/* Divider */}
                <div className="w-px h-8 bg-slate-200 mx-2 hidden sm:block"></div>

                {/* Upload Button */}
                <div className="hidden sm:flex items-center pl-2">
                  <input
                    type="file"
                    id="resume-upload"
                    className="hidden"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileUpload}
                    disabled={isAnalyzing}
                  />
                  <label
                    htmlFor="resume-upload"
                    className="cursor-pointer group/upload flex items-center gap-2 px-4 py-2 hover:bg-slate-100 rounded-xl transition-all"
                  >
                    <div className="p-1.5 bg-slate-100 group-hover/upload:bg-white rounded-lg group-hover/upload:shadow-sm border border-transparent group-hover/upload:border-slate-200 transition-all">
                      <Upload className="w-5 h-5 text-slate-500 group-hover/upload:text-blue-600" />
                    </div>
                    <span className="text-sm font-semibold text-slate-500 group-hover/upload:text-slate-800">Upload Resume</span>
                  </label>
                </div>
              </div>

              {/* Mobile Upload Button (below search on tiny screens) */}
              <div className="sm:hidden absolute top-1/2 right-4 -translate-y-1/2">
                <label htmlFor="resume-upload" className="p-2">
                  <Upload className="w-6 h-6 text-slate-400" />
                </label>
              </div>

              {/* Error Message */}
              {uploadError && (
                <div className="absolute top-full left-0 right-0 mt-4 mx-4 p-4 bg-red-500/10 border border-red-500/20 text-red-200 text-sm rounded-xl text-center backdrop-blur-md">
                  {uploadError}
                </div>
              )}
            </div>
          </motion.form>

          {/* Example Searches */}
          <motion.div
            className="max-w-2xl mx-auto mb-20 text-center px-4"
            variants={staggerItemVariants}
          >
            <div className="flex flex-wrap items-center justify-center gap-3">
              <span className="text-white/40 text-sm font-medium">Try:</span>
              {['Software Engineer', 'Product Manager', 'Marketing Director', 'Pivot to Tech'].map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setJobTitle(example)}
                  className="bg-white/5 hover:bg-white/10 text-white/60 hover:text-white text-sm px-4 py-2 rounded-lg transition-all duration-200 border border-white/5 hover:border-white/10"
                  disabled={isAnalyzing}
                >
                  {example}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Trust/Social Proof - Simple 3 items */}
          <motion.div
            className="flex flex-wrap items-center justify-center gap-12 text-white/50 text-sm font-medium"
            variants={staggerItemVariants}
          >
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-emerald-400" />
              <span>Private & Secure</span>
            </div>
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-400" />
              <span>DeepSeek R1 Engine</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-400" />
              <span>Real-time Data</span>
            </div>
          </motion.div>

        </motion.div>
      </main>

      {/* Spacious Sections */}
      <HowItWorksSection />
      <BenefitsSection />
      <TestimonialsCarousel />

      {/* Final CTA Section */}
      <section className="py-32 px-4 relative overflow-hidden">
        {/* Background Glow */}
        <div className="absolute inset-0 bg-blue-900/10 pointer-events-none"></div>
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-600/20 rounded-full blur-[100px] pointer-events-none"></div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Future-Proof Your Career?
            </h2>
            <p className="text-xl text-white/60 mb-10 max-w-2xl mx-auto">
              Get your personalized career analysis and roadmap in under 60 seconds.
            </p>

            <button
              onClick={() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                setTimeout(() => {
                  const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                  input?.focus();
                }, 800);
              }}
              className="px-12 py-5 bg-white text-slate-900 font-bold text-lg rounded-full transition-all shadow-xl hover:shadow-2xl hover:scale-105 hover:bg-blue-50 flex items-center gap-2 mx-auto"
            >
              <span>Get Started for Free</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
