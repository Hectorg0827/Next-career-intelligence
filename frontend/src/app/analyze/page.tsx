'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Loader2, TrendingUp, AlertCircle, CheckCircle2, ArrowRight, DollarSign, Sparkles } from 'lucide-react';
import { intelligenceApi } from '@/lib/api';
import { useAuth } from '@/lib/firebase';
import InstantSnapshot from '@/components/InstantSnapshot';
import MicroWin from '@/components/MicroWins';
import { RiskCard, CompatibilityCard, SkillGapsCard, NextStepsCard, CoachQuestionsCard } from '@/components/analysis/AnalysisCards';

export default function AnalyzePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useAuth();
  const jobTitle = searchParams.get('job') || '';
  
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [showInstantSnapshot, setShowInstantSnapshot] = useState(true);
  const [showMicroWin, setShowMicroWin] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('🚀 Activating Multi-Agent Intelligence System...');

  useEffect(() => {
    if (!jobTitle) {
      router.push('/');
      return;
    }

    if (!user) {
      router.push('/login');
      return;
    }

    // Real API call to backend with FULL MULTI-AGENT ORCHESTRATOR
    const performAnalysis = async () => {
      try {
        setIsAnalyzing(true);
        setError(null);
        
        // Show progress messages for multi-agent system
        setTimeout(() => setLoadingMessage('🤖 Deploying 9 specialized AI agents...'), 2000);
        setTimeout(() => setLoadingMessage('🧠 Profile Agent analyzing your background...'), 5000);
        setTimeout(() => setLoadingMessage('⚠️ Risk Agent evaluating AI displacement...'), 8000);
        setTimeout(() => setLoadingMessage('🎯 Match Agent calculating compatibility...'), 11000);
        setTimeout(() => setLoadingMessage('📊 Gap Agent identifying skill requirements...'), 14000);
        setTimeout(() => setLoadingMessage('💬 Sentiment Agent analyzing industry trends...'), 17000);
        setTimeout(() => setLoadingMessage('🔮 Trajectory Agent forecasting career paths...'), 20000);
        setTimeout(() => setLoadingMessage('📈 Market Intel Agent gathering insights...'), 23000);
        setTimeout(() => setLoadingMessage('🚨 Early Warning Agent checking risks...'), 26000);
        setTimeout(() => setLoadingMessage('✨ Orchestrator synthesizing insights...'), 29000);
        
        // Call the MULTI-AGENT ORCHESTRATOR API
        const result = await intelligenceApi.analyzeCareer({
          job_title: jobTitle,
          skills: [],
          location: 'United States'
        });
        
        console.log('🎯 Orchestrator analysis result:', result);
        
        setAnalysis(result);
        
        // Show micro-win notification
        setShowMicroWin(true);
      } catch (err: any) {
        console.error('❌ Multi-agent analysis error:', err);
        setError(err.response?.data?.detail || 'Multi-agent analysis failed. Please try again.');
      } finally {
        setIsAnalyzing(false);
      }
    };

    performAnalysis();
  }, [jobTitle, user, router]);

  if (!jobTitle) {
    return null;
  }

  if (isAnalyzing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Analyzing Your Career
            </h1>
            <p className="text-xl text-white/80">
              for <span className="font-semibold text-gold-primary">{jobTitle}</span>
            </p>
          </div>

          {/* Instant Snapshot Component - Shows immediately */}
          {showInstantSnapshot && <InstantSnapshot jobTitle={jobTitle} />}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl text-white font-semibold mb-2">Analysis Failed</h2>
          <p className="text-white/70 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-white text-royal-navy rounded-lg font-semibold hover:bg-white/90 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const getRiskColor = (score: number) => {
    if (score < 40) return 'text-green-400';
    if (score < 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 py-12 px-4">
      {/* Micro-Win Notification */}
      <MicroWin 
        show={showMicroWin} 
        message="Analysis Complete! Your career insights are ready." 
        xp={50} 
      />
      
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-10 h-10 text-gold-primary mr-3 animate-pulse" />
            <h1 className="text-4xl md:text-5xl font-bold text-white">
              Multi-Agent Analysis Report
            </h1>
          </div>
          <p className="text-xl text-white/80">
            for <span className="font-semibold text-gold-primary">{jobTitle}</span>
          </p>
          <p className="text-sm text-white/60 mt-2">Powered by 9 AI agents working in harmony</p>
        </div>

        {/* Multi-Agent Analysis Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <RiskCard risk={analysis?.risk} />
          <CompatibilityCard 
            score={analysis?.compatibility?.score || 0} 
            highlights={analysis?.compatibility?.highlights || []} 
          />
          <div className="md:col-span-2">
            <SkillGapsCard gaps={analysis?.gaps || []} />
          </div>
          <div className="md:col-span-2">
            <NextStepsCard steps={analysis?.next_steps || []} />
          </div>
          {analysis?.coach_questions && analysis.coach_questions.length > 0 && (
            <div className="md:col-span-2">
              <CoachQuestionsCard questions={analysis.coach_questions} />
            </div>
          )}
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.push('/coach/chat')}
            className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-pink-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
          >
            Get Personalized Coaching
            <ArrowRight className="w-5 h-5" />
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
          >
            Analyze Another Job
          </button>
        </div>
      </div>
    </div>
  );
}
