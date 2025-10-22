'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Mail, Lock, User, ArrowRight, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';

type AuthStep = 'welcome' | 'signup' | 'login' | 'verify-email' | 'reset-password';

interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  acceptTerms: boolean;
}

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export const AuthFlow = () => {
  const [step, setStep] = useState<AuthStep>('welcome');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [signupData, setSignupData] = useState<SignupFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    acceptTerms: false,
  });

  const [loginData, setLoginData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false,
  });

  const handleSignupChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    setSignupData({
      ...signupData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    });
  };

  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setLoginData({
      ...loginData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    });
  };

  const validateSignup = () => {
    setError('');
    
    if (!signupData.fullName.trim()) {
      setError('Full name is required');
      return false;
    }
    
    if (!signupData.email.includes('@')) {
      setError('Please enter a valid email');
      return false;
    }
    
    if (signupData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }
    
    if (signupData.password !== signupData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    if (!signupData.acceptTerms) {
      setError('You must accept the terms and privacy policy');
      return false;
    }
    
    return true;
  };

  const validateLogin = () => {
    setError('');
    
    if (!loginData.email.includes('@')) {
      setError('Please enter a valid email');
      return false;
    }
    
    if (!loginData.password) {
      setError('Password is required');
      return false;
    }
    
    return true;
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateSignup()) return;
    
    setIsLoading(true);
    try {
      const response = await apiClient.signup({
        full_name: signupData.fullName,
        email: signupData.email,
        password: signupData.password,
        confirm_password: signupData.confirmPassword,
      });
      
      if (response.success) {
        setUserEmail(signupData.email);
        setSuccess(response.message);
        setStep('verify-email');
      } else {
        setError(response.message || 'Signup failed. Please try again.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateLogin()) return;
    
    setIsLoading(true);
    try {
      const response = await apiClient.login({
        email: loginData.email,
        password: loginData.password,
        remember_me: loginData.rememberMe,
      });
      
      if (response.success) {
        setSuccess(response.message);
        // Redirect to dashboard after brief delay
        setTimeout(() => {
          router.push('/dashboard');
        }, 1000);
      } else {
        setError(response.message || 'Login failed. Please try again.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!verificationCode || verificationCode.length < 6) {
      setError('Please enter a valid verification code');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await apiClient.verifyEmail({
        email: userEmail || signupData.email,
        verification_code: verificationCode,
      });
      
      if (response.success) {
        setSuccess('Email verified! Redirecting to onboarding...');
        setTimeout(() => {
          router.push('/onboarding');
        }, 1500);
      } else {
        setError(response.message || 'Verification failed. Please try again.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-next-hero flex items-center justify-center p-4">
      {/* Welcome Step */}
      {step === 'welcome' && (
        <div className="max-w-md w-full space-y-8 animate-fade-in">
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold text-white mb-4">
              Welcome to NEXT
            </h1>
            <p className="text-white/70 mb-8">
              Join thousands of professionals taking control of their careers in the age of AI
            </p>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => {
                setStep('signup');
                setError('');
                setSuccess('');
              }}
              className="w-full bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
            >
              Create Account
              <ArrowRight className="w-5 h-5" />
            </button>

            <button
              onClick={() => {
                setStep('login');
                setError('');
                setSuccess('');
              }}
              className="w-full bg-white/10 hover:bg-white/20 text-white font-semibold py-3 rounded-lg transition-all border border-white/30"
            >
              Sign In
            </button>
          </div>

          {/* OAuth Options */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/20" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-next-deep-blue text-white/60">Or continue with</span>
            </div>
          </div>

          <div className="space-y-2">
            <button className="w-full bg-white hover:bg-white/90 text-next-deep-blue font-semibold py-2 rounded-lg transition-all flex items-center justify-center gap-2">
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Google
            </button>

            <button className="w-full bg-[#0077b5] hover:bg-[#0077b5]/90 text-white font-semibold py-2 rounded-lg transition-all flex items-center justify-center gap-2">
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.475-2.236-1.986-2.236-1.081 0-1.722.722-2.004 1.418-.103.25-.129.599-.129.948v5.439h-3.554s.05-8.736 0-9.646h3.554v1.364c.429-.661 1.196-1.605 2.907-1.605 2.126 0 3.716 1.39 3.716 4.382v5.505zM5.337 8.855c-1.144 0-1.915-.758-1.915-1.708 0-.951.77-1.708 1.971-1.708 1.2 0 1.914.757 1.938 1.708 0 .95-.738 1.708-1.994 1.708zm1.581 11.597H3.715V9.861h3.203v10.591zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z" />
              </svg>
              LinkedIn
            </button>
          </div>

          <p className="text-center text-white/60 text-sm">
            By signing up, you agree to our{' '}
            <a href="#" className="text-next-gold hover:underline">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-next-gold hover:underline">
              Privacy Policy
            </a>
          </p>
        </div>
      )}

      {/* Signup Step */}
      {step === 'signup' && (
        <div className="max-w-md w-full space-y-6 animate-fade-in">
          <div className="text-center">
            <h1 className="text-3xl font-heading font-bold text-white mb-2">
              Create Your Account
            </h1>
            <p className="text-white/70">
              Join thousands discovering their AI-proof career path
            </p>
          </div>

          <form onSubmit={handleSignup} className="space-y-4">
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 flex items-start gap-2 text-red-200">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {success && (
              <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-3 flex items-start gap-2 text-green-200">
                <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{success}</span>
              </div>
            )}

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-3 w-5 h-5 text-white/40" />
                <input
                  type="text"
                  name="fullName"
                  value={signupData.fullName}
                  onChange={handleSignupChange}
                  placeholder="John Doe"
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-5 h-5 text-white/40" />
                <input
                  type="email"
                  name="email"
                  value={signupData.email}
                  onChange={handleSignupChange}
                  placeholder="your@email.com"
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-white/40" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={signupData.password}
                  onChange={handleSignupChange}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-10 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-white/40 hover:text-white/60"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              <p className="text-white/50 text-xs mt-1">
                At least 8 characters
              </p>
            </div>

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-white/40" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={signupData.confirmPassword}
                  onChange={handleSignupChange}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-10 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>
            </div>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="acceptTerms"
                checked={signupData.acceptTerms}
                onChange={handleSignupChange}
                className="mt-1 w-4 h-4 rounded border-white/20 bg-white/10 text-next-gold focus:ring-next-gold"
              />
              <span className="text-white/80 text-sm">
                I agree to the Terms of Service and Privacy Policy
              </span>
            </label>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
              {!isLoading && <ArrowRight className="w-5 h-5" />}
            </button>

            <p className="text-center text-white/60">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setStep('login');
                  setError('');
                }}
                className="text-next-gold hover:underline"
              >
                Sign In
              </button>
            </p>
          </form>
        </div>
      )}

      {/* Login Step */}
      {step === 'login' && (
        <div className="max-w-md w-full space-y-6 animate-fade-in">
          <div className="text-center">
            <h1 className="text-3xl font-heading font-bold text-white mb-2">
              Welcome Back
            </h1>
            <p className="text-white/70">
              Sign in to access your career intelligence
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 flex items-start gap-2 text-red-200">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {success && (
              <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-3 flex items-start gap-2 text-green-200">
                <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{success}</span>
              </div>
            )}

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-5 h-5 text-white/40" />
                <input
                  type="email"
                  name="email"
                  value={loginData.email}
                  onChange={handleLoginChange}
                  placeholder="your@email.com"
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-white/40" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={loginData.password}
                  onChange={handleLoginChange}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-10 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-white/40 hover:text-white/60"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={loginData.rememberMe}
                  onChange={handleLoginChange}
                  className="w-4 h-4 rounded border-white/20 bg-white/10 text-next-gold focus:ring-next-gold"
                />
                <span className="text-white/80 text-sm">Remember me</span>
              </label>

              <button
                type="button"
                onClick={() => {
                  setStep('reset-password');
                  setError('');
                }}
                className="text-next-gold hover:underline text-sm"
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
              {!isLoading && <ArrowRight className="w-5 h-5" />}
            </button>

            <p className="text-center text-white/60">
              Don&apos;t have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setStep('signup');
                  setError('');
                }}
                className="text-next-gold hover:underline"
              >
                Create one
              </button>
            </p>
          </form>
        </div>
      )}

      {/* Verify Email Step */}
      {step === 'verify-email' && (
        <div className="max-w-md w-full space-y-6 animate-fade-in">
          <div className="text-center">
            <div className="w-16 h-16 bg-next-gold/20 rounded-full flex items-center justify-center mx-auto border border-next-gold/50 mb-4">
              <CheckCircle className="w-8 h-8 text-next-gold" />
            </div>

            <h1 className="text-3xl font-heading font-bold text-white mb-2">
              Verify Your Email
            </h1>
            <p className="text-white/70">
              We&apos;ve sent a verification code to<br />
              <span className="text-next-gold">{userEmail || signupData.email}</span>
            </p>
          </div>

          <form onSubmit={handleVerifyEmail} className="space-y-4">
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 flex items-start gap-2 text-red-200">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <div>
              <label className="block text-white font-semibold mb-2 text-sm">
                Verification Code
              </label>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => {
                  setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6));
                  setError('');
                }}
                placeholder="000000"
                maxLength={6}
                className="w-full text-center text-2xl tracking-widest bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
              />
              <p className="text-white/50 text-xs mt-1">
                Enter the 6-digit code from your email
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading || verificationCode.length < 6}
              className="w-full bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
            >
              {isLoading ? 'Verifying...' : 'Verify Email'}
              {!isLoading && <ArrowRight className="w-5 h-5" />}
            </button>
          </form>

          <p className="text-center text-white/60 text-sm bg-white/5 rounded-lg p-4">
            Didn&apos;t receive the code?{' '}
            <button className="text-next-gold hover:underline">
              Resend it
            </button>
          </p>

          <button
            onClick={() => setStep('welcome')}
            className="w-full text-white/60 hover:text-white/80 text-sm py-2"
          >
            Back to Welcome
          </button>
        </div>
      )}
    </div>
  );
};

export default AuthFlow;
