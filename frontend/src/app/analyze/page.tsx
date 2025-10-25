'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Loader2, TrendingUp, AlertCircle, CheckCircle2, ArrowRight, DollarSign } from 'lucide-react';
import { analyzeCareer } from '@/lib/api';

export default function AnalyzePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const jobTitle = searchParams.get('job') || '';
  
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('Initializing AI analysis...');

  useEffect(() => {
    if (!jobTitle) {
      router.push('/');
      return;
    }

    // Real API call to backend with Gemini AI
    const performAnalysis = async () => {
      try {
        setIsAnalyzing(true);
        setError(null);
        
        // Show progress messages
        setTimeout(() => setLoadingMessage('Analyzing job market trends...'), 3000);
        setTimeout(() => setLoadingMessage('Calculating automation risk...'), 10000);
        setTimeout(() => setLoadingMessage('Fetching salary benchmarks...'), 20000);
        setTimeout(() => setLoadingMessage('Generating AI insights...'), 40000);
        setTimeout(() => setLoadingMessage('Almost done, finalizing report...'), 80000);
        
        // Call the real backend API
        const result = await analyzeCareer({
          job_title: jobTitle,
          skills: ['Communication', 'Problem Solving', 'Teamwork'], // Default skills for demo
          years_experience: 5, // Default experience
          location: 'United States'
        });
        
        console.log('Backend analysis result:', result);
        
        // Transform backend response to match UI expectations
        const salaryData = result.metadata?.benchmarks?.salary_benchmark;
        setAnalysis({
          jobTitle: result.job_title,
          riskScore: result.ai_displacement_risk?.score || 50,
          riskLevel: result.ai_displacement_risk?.level || 'Medium',
          aiImpact: result.ai_displacement_risk?.reasoning || 'Analysis completed',
          averageSalary: salaryData?.industry_median 
            ? `$${Math.round(salaryData.industry_median / 1000)}k`
            : 'N/A',
          salaryRange: salaryData
            ? `$${Math.round(salaryData.percentile_25 / 1000)}k - $${Math.round(salaryData.percentile_90 / 1000)}k`
            : 'N/A',
          topSkills: result.metadata?.benchmarks?.skill_demand?.top_skills?.map((s: any) => s.name) || [],
          recommendations: result.human_advantage_factors || [],
          analysisId: result.analysis_id,
          compatibilityScore: result.compatibility_score,
          augmentationPotential: result.ai_displacement_risk?.augmentation_potential
        });
      } catch (err: any) {
        console.error('Analysis error:', err);
        setError(err.response?.data?.detail || 'Failed to analyze. Please try again.');
      } finally {
        setIsAnalyzing(false);
      }
    };

    performAnalysis();
  }, [jobTitle, router]);

  if (!jobTitle) {
    return null;
  }

  if (isAnalyzing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 flex items-center justify-center">
        <div className="text-center max-w-md px-6">
          <Loader2 className="w-16 h-16 text-gold-primary animate-spin mx-auto mb-4" />
          <h2 className="text-2xl text-white font-semibold mb-2">Analyzing Your Career with AI</h2>
          <p className="text-white/70 mb-4">Processing {jobTitle}...</p>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 mt-6">
            <p className="text-gold-primary text-sm font-medium">{loadingMessage}</p>
            <p className="text-white/50 text-xs mt-2">This comprehensive analysis takes 1-2 minutes</p>
          </div>
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
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Career Analysis Report
          </h1>
          <p className="text-xl text-white/80">
            for <span className="font-semibold">{jobTitle}</span>
          </p>
        </div>

        {/* Risk Score Card */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <div className="text-center">
            <h2 className="text-white/80 text-lg mb-4">AI Automation Risk Score</h2>
            <div className={`text-7xl font-bold mb-4 ${getRiskColor(analysis.riskScore)}`}>
              {analysis.riskScore}%
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              <span className="text-white font-medium">{analysis.riskLevel} Risk</span>
            </div>
            <p className="text-white/70 mt-4">{analysis.aiImpact}</p>
          </div>
        </div>

        {/* Salary Information */}
        {analysis.averageSalary && analysis.averageSalary !== 'N/A' && (
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-4">
                <DollarSign className="w-6 h-6 text-gold-primary" />
                <h2 className="text-2xl font-bold text-white">Average Salary</h2>
              </div>
              <div className="text-5xl font-bold text-gold-primary mb-2">
                ${typeof analysis.averageSalary === 'number' 
                  ? analysis.averageSalary.toLocaleString() 
                  : analysis.averageSalary}
              </div>
              {analysis.salaryRange && analysis.salaryRange !== 'N/A' && (
                <p className="text-white/70 text-lg">
                  Typical Range: {analysis.salaryRange}
                </p>
              )}
              <p className="text-white/60 text-sm mt-2">Based on industry data</p>
            </div>
          </div>
        )}

        {/* Skills to Learn */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6" />
            Top Skills to Future-Proof Your Career
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {analysis.topSkills.map((skill: string, index: number) => (
              <div key={index} className="flex items-center gap-3 bg-white/5 rounded-lg p-4">
                <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-white">{skill}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Recommended Next Steps</h2>
          <div className="space-y-4">
            {analysis.recommendations.map((rec: string, index: number) => (
              <div key={index} className="flex items-start gap-3 bg-white/5 rounded-lg p-4">
                <div className="w-8 h-8 bg-royal-blue/30 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-semibold">{index + 1}</span>
                </div>
                <p className="text-white/90">{rec}</p>
              </div>
            ))}
          </div>
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
