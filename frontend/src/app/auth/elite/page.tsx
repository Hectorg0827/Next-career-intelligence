'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Crown, Lock, User, ArrowRight, AlertCircle, Loader2, Shield } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function EliteLoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/elite/login`, {
        username,
        password
      });

      const data = response.data;

      if (data.success) {
        // Store elite user info in localStorage
        localStorage.setItem('eliteUser', JSON.stringify({
          userId: data.user_id,
          firebaseUid: data.firebase_uid,
          email: data.email,
          role: data.role,
          subscriptionStatus: data.subscription_status,
          isElite: true,
          loginTime: new Date().toISOString()
        }));

        // Store auth token
        localStorage.setItem('authToken', `elite_${data.firebase_uid}`);

        // Redirect to dashboard
        router.push('/dashboard');
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } catch (err: any) {
      console.error('Elite login error:', err);
      if (err.response?.status === 401) {
        setError('Invalid elite credentials. Please try again.');
      } else {
        setError(err.response?.data?.detail || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Elite Badge */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-amber-500 to-yellow-600 rounded-full mb-4 shadow-2xl animate-pulse">
            <Crown className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-yellow-600 mb-2">
            Elite Access
          </h1>
          <p className="text-white/70 text-lg flex items-center justify-center gap-2">
            <Shield className="w-5 h-5" />
            Admin & Testing Portal
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="flex items-start gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            {/* Username Field */}
            <div>
              <label className="block text-white/90 font-medium mb-2">
                Elite Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="elite_admin"
                  className="w-full pl-11 pr-4 py-3 bg-white/90 border-0 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  disabled={loading}
                  autoComplete="username"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-white/90 font-medium mb-2">
                Elite Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter elite password"
                  className="w-full pl-11 pr-4 py-3 bg-white/90 border-0 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  disabled={loading}
                  autoComplete="current-password"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-amber-500 to-yellow-600 hover:from-amber-600 hover:to-yellow-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  <Crown className="w-5 h-5" />
                  Elite Login
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Credentials Info */}
          <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-amber-200/90">
                <p className="font-semibold mb-1">Elite Credentials:</p>
                <p className="font-mono text-xs">Username: elite_admin</p>
                <p className="font-mono text-xs">Password: NextElite2025!</p>
              </div>
            </div>
          </div>

          {/* Regular Login Link */}
          <div className="mt-6 text-center">
            <button
              onClick={() => router.push('/auth/login')}
              className="text-white/70 hover:text-white transition-colors text-sm"
            >
              Back to Regular Login →
            </button>
          </div>
        </div>

        {/* Elite Features */}
        <div className="mt-8 text-center">
          <p className="text-white/50 text-sm mb-3">Elite Access Includes:</p>
          <div className="flex flex-wrap justify-center gap-2">
            <span className="px-3 py-1 bg-white/10 rounded-full text-white/70 text-xs">Unlimited Analyses</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-white/70 text-xs">All AI Features</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-white/70 text-xs">Admin Panel</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-white/70 text-xs">Priority Support</span>
          </div>
        </div>
      </div>
    </div>
  );
}
