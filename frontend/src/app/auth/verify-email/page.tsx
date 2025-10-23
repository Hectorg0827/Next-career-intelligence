'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Mail, CheckCircle, AlertCircle, Loader2, ArrowRight, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get('email');

  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(false);

  // Countdown timer for resend
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [countdown]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResendMessage('');

    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    if (!email) {
      setError('Email address is missing. Please sign up again.');
      return;
    }

    setLoading(true);

    try {
      const response = await api.auth.verifyEmail({
        email,
        verification_code: verificationCode
      });

      setSuccess(true);

      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      console.error('Verification error:', err);
      if (err.response?.status === 400) {
        setError('Invalid or expired verification code. Please try again or request a new code.');
      } else if (err.response?.status === 404) {
        setError('User not found. Please sign up again.');
      } else {
        setError(err.response?.data?.detail || 'Verification failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (!canResend) return;
    
    setError('');
    setResendMessage('');
    setResendLoading(true);

    try {
      await api.auth.resendVerification({ email: email! });
      
      setResendMessage('Verification code resent! Check your email.');
      setCountdown(60);
      setCanResend(false);
    } catch (err: any) {
      console.error('Resend error:', err);
      if (err.response?.status === 400) {
        setError('Email is already verified or request too frequent.');
      } else if (err.response?.status === 404) {
        setError('User not found. Please sign up again.');
      } else {
        setError(err.response?.data?.detail || 'Failed to resend code. Please try again.');
      }
    } finally {
      setResendLoading(false);
    }
  };

  const handleCodeInput = (value: string) => {
    // Only allow numbers and max 6 digits
    const cleaned = value.replace(/\D/g, '').slice(0, 6);
    setVerificationCode(cleaned);
    
    // Auto-submit when 6 digits entered
    if (cleaned.length === 6 && !loading) {
      // Small delay to show the full code before submitting
      setTimeout(() => {
        const form = document.getElementById('verify-form') as HTMLFormElement;
        if (form) form.requestSubmit();
      }, 300);
    }
  };

  if (!email) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Missing Email</h2>
          <p className="text-white/80 mb-6">
            We need your email address to verify your account.
          </p>
          <Link
            href="/auth/signup"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all"
          >
            Back to Sign Up
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 text-center">
          <div className="relative">
            <CheckCircle className="w-20 h-20 text-green-400 mx-auto mb-4 animate-bounce" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 bg-green-400/20 rounded-full animate-ping" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Email Verified! 🎉</h2>
          <p className="text-white/80 mb-6">
            Your account has been successfully verified. Redirecting you to your dashboard...
          </p>
          <div className="flex items-center justify-center gap-2 text-white/60">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Taking you to your dashboard</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Verify Your Email
          </h1>
          <p className="text-white/80 text-lg">
            We sent a 6-digit code to
          </p>
          <p className="text-white font-semibold text-lg mt-1">
            {email}
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 shadow-2xl">
          <form id="verify-form" onSubmit={handleVerify} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="flex items-start gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            {/* Success Message for Resend */}
            {resendMessage && (
              <div className="flex items-start gap-3 p-4 bg-green-500/20 border border-green-500/30 rounded-xl">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-green-200 text-sm">{resendMessage}</p>
              </div>
            )}

            {/* Verification Code Input */}
            <div>
              <label className="block text-white/90 font-medium mb-2">
                Verification Code
              </label>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                value={verificationCode}
                onChange={(e) => handleCodeInput(e.target.value)}
                placeholder="000000"
                className="w-full px-4 py-4 bg-white/90 border-0 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 text-center text-2xl font-bold tracking-widest"
                disabled={loading}
                autoFocus
              />
              <p className="text-white/60 text-sm mt-2 text-center">
                Enter the 6-digit code from your email
              </p>
            </div>

            {/* Verify Button */}
            <button
              type="submit"
              disabled={loading || verificationCode.length !== 6}
              className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Verifying...
                </>
              ) : (
                <>
                  Verify Email
                  <CheckCircle className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Resend Code */}
          <div className="mt-6 text-center">
            <p className="text-white/60 text-sm mb-3">
              Didn&apos;t receive the code?
            </p>
            <button
              onClick={handleResendCode}
              disabled={!canResend || resendLoading}
              className="inline-flex items-center gap-2 text-white/90 hover:text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resendLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Sending...
                </>
              ) : canResend ? (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Resend Code
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Resend in {countdown}s
                </>
              )}
            </button>
          </div>

          {/* Help */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <p className="text-white/60 text-sm text-center">
              Wrong email?{' '}
              <Link
                href="/auth/signup"
                className="text-white hover:text-white/80 font-medium transition-colors"
              >
                Sign up again
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-white/50 text-sm mt-6">
          Having trouble? <a href="mailto:support@nextcareer.ai" className="text-white hover:text-white/80 transition-colors">Contact support</a>
        </p>
      </div>
    </div>
  );
}
