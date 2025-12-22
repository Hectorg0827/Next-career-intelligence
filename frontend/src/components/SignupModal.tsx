'use client';

import { useState } from 'react';
import { X, Mail, Lock, User, Sparkles, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobTitle: string;
  analysisData?: unknown;
}

export default function SignupModal({ isOpen, onClose, jobTitle }: SignupModalProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState<'signup' | 'login'>('signup');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // For now, just redirect to login page with job title preserved
      // In production, this would create account and save analysis
      localStorage.setItem('pendingJobTitle', jobTitle);
      router.push(`/login?job=${encodeURIComponent(jobTitle)}&mode=${mode}`);
    } catch (err) {
      setError('Something went wrong. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-fade-in">
      <div 
        className="premium-card max-w-md w-full relative animate-scale-in overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="absolute inset-0 premium-bg-gradient opacity-30" />
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 w-8 h-8 bg-white/5 hover:bg-white/10 rounded-full flex items-center justify-center transition-all group z-20"
          aria-label="Close modal"
        >
          <X className="w-4 h-4 text-white/50 group-hover:text-white" />
        </button>

        {/* Header */}
        <div className="p-10 pb-6 text-center relative z-10">
          <div className="w-16 h-16 mx-auto mb-6 bg-premium-accent/10 border border-premium-accent/20 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-premium-accent" />
          </div>
          <h2 className="text-3xl font-serif italic text-white mb-3">
            {mode === 'signup' ? 'Unlock Intelligence' : 'Welcome Back'}
          </h2>
          <p className="text-premium-text-muted text-sm leading-relaxed">
            {mode === 'signup' 
              ? 'Create your account to access the full multi-agent career report.'
              : 'Sign in to continue your career transformation.'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-10 pt-0 space-y-5 relative z-10">
          {/* Name Field (Signup only) */}
          {mode === 'signup' && (
            <div>
              <label htmlFor="name" className="block text-premium-text-muted/60 uppercase tracking-widest text-[10px] font-medium mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-premium-accent/40" />
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full pl-12 pr-4 py-3.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-premium-accent/50 focus:border-transparent transition-all text-sm"
                  required
                />
              </div>
            </div>
          )}

          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-premium-text-muted/60 uppercase tracking-widest text-[10px] font-medium mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-premium-accent/40" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-12 pr-4 py-3.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-premium-accent/50 focus:border-transparent transition-all text-sm"
                required
              />
            </div>
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-premium-text-muted/60 uppercase tracking-widest text-[10px] font-medium mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-premium-accent/40" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-12 pr-12 py-3.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-premium-accent/50 focus:border-transparent transition-all text-sm"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/20 hover:text-white/50 transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="premium-btn-primary w-full py-4 flex items-center justify-center gap-2 group disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span className="text-sm">Processing...</span>
              </>
            ) : (
              <>
                <span className="text-sm">{mode === 'signup' ? 'Create Account' : 'Sign In'}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>

          {/* Mode Toggle */}
          <div className="text-center pt-6 border-t border-white/5">
            <p className="text-premium-text-muted/60 text-xs">
              {mode === 'signup' ? 'Already have an account?' : "Don't have an account?"}
              <button
                type="button"
                onClick={() => setMode(mode === 'signup' ? 'login' : 'signup')}
                className="ml-2 text-premium-accent hover:text-white font-medium transition-colors"
              >
                {mode === 'signup' ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </div>
        </form>

        {/* Footer */}
        <div className="px-10 pb-10 text-center relative z-10">
          <p className="text-premium-text-muted/30 text-[10px] uppercase tracking-widest leading-relaxed">
            By continuing, you agree to our <br /> Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}
