'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { AlertCircle, ArrowRight, Sparkles } from 'lucide-react';
import { intelligenceApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import EnhancedLoadingExperience from '@/components/EnhancedLoadingExperience';
import MicroWin from '@/components/MicroWins';
import SocialShare from '@/components/SocialShare';
import PremiumContentOverlay from '@/components/PremiumContentOverlay';
import SignupModal from '@/components/SignupModal';
import {
  RiskCard,
  CompatibilityCard,
  SkillGapsCard,
  NextStepsCard,
  CoachQuestionsCard,
  HumanAdvantageCard,
  BenchmarksCard,
} from '@/components/analysis/AnalysisCards';
import type { AnalysisResult } from '@/types/intelligence';

export default function AnalyzePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user, hasPremiumAccess } = useAuth();
  const jobTitle = searchParams.get('job') || '';
  
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [showMicroWin, setShowMicroWin] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSignupModal, setShowSignupModal] = useState(false);

  useEffect(() => {
    if (!jobTitle) {
      router.push('/');
      return;
    }

    // Allow analysis without login for free preview
    // if (!user) {
    //   router.push('/login');
    //   return;
    // }

    // Real API call to backend with FULL MULTI-AGENT ORCHESTRATOR
    const performAnalysis = async () => {
      try {
        setIsAnalyzing(true);
        setError(null);
        
        // Call the MULTI-AGENT ORCHESTRATOR API
        const normalizedSkills = jobTitle
          ? [
              `${jobTitle} core skills`,
              `${jobTitle} domain expertise`
            ]
          : ['transferable career skills'];

        const result = await intelligenceApi.analyzeCareer({
          job_title: jobTitle,
          skills: normalizedSkills,
          location: 'United States'
        });
        
        console.log('🎯 Orchestrator analysis result:', result);
        
        setAnalysis(result);
        
        // Show micro-win notification
        setShowMicroWin(true);
      } catch (err) {
        console.error('❌ Multi-agent analysis error:', err);
        const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Multi-agent analysis failed. Please try again.';
        setError(errorMessage);
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
    return <EnhancedLoadingExperience jobTitle={jobTitle} />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-premium-bg flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 premium-bg-gradient opacity-50" />
        <div className="text-center max-w-md mx-auto px-4 relative z-10">
          <div className="w-20 h-20 bg-red-500/10 border border-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="w-10 h-10 text-red-400" />
          </div>
          <h2 className="text-3xl font-serif italic text-white mb-4">Analysis Failed</h2>
          <p className="text-premium-text-muted mb-8">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="premium-btn-primary px-8 py-3"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-premium-bg py-24 px-4 relative overflow-hidden">
      <div className="absolute inset-0 premium-bg-gradient opacity-50" />
      
      {/* Micro-Win Notification */}
      <MicroWin 
        show={showMicroWin} 
        message="Analysis Complete! Your career insights are ready." 
        xp={50} 
      />
      
      <div className="max-w-5xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-20">
          {/* Free Preview Badge */}
          {!hasPremiumAccess && (
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-premium-accent/10 border border-premium-accent/20 rounded-full mb-8">
              <Sparkles className="w-3.5 h-3.5 text-premium-accent" />
              <span className="text-premium-accent text-xs font-medium tracking-widest uppercase">Free Preview</span>
            </div>
          )}
          
          <div className="flex flex-col items-center justify-center mb-6">
            <div className="w-16 h-16 bg-premium-accent/10 border border-premium-accent/20 rounded-full flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-premium-accent animate-pulse" />
            </div>
            <h1 className="text-5xl md:text-6xl font-serif italic text-white mb-4">
              Intelligence Report
            </h1>
            <p className="text-xl text-premium-text-muted max-w-2xl mx-auto">
              Strategic career analysis for <span className="text-white font-serif italic">{jobTitle}</span>
            </p>
            <div className="mt-4 flex items-center gap-2 text-[10px] text-premium-text-muted/40 uppercase tracking-[0.2em]">
              <span>Powered by 9 AI Agents</span>
              <span className="w-1 h-1 rounded-full bg-premium-accent/30" />
              <span>Real-time Market Data</span>
            </div>
          </div>
        </div>

        {/* Multi-Agent Analysis Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Free Preview: Risk Card (always visible) */}
          <RiskCard risk={analysis?.risk || analysis?.ai_displacement_risk} />
          
          {/* Free Preview: Compatibility Card (always visible) */}
          <CompatibilityCard
            compatibility={analysis?.compatibility}
            fallbackScore={analysis?.compatibility_score ?? 0}
            fallbackHighlights={hasPremiumAccess 
              ? (analysis?.human_advantage_factors || [])
              : (analysis?.human_advantage_factors?.slice(0, 2) || [])
            }
          />

          {/* Free Preview: Skill Gaps Card (show first 3 gaps) */}
          <div className="md:col-span-2">
            <SkillGapsCard gaps={hasPremiumAccess ? (analysis?.gaps || []) : (analysis?.gaps || []).slice(0, 3)} />
            {!hasPremiumAccess && (analysis?.gaps || []).length > 3 && (
              <div className="mt-6 text-center">
                <button
                  onClick={() => setShowSignupModal(true)}
                  className="premium-btn-primary px-8 py-3 text-sm"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Unlock {(analysis?.gaps || []).length - 3} More Skill Gaps
                </button>
              </div>
            )}
          </div>
          
          {/* Free Preview: Next Steps Card (show first 3 steps) */}
          <div className="md:col-span-2">
            <NextStepsCard steps={hasPremiumAccess ? (analysis?.next_steps || []) : (analysis?.next_steps || []).slice(0, 3)} />
            {!hasPremiumAccess && (analysis?.next_steps || []).length > 3 && (
              <div className="mt-6 text-center">
                <button
                  onClick={() => setShowSignupModal(true)}
                  className="premium-btn-primary px-8 py-3 text-sm"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  See Full Personalized Roadmap
                </button>
              </div>
            )}
          </div>

          {/* Human Advantage Factors - Show preview for free users */}
          {analysis?.human_advantage_factors && analysis.human_advantage_factors.length > 0 && (
            <div className="md:col-span-2">
              <HumanAdvantageCard 
                factors={hasPremiumAccess 
                  ? analysis.human_advantage_factors 
                  : analysis.human_advantage_factors.slice(0, 2)
                } 
              />
              {!hasPremiumAccess && analysis.human_advantage_factors.length > 2 && (
                <div className="mt-6 text-center">
                  <button
                    onClick={() => setShowSignupModal(true)}
                    className="premium-btn-primary px-8 py-3 text-sm"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Unlock {analysis.human_advantage_factors.length - 2} More Advantages
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Premium: Coach Questions (premium only) */}
          {analysis?.coach_questions && analysis.coach_questions.length > 0 && (
            <div className="md:col-span-2 relative">
              <div className={!hasPremiumAccess ? 'blur-md pointer-events-none opacity-50' : ''}>
                <CoachQuestionsCard questions={analysis.coach_questions} />
              </div>
              {!hasPremiumAccess && (
                <PremiumContentOverlay 
                  onUnlock={() => setShowSignupModal(true)} 
                  feature="AI Coach Questions"
                />
              )}
            </div>
          )}

          {/* Premium: Industry Benchmarks (premium only) */}
          {analysis?.industry_benchmarks && (
            <div className="md:col-span-2 relative">
              <div className={!hasPremiumAccess ? 'blur-md pointer-events-none opacity-50' : ''}>
                <BenchmarksCard benchmarks={analysis.industry_benchmarks} />
              </div>
              {!hasPremiumAccess && (
                <PremiumContentOverlay
                  onUnlock={() => setShowSignupModal(true)}
                  feature="Industry Benchmarks"
                />
              )}
            </div>
          )}
        </div>

        {/* Social Share Section */}
        <div className="mb-12 premium-card p-8 text-center">
          <div className="max-w-2xl mx-auto">
            <h3 className="text-2xl font-serif italic text-white mb-3">Share Your Career Insights</h3>
            <p className="text-premium-text-muted mb-8">
              Help your network discover career resilience. Share your results and earn free premium features.
            </p>
            <div className="flex justify-center">
              <SocialShare
                jobTitle={jobTitle}
                riskScore={analysis?.risk?.score || 0}
                riskLevel={analysis?.risk?.level || 'Unknown'}
              />
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
          {hasPremiumAccess ? (
            <button
              onClick={() => router.push('/coach/chat')}
              className="premium-btn-primary px-10 py-4 flex items-center gap-2"
            >
              Get Personalized Coaching
              <ArrowRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={() => setShowSignupModal(true)}
              className="premium-btn-primary px-10 py-4 flex items-center gap-2"
            >
              Unlock Full Analysis
              <ArrowRight className="w-5 h-5" />
            </button>
          )}
          <button
            onClick={() => router.push('/')}
            className="text-premium-text-muted hover:text-white transition-colors text-sm uppercase tracking-widest"
          >
            Analyze Another Job
          </button>
        </div>
      </div>

      {/* Signup Modal */}
      <SignupModal
        isOpen={showSignupModal}
        onClose={() => setShowSignupModal(false)}
        jobTitle={jobTitle}
        analysisData={analysis}
      />
    </div>
  );
}
