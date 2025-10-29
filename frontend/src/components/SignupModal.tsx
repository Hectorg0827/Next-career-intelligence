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
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div 
        className="bg-gradient-to-br from-royal-navy via-royal-navy to-royal-blue-deep rounded-3xl max-w-md w-full shadow-2xl border border-white/10 relative animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all group z-10"
          aria-label="Close modal"
        >
          <X className="w-5 h-5 text-white/70 group-hover:text-white" />
        </button>

        {/* Header */}
        <div className="p-8 pb-6 text-center border-b border-white/10">
          <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-gold-primary to-gold-accent rounded-full flex items-center justify-center shadow-gold">
            <Sparkles className="w-8 h-8 text-royal-navy" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            {mode === 'signup' ? 'Unlock Your Full Analysis' : 'Welcome Back'}
          </h2>
          <p className="text-white/70">
            {mode === 'signup' 
              ? 'Create a free account to see your complete career intelligence report'
              : 'Sign in to access your full analysis'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-8 space-y-4">
          {/* Name Field (Signup only) */}
          {mode === 'signup' && (
            <div>
              <label htmlFor="name" className="block text-white/90 font-medium mb-2 text-sm">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-primary focus:border-transparent transition-all"
                  required
                />
              </div>
            </div>
          )}

          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-white/90 font-medium mb-2 text-sm">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-primary focus:border-transparent transition-all"
                required
              />
            </div>
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-white/90 font-medium mb-2 text-sm">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-12 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-primary focus:border-transparent transition-all"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/70 transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-6 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-royal-navy/30 border-t-royal-navy rounded-full animate-spin"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>{mode === 'signup' ? 'Create Free Account' : 'Sign In'}</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>

          {/* Mode Toggle */}
          <div className="text-center pt-4 border-t border-white/10">
            <p className="text-white/70 text-sm">
              {mode === 'signup' ? 'Already have an account?' : "Don't have an account?"}
              <button
                type="button"
                onClick={() => setMode(mode === 'signup' ? 'login' : 'signup')}
                className="ml-2 text-gold-primary hover:text-gold-accent font-semibold transition-colors"
              >
                {mode === 'signup' ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </div>
        </form>

        {/* Footer */}
        <div className="px-8 pb-8 text-center">
          <p className="text-white/50 text-xs">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}
