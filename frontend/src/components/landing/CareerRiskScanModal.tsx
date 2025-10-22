import React, { useState, useRef, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, TrendingDown, TrendingUp, Zap, ArrowRight, Brain, Briefcase } from 'lucide-react';
import Link from 'next/link';

interface ScanResults {
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  strengths: string[];
  vulnerabilities: string[];
  jobMatches: Array<{
    title: string;
    demandIncrease: string;
  }>;
  estimatedTimeToUpskill: string;
}

export const CareerRiskScanModal = ({ 
  isOpen, 
  onClose 
}: { 
  isOpen: boolean;
  onClose: () => void;
}) => {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<ScanResults | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  const [formData, setFormData] = useState({
    jobTitle: '',
    industry: '',
    yearsExperience: '',
    skills: '',
    location: '',
    email: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleNext = async () => {
    if (step === 2) {
      // Validate form
      if (!formData.jobTitle || !formData.industry || !formData.yearsExperience) {
        alert('Please fill in all required fields');
        return;
      }
      
      // Move to loading
      setStep(3);
      
      // Simulate AI analysis
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock results (in production, this would come from your API)
      setResults({
        riskScore: 72,
        riskLevel: 'high',
        strengths: [
          'Strong leadership experience',
          'Proven track record in team management',
          'Cross-functional collaboration skills'
        ],
        vulnerabilities: [
          'Limited AI/ML technical skills',
          'Lack of data analytics expertise',
          'Traditional management approach'
        ],
        jobMatches: [
          { title: 'AI Operations Manager', demandIncrease: '+240%' },
          { title: 'Change Management Director', demandIncrease: '+185%' },
          { title: 'Digital Strategy Consultant', demandIncrease: '+165%' }
        ],
        estimatedTimeToUpskill: '8-12 weeks'
      });
      
      setStep(4);
    } else if (step === 1) {
      setStep(2);
    } else if (step === 4) {
      // Move to signup
      setStep(5);
    }
  };

  const handlePrevious = () => {
    if (step > 1 && step !== 3) {
      setStep(step - 1);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-400';
      case 'medium':
        return 'text-yellow-400';
      case 'high':
        return 'text-orange-400';
      case 'critical':
        return 'text-red-400';
      default:
        return 'text-white';
    }
  };

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'bg-green-500/20';
      case 'medium':
        return 'bg-yellow-500/20';
      case 'high':
        return 'bg-orange-500/20';
      case 'critical':
        return 'bg-red-500/20';
      default:
        return 'bg-white/10';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-gradient-to-br from-next-deep-blue via-next-deep-blue to-next-deep-blue border border-next-gold/20 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-white/60 hover:text-white transition-colors z-10 bg-white/10 hover:bg-white/20 rounded-full p-2"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Progress indicator */}
        {step < 5 && (
          <div className="h-1 bg-white/10">
            <div 
              className="h-full bg-gradient-next-gold transition-all duration-500"
              style={{ width: `${(step / 4) * 100}%` }}
            />
          </div>
        )}

        <div className="p-8 md:p-12">
          {/* Step 1: Welcome */}
          {step === 1 && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Brain className="w-8 h-8 text-next-gold" />
                  <h2 className="text-3xl font-heading font-bold text-white">
                    Free Career Risk Scan
                  </h2>
                </div>
                <p className="text-white/70">
                  Get an instant AI analysis of your career stability and discover opportunities aligned with emerging job markets.
                </p>
              </div>

              <div className="space-y-3 bg-white/5 rounded-lg p-6 border border-white/10">
                <div className="flex gap-3">
                  <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white font-semibold">Automation Risk Assessment</p>
                    <p className="text-white/60 text-sm">Powered by latest labor market data</p>
                  </div>
                </div>
                
                <div className="flex gap-3">
                  <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white font-semibold">Personalized Job Recommendations</p>
                    <p className="text-white/60 text-sm">Matched to your skills and experience</p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white font-semibold">Upskilling Roadmap</p>
                    <p className="text-white/60 text-sm">Clear path to career resilience</p>
                  </div>
                </div>
              </div>

              <div className="bg-next-gold/10 border border-next-gold/30 rounded-lg p-4">
                <p className="text-white/70 text-sm">
                  ⏱️ Takes just <strong>2 minutes</strong>. No credit card required.
                </p>
              </div>

              <button
                onClick={handleNext}
                className="w-full bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2 group"
              >
                Let&apos;s Get Started
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          )}

          {/* Step 2: Form */}
          {step === 2 && (
            <form ref={formRef} className="space-y-6 animate-fade-in">
              <div>
                <h3 className="text-2xl font-heading font-bold text-white mb-6">
                  Tell us about your role
                </h3>
              </div>

              <div>
                <label className="block text-white font-semibold mb-2">
                  Job Title <span className="text-next-gold">*</span>
                </label>
                <input
                  type="text"
                  name="jobTitle"
                  value={formData.jobTitle}
                  onChange={handleInputChange}
                  placeholder="e.g., Product Manager, Software Engineer"
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Industry <span className="text-next-gold">*</span>
                  </label>
                  <select
                    name="industry"
                    value={formData.industry}
                    onChange={handleInputChange}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-next-gold/50 transition-colors"
                  >
                    <option value="">Select industry</option>
                    <option value="tech">Technology</option>
                    <option value="finance">Finance</option>
                    <option value="healthcare">Healthcare</option>
                    <option value="manufacturing">Manufacturing</option>
                    <option value="retail">Retail</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Years of Experience <span className="text-next-gold">*</span>
                  </label>
                  <select
                    name="yearsExperience"
                    value={formData.yearsExperience}
                    onChange={handleInputChange}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-next-gold/50 transition-colors"
                  >
                    <option value="">Select years</option>
                    <option value="0-2">0-2 years</option>
                    <option value="2-5">2-5 years</option>
                    <option value="5-10">5-10 years</option>
                    <option value="10+">10+ years</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-white font-semibold mb-2">
                  Key Skills (comma separated)
                </label>
                <textarea
                  name="skills"
                  value={formData.skills}
                  onChange={handleInputChange}
                  placeholder="e.g., Leadership, Python, Data Analysis"
                  rows={3}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors resize-none"
                />
              </div>

              <div>
                <label className="block text-white font-semibold mb-2">
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="City, Country"
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>

              <div className="flex gap-4 pt-6">
                <button
                  type="button"
                  onClick={handlePrevious}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white font-semibold py-3 rounded-lg transition-colors border border-white/20"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={handleNext}
                  className="flex-1 bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl"
                >
                  Analyze My Career
                </button>
              </div>
            </form>
          )}

          {/* Step 3: Loading */}
          {step === 3 && (
            <div className="space-y-8 py-12 animate-fade-in">
              <div className="text-center">
                <h3 className="text-2xl font-heading font-bold text-white mb-2">
                  Analyzing your career...
                </h3>
                <p className="text-white/60">
                  Our AI is evaluating market trends and your profile
                </p>
              </div>

              {/* Animated loading visualization */}
              <div className="flex justify-center py-8">
                <div className="relative w-32 h-32">
                  {/* Rotating circles */}
                  <svg className="absolute inset-0 w-full h-full animate-spin-slow">
                    <circle
                      cx="64"
                      cy="64"
                      r="50"
                      fill="none"
                      stroke="url(#loadingGradient)"
                      strokeWidth="3"
                    />
                    <defs>
                      <linearGradient id="loadingGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#CBA135" />
                        <stop offset="100%" stopColor="#1E3C78" />
                      </linearGradient>
                    </defs>
                  </svg>

                  {/* Inner circle */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-20 h-20 bg-gradient-next-gold/20 rounded-full flex items-center justify-center border border-next-gold/40">
                      <Brain className="w-10 h-10 text-next-gold animate-pulse-gold" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Loading stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center animate-pulse">
                  <p className="text-next-gold text-2xl font-bold">50K+</p>
                  <p className="text-white/60 text-xs">Job postings</p>
                </div>
                <div className="text-center animate-pulse" style={{ animationDelay: '0.2s' }}>
                  <p className="text-next-gold text-2xl font-bold">12M</p>
                  <p className="text-white/60 text-xs">Data points</p>
                </div>
                <div className="text-center animate-pulse" style={{ animationDelay: '0.4s' }}>
                  <p className="text-next-gold text-2xl font-bold">98%</p>
                  <p className="text-white/60 text-xs">Accuracy</p>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Results */}
          {step === 4 && results && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h3 className="text-2xl font-heading font-bold text-white mb-2">
                  Your Career Analysis
                </h3>
                <p className="text-white/60">
                  Based on {formData.jobTitle} in {formData.industry}
                </p>
              </div>

              {/* Risk Score */}
              <div className={`rounded-lg p-6 border ${getRiskBgColor(results.riskLevel)} border-current`}>
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-white font-semibold">Career Risk Score</h4>
                  <span className={`text-3xl font-bold ${getRiskColor(results.riskLevel)}`}>
                    {results.riskScore}%
                  </span>
                </div>
                <p className={`text-sm font-semibold ${getRiskColor(results.riskLevel)} capitalize`}>
                  {results.riskLevel} Risk Level
                </p>
                <p className="text-white/70 text-sm mt-2">
                  Your role has a {results.riskLevel} probability of significant market disruption in the next 3-5 years.
                </p>
              </div>

              {/* Strengths */}
              <div>
                <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  Your Strengths
                </h4>
                <div className="space-y-2">
                  {results.strengths.map((strength, i) => (
                    <div key={i} className="flex items-start gap-3 bg-white/5 rounded p-3">
                      <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      <p className="text-white/80">{strength}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Vulnerabilities */}
              <div>
                <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-400" />
                  Areas to Strengthen
                </h4>
                <div className="space-y-2">
                  {results.vulnerabilities.map((vuln, i) => (
                    <div key={i} className="flex items-start gap-3 bg-orange-500/10 rounded p-3 border border-orange-500/20">
                      <AlertCircle className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                      <p className="text-white/80">{vuln}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Job Matches */}
              <div>
                <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-next-gold" />
                  Emerging Opportunities
                </h4>
                <div className="space-y-2">
                  {results.jobMatches.map((job, i) => (
                    <div key={i} className="flex items-center justify-between bg-white/5 rounded p-4 border border-white/10 hover:border-next-gold/30 transition-colors">
                      <span className="text-white">{job.title}</span>
                      <span className="text-green-400 font-semibold text-sm">{job.demandIncrease}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Upskill estimate */}
              <div className="bg-next-gold/10 border border-next-gold/30 rounded-lg p-4">
                <p className="text-white/80">
                  <span className="font-semibold">Estimated upskilling time:</span> {results.estimatedTimeToUpskill}
                </p>
              </div>

              {/* CTA */}
              <button
                onClick={handleNext}
                className="w-full bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2 group"
              >
                See Your Personalized Roadmap
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={handlePrevious}
                className="w-full bg-white/10 hover:bg-white/20 text-white font-semibold py-3 rounded-lg transition-colors border border-white/20"
              >
                Back
              </button>
            </div>
          )}

          {/* Step 5: Signup CTA */}
          {step === 5 && (
            <div className="space-y-6 animate-fade-in py-8">
              <div className="text-center">
                <Zap className="w-12 h-12 text-next-gold mx-auto mb-4" />
                <h3 className="text-2xl font-heading font-bold text-white mb-2">
                  Unlock Your Full Roadmap
                </h3>
                <p className="text-white/70">
                  Get personalized strategies, skill recommendations, and job-matching to secure your future.
                </p>
              </div>

              <div className="space-y-3 bg-white/5 rounded-lg p-6 border border-white/10">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white font-semibold">AI-Powered Career Coach</p>
                    <p className="text-white/60 text-sm">Chat with your personal AI mentor</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white font-semibold">Weekly Insights</p>
                    <p className="text-white/60 text-sm">Market trends relevant to your role</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white font-semibold">Learning Resources</p>
                    <p className="text-white/60 text-sm">Curated courses to close skill gaps</p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-white font-semibold mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="your@email.com"
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-next-gold/50 transition-colors"
                />
              </div>

              <Link 
                href="/dashboard"
                className="w-full block bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl text-center"
              >
                Start Your Free Trial
              </Link>

              <p className="text-white/60 text-center text-sm">
                No credit card required. Free forever tier available.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CareerRiskScanModal;
