'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle2, Sparkles } from 'lucide-react';

export default function CheckoutSuccessPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard after 5 seconds
    const timer = setTimeout(() => {
      router.push('/dashboard');
    }, 5000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Success Icon */}
        <div className="relative mb-8">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 bg-green-500/20 rounded-full animate-ping"></div>
          </div>
          <div className="relative flex items-center justify-center">
            <CheckCircle2 className="w-32 h-32 text-green-400" />
          </div>
        </div>

        {/* Success Message */}
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
          Welcome to Pro! 🎉
        </h1>
        <p className="text-xl text-white/80 mb-8">
          Your payment was successful. You now have access to all premium features!
        </p>

        {/* Features Unlocked */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Sparkles className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">Features Unlocked</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-4 text-left">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-white font-medium">Unlimited AI Analyses</div>
                <div className="text-white/60 text-sm">No limits on career assessments</div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-white font-medium">24/7 AI Coach</div>
                <div className="text-white/60 text-sm">Personalized career guidance</div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-white font-medium">AI Interview Practice</div>
                <div className="text-white/60 text-sm">Unlimited mock interviews</div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-white font-medium">Advanced Job Matching</div>
                <div className="text-white/60 text-sm">AI-powered opportunities</div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.push('/dashboard')}
            className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-pink-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl"
          >
            Go to Dashboard
          </button>
          
          <button
            onClick={() => router.push('/coach/chat')}
            className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
          >
            Try AI Coach
          </button>
        </div>

        {/* Auto redirect notice */}
        <p className="text-white/50 text-sm mt-8">
          Redirecting to dashboard in 5 seconds...
        </p>
      </div>
    </div>
  );
}
