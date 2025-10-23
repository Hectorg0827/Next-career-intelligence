'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;

    setIsAnalyzing(true);
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-500 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-indigo-500 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12">
        <div className="max-w-4xl w-full text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-yellow-400" />
            <span className="text-white/90 text-sm font-medium">Powered by AI</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Is Your Job
            <span className="block bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              AI-Proof?
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-white/80 mb-12 max-w-2xl mx-auto">
            Get a free AI-powered analysis of your career's automation risk and discover skills that future-proof your career
          </p>

          <form onSubmit={handleAnalyze} className="max-w-2xl mx-auto mb-8">
            <div className="flex flex-col sm:flex-row gap-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-3 shadow-2xl">
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Enter your job title (e.g., Software Engineer)"
                className="flex-1 px-6 py-4 bg-white/90 border-0 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                disabled={isAnalyzing}
              />
              <button
                type="submit"
                disabled={!jobTitle.trim() || isAnalyzing}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap shadow-lg hover:shadow-xl"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Free'}
                {!isAnalyzing && <ArrowRight className="w-5 h-5" />}
              </button>
            </div>
          </form>

          <div className="flex flex-wrap items-center justify-center gap-8 text-white/60 text-sm mb-16">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              <span>100% Free Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              <span>AI-Powered Insights</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              <span>Personalized Roadmap</span>
            </div>
          </div>

          <div className="max-w-3xl mx-auto bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <div className="grid md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-4xl font-bold text-white mb-2">10k+</div>
                <div className="text-white/60">Careers Analyzed</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white mb-2">87%</div>
                <div className="text-white/60">Found Skills to Learn</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white mb-2">4.9/5</div>
                <div className="text-white/60">User Rating</div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <p className="text-white/50 text-sm mb-4">
            Join thousands of professionals taking control of their careers
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <a href="#" className="text-white/60 hover:text-white text-sm transition-colors">How It Works</a>
            <span className="text-white/30">•</span>
            <a href="#" className="text-white/60 hover:text-white text-sm transition-colors">Success Stories</a>
            <span className="text-white/30">•</span>
            <a href="/dashboard" className="text-white/60 hover:text-white text-sm transition-colors">Sign In</a>
          </div>
        </div>
      </div>
    </div>
  );
}
