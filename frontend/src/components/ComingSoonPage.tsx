'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, CheckCircle, Clock, Mail } from 'lucide-react';
import { useRouter } from 'next/navigation';
import {
  staggerContainerVariants,
  staggerItemVariants,
  buttonVariants,
  cardVariants,
  scaleInVariants,
  successCheckVariants,
} from '@/lib/animations';

interface ComingSoonPageProps {
  feature: {
    title: string;
    subtitle: string;
    icon: string;
    description: string;
    benefits: string[];
    launchTimeline: string;
    previewImage?: string;
  };
}

export default function ComingSoonPage({ feature }: ComingSoonPageProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleWaitlistSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setIsSubmitted(true);
      setIsLoading(false);
      // In production, this would save to waitlist database
      localStorage.setItem(`waitlist_${feature.title}`, email);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900">
      {/* Background Animation */}
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gold-primary rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-royal-blue rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-12">
        <motion.div 
          className="max-w-4xl w-full"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Back Button */}
          <motion.button
            onClick={() => router.push('/')}
            className="mb-8 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-white/70 hover:text-white transition-all flex items-center gap-2"
            whileHover={{ scale: 1.02, x: -4 }}
            whileTap={{ scale: 0.98 }}
          >
            ← Back to Home
          </motion.button>

          {/* Main Card */}
          <motion.div 
            className="bg-slate-800 border border-slate-700 rounded-3xl p-8 md:p-12 shadow-2xl"
            variants={cardVariants}
            initial="initial"
            whileHover="hover"
          >
            {/* Header */}
            <motion.div 
              className="text-center mb-12"
              variants={staggerContainerVariants}
              initial="initial"
              animate="animate"
            >
              {/* Icon */}
              <motion.div 
                className="text-8xl mb-6"
                variants={scaleInVariants}
                animate={{
                  y: [0, -10, 0],
                  transition: {
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }
                }}
              >
                {feature.icon}
              </motion.div>

              {/* Coming Soon Badge */}
              <motion.div 
                className="inline-flex items-center gap-2 px-4 py-2 bg-gold-primary/20 border border-gold-primary/40 rounded-full mb-6"
                variants={staggerItemVariants}
              >
                <Clock className="w-4 h-4 text-gold-primary" />
                <span className="text-gold-primary text-sm font-semibold">Coming Soon</span>
              </motion.div>

              {/* Title */}
              <motion.h1 
                className="text-4xl md:text-5xl font-bold text-white mb-4"
                variants={staggerItemVariants}
              >
                {feature.title}
              </motion.h1>

              {/* Subtitle */}
              <motion.p 
                className="text-xl md:text-2xl text-white/80 mb-6"
                variants={staggerItemVariants}
              >
                {feature.subtitle}
              </motion.p>

              {/* Description */}
              <motion.p 
                className="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed"
                variants={staggerItemVariants}
              >
                {feature.description}
              </motion.p>
            </motion.div>

            {/* Benefits Section */}
            <motion.div 
              className="mb-12"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="text-2xl font-bold text-white mb-6 text-center">
                What to Expect
              </h2>
              <motion.div 
                className="grid md:grid-cols-2 gap-4"
                variants={staggerContainerVariants}
                initial="initial"
                whileInView="animate"
                viewport={{ once: true }}
              >
                {feature.benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10 hover:border-gold-primary/50 transition-all group"
                    variants={staggerItemVariants}
                    whileHover={{ 
                      scale: 1.02,
                      backgroundColor: "rgba(255, 255, 255, 0.08)",
                      transition: { duration: 0.2 }
                    }}
                  >
                    <motion.div
                      whileHover={{ 
                        scale: 1.2,
                        rotate: 360,
                        transition: { duration: 0.5 }
                      }}
                    >
                      <CheckCircle className="w-6 h-6 text-gold-primary flex-shrink-0 mt-0.5" />
                    </motion.div>
                    <span className="text-white/90">{benefit}</span>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>

            {/* Timeline */}
            <motion.div 
              className="mb-12 text-center"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <motion.div 
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-gold-primary/20 to-gold-accent/20 border border-gold-primary/30 rounded-xl"
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 0 30px rgba(229, 183, 59, 0.3)",
                  transition: { duration: 0.3 }
                }}
              >
                <motion.div
                  animate={{ 
                    rotate: [0, 10, -10, 10, 0],
                    transition: { duration: 2, repeat: Infinity, repeatDelay: 1 }
                  }}
                >
                  <Sparkles className="w-5 h-5 text-gold-primary" />
                </motion.div>
                <span className="text-white font-semibold">Expected Launch: {feature.launchTimeline}</span>
              </motion.div>
            </motion.div>

            {/* Waitlist Form */}
            {!isSubmitted ? (
              <motion.div 
                className="max-w-md mx-auto"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <h3 className="text-xl font-bold text-white mb-4 text-center">
                  Join the Waitlist
                </h3>
                <p className="text-white/70 mb-6 text-center">
                  Be the first to know when we launch. Get exclusive early access!
                </p>
                <form onSubmit={handleWaitlistSignup} className="space-y-4">
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
                    <motion.input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your.email@example.com"
                      className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-primary focus:border-transparent transition-all"
                      required
                      whileFocus={{ scale: 1.01 }}
                    />
                  </div>
                  <motion.button
                    type="submit"
                    disabled={isLoading}
                    className="w-full px-6 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
                    variants={buttonVariants}
                    whileHover="hover"
                    whileTap="tap"
                  >
                    {isLoading ? (
                      <>
                        <motion.div 
                          className="w-5 h-5 border-2 border-royal-navy/30 border-t-royal-navy rounded-full"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        <span>Joining...</span>
                      </>
                    ) : (
                      <>
                        <span>Join Waitlist</span>
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </motion.button>
                </form>
                <p className="text-white/50 text-xs text-center mt-4">
                  We&apos;ll only email you about this feature launch. No spam, ever.
                </p>
              </motion.div>
            ) : (
              <motion.div 
                className="max-w-md mx-auto text-center"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              >
                <motion.div 
                  className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-gold-primary to-gold-accent rounded-full flex items-center justify-center shadow-gold"
                  variants={successCheckVariants}
                  initial="initial"
                  animate="animate"
                >
                  <CheckCircle className="w-10 h-10 text-royal-navy" />
                </motion.div>
                <motion.h3 
                  className="text-2xl font-bold text-white mb-3"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  You&apos;re on the list! 🎉
                </motion.h3>
                <motion.p 
                  className="text-white/80 mb-6"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  We&apos;ll email you at <span className="text-gold-primary font-semibold">{email}</span> when {feature.title} launches.
                </motion.p>
                <motion.button
                  onClick={() => router.push('/')}
                  className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Back to Home
                </motion.button>
              </motion.div>
            )}
          </motion.div>

          {/* Bottom CTA */}
          {!isSubmitted && (
            <motion.div 
              className="text-center mt-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <p className="text-white/60 mb-4">
                Want to explore what&apos;s available now?
              </p>
              <motion.button
                onClick={() => router.push('/analyze?job=Software Engineer')}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-xl text-white/90 hover:text-white transition-all inline-flex items-center gap-2"
                whileHover={{ scale: 1.02, backgroundColor: "#475569" }}
                whileTap={{ scale: 0.98 }}
              >
                <Sparkles className="w-5 h-5" />
                <span>Try Free Career Analysis</span>
              </motion.button>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
