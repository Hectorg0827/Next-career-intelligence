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

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 pt-24 pb-12 px-4">
      {/* Micro-Win Notification */}
      <MicroWin
        show={showMicroWin}
        message="Analysis Complete! Your career insights are ready."
        xp={50}
      />

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12">
          {/* Free Preview Badge */}
          {!hasPremiumAccess && (
            <div className="inline-flex items-center gap-2 px-3 sm:px-4 py-2 bg-gold-primary/20 border border-gold-primary/40 rounded-full mb-4 sm:mb-6 animate-pulse-slow">
              <Sparkles className="w-4 h-4 text-gold-primary flex-shrink-0" />
              <span className="text-gold-primary text-xs sm:text-sm font-semibold">Free Preview - Sign up to see full analysis</span>
            </div>
          )}

          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-7 h-7 sm:w-10 sm:h-10 text-gold-primary mr-2 sm:mr-3 animate-pulse flex-shrink-0" />
            <h1 className="text-2xl sm:text-4xl md:text-5xl font-bold text-white">
              Multi-Agent Analysis Report
            </h1>
          </div>
          <p className="text-base sm:text-xl text-white/80">
            for <span className="font-semibold text-gold-primary">{jobTitle}</span>
          </p>
          <p className="text-xs sm:text-sm text-white/60 mt-2">Powered by 9 AI agents working in harmony</p>
        </div>

        {/* Multi-Agent Analysis Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
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
              <div className="mt-4 text-center">
                <button
                  onClick={() => setShowSignupModal(true)}
                  className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Unlock {(analysis?.gaps || []).length - 3} More Skill Gaps
                </button>
              </div>
            )}
          </div>
          
          {/* Free Preview: Next Steps Card (show first 3 steps) */}
          <div className="md:col-span-2">
            <NextStepsCard steps={hasPremiumAccess ? (analysis?.next_steps || []) : (analysis?.next_steps || []).slice(0, 3)} />
            {!hasPremiumAccess && (analysis?.next_steps || []).length > 3 && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => setShowSignupModal(true)}
                  className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
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
                <div className="mt-4 text-center">
                  <button
                    onClick={() => setShowSignupModal(true)}
                    className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    Unlock {analysis.human_advantage_factors.length - 2} More Advantages
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Premium: Coach Questions (premium only) */}
          {analysis?.coach_questions && analysis.coach_questions.length > 0 && (
            <div className="md:col-span-2 relative">
              <div className={!hasPremiumAccess ? 'blur-sm pointer-events-none' : ''}>
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
              <div className={!hasPremiumAccess ? 'blur-sm pointer-events-none' : ''}>
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
        <div className="mb-8 bg-gradient-to-r from-gold-primary/10 to-gold-accent/10 backdrop-blur-sm border border-gold-primary/20 rounded-2xl p-4 sm:p-6">
          <div className="text-center mb-4">
            <h3 className="text-xl sm:text-2xl font-bold text-white mb-2">Share Your Career Insights!</h3>
            <p className="text-white/70 text-sm sm:text-base">
              Help your network discover career resilience. Share your results and earn free premium features!
            </p>
          </div>
          <div className="flex justify-center">
            <SocialShare
              jobTitle={jobTitle}
              riskScore={analysis?.risk?.score || 0}
              riskLevel={analysis?.risk?.level || 'Unknown'}
            />
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {hasPremiumAccess ? (
            <button
              onClick={() => router.push('/coach/chat')}
              className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-pink-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
            >
              Get Personalized Coaching
              <ArrowRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={() => setShowSignupModal(true)}
              className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
            >
              Unlock Full Analysis - Free
              <ArrowRight className="w-5 h-5" />
            </button>
          )}
          <button
            onClick={() => router.push('/')}
            className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
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
