'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, CheckCircle, Brain, Target, Zap, BookOpen } from 'lucide-react';
import { apiClient } from '@/lib/api';

type OnboardingStep = 1 | 2 | 3 | 4;

interface OnboardingData {
  currentRole: string;
  industry: string;
  yearsExp: string;
  skills: string[];
  goals: string[];
  learningStyle: 'videos' | 'articles' | 'courses' | 'interactive';
}

export const OnboardingSequence = () => {
  const router = useRouter();
  const [step, setStep] = useState<OnboardingStep>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState<OnboardingData>({
    currentRole: '',
    industry: '',
    yearsExp: '',
    skills: [],
    goals: [],
    learningStyle: 'courses',
  });

  const handleNext = async () => {
    if (step < 4) {
      setStep((step + 1) as OnboardingStep);
    } else {
      // Final step - complete onboarding
      await completeOnboarding();
    }
  };

  const completeOnboarding = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await apiClient.completeOnboarding({
        current_role: data.currentRole,
        industry: data.industry,
        years_experience: data.yearsExp,
        skills: data.skills,
        goals: data.goals,
        learning_style: data.learningStyle,
      });

      if (response.success) {
        // Redirect to dashboard
        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
      } else {
        setError(response.message || 'Failed to complete onboarding');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete onboarding');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep((step - 1) as OnboardingStep);
    }
  };

  const toggleSkill = (skill: string) => {
    setData({
      ...data,
      skills: data.skills.includes(skill)
        ? data.skills.filter(s => s !== skill)
        : [...data.skills, skill]
    });
  };

  const toggleGoal = (goal: string) => {
    setData({
      ...data,
      goals: data.goals.includes(goal)
        ? data.goals.filter(g => g !== goal)
        : [...data.goals, goal]
    });
  };

  const progress = (step / 4) * 100;

  return (
    <div className="min-h-screen bg-gradient-next-hero flex items-center justify-center p-4">
      {/* Container */}
      <div className="w-full max-w-2xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-next-gold transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-white/60 text-sm mt-3">
            Step {step} of 4
          </p>
        </div>

        {/* Step 1: Role & Industry */}
        {step === 1 && (
          <div className="space-y-8 animate-fade-in">
            <div>
              <h1 className="text-4xl font-heading font-bold text-white mb-3">
                Let&apos;s Get to Know You
              </h1>
              <p className="text-white/70 text-lg">
                Tell us about your current role to personalize your experience
              </p>
            </div>

            <div className="space-y-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div>
                <label className="block text-white font-semibold mb-3">
                  What&apos;s your current role?
                </label>
                <div className="space-y-2">
                  {[
                    'Software Engineer',
                    'Product Manager',
                    'Data Analyst',
                    'Marketing Manager',
                    'Sales Executive',
                    'Finance Professional',
                    'Other'
                  ].map(role => (
                    <label
                      key={role}
                      className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer border transition-all ${
                        data.currentRole === role
                          ? 'bg-next-gold/20 border-next-gold/50'
                          : 'bg-white/5 border-white/10 hover:border-white/30'
                      }`}
                    >
                      <input
                        type="radio"
                        name="role"
                        value={role}
                        checked={data.currentRole === role}
                        onChange={(e) => setData({ ...data, currentRole: e.target.value })}
                        className="w-4 h-4"
                      />
                      <span className="text-white">{role}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-white font-semibold mb-3">
                  What industry are you in?
                </label>
                <select
                  value={data.industry}
                  onChange={(e) => setData({ ...data, industry: e.target.value })}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-next-gold/50 transition-colors"
                >
                  <option value="">Select an industry</option>
                  <option value="tech">Technology</option>
                  <option value="finance">Finance & Banking</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="retail">Retail & Commerce</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="education">Education</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-white font-semibold mb-3">
                  Years of experience
                </label>
                <div className="flex gap-2">
                  {['0-2', '2-5', '5-10', '10+'].map(range => (
                    <button
                      key={range}
                      onClick={() => setData({ ...data, yearsExp: range })}
                      className={`flex-1 py-2 px-3 rounded-lg border transition-all ${
                        data.yearsExp === range
                          ? 'bg-next-gold/20 border-next-gold/50 text-next-gold'
                          : 'bg-white/5 border-white/10 text-white hover:border-white/30'
                      }`}
                    >
                      {range}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleBack}
                disabled
                className="flex-1 bg-white/10 hover:bg-white/20 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-all border border-white/20"
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={!data.currentRole || !data.industry || !data.yearsExp}
                className="flex-1 bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Skills Assessment */}
        {step === 2 && (
          <div className="space-y-8 animate-fade-in">
            <div>
              <h1 className="text-4xl font-heading font-bold text-white mb-3">
                What Skills Do You Have?
              </h1>
              <p className="text-white/70 text-lg">
                Select the skills you&apos;re most confident in
              </p>
            </div>

            <div className="space-y-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div className="grid grid-cols-2 gap-3">
                {[
                  'Leadership',
                  'Communication',
                  'Data Analysis',
                  'Problem Solving',
                  'Project Management',
                  'Technical Skills',
                  'Sales',
                  'Marketing',
                  'AI/Machine Learning',
                  'Cloud Computing',
                  'Strategy',
                  'Customer Service'
                ].map(skill => (
                  <button
                    key={skill}
                    onClick={() => toggleSkill(skill)}
                    className={`flex items-center gap-2 p-3 rounded-lg border transition-all text-left ${
                      data.skills.includes(skill)
                        ? 'bg-next-gold/20 border-next-gold/50'
                        : 'bg-white/5 border-white/10 hover:border-white/30'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                      data.skills.includes(skill)
                        ? 'bg-next-gold border-next-gold'
                        : 'border-white/30'
                    }`}>
                      {data.skills.includes(skill) && (
                        <CheckCircle className="w-4 h-4 text-next-deep-blue" />
                      )}
                    </div>
                    <span className="text-white text-sm">{skill}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleBack}
                className="flex-1 bg-white/10 hover:bg-white/20 text-white font-semibold py-3 rounded-lg transition-all border border-white/20"
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={data.skills.length === 0}
                className="flex-1 bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Career Goals */}
        {step === 3 && (
          <div className="space-y-8 animate-fade-in">
            <div>
              <h1 className="text-4xl font-heading font-bold text-white mb-3">
                What Are Your Career Goals?
              </h1>
              <p className="text-white/70 text-lg">
                Choose what you want to achieve in the next 12 months
              </p>
            </div>

            <div className="space-y-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div className="space-y-3">
                {[
                  { goal: 'Get promoted', icon: Target },
                  { goal: 'Switch careers', icon: Zap },
                  { goal: 'Learn new skills', icon: Brain },
                  { goal: 'Increase salary', icon: CheckCircle },
                  { goal: 'Improve work-life balance', icon: BookOpen },
                  { goal: 'Start a business', icon: ArrowRight }
                ].map(({ goal, icon: Icon }) => (
                  <button
                    key={goal}
                    onClick={() => toggleGoal(goal)}
                    className={`w-full flex items-start gap-3 p-4 rounded-lg border transition-all text-left ${
                      data.goals.includes(goal)
                        ? 'bg-next-gold/20 border-next-gold/50'
                        : 'bg-white/5 border-white/10 hover:border-white/30'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded border-2 flex-shrink-0 mt-0.5 flex items-center justify-center ${
                      data.goals.includes(goal)
                        ? 'bg-next-gold border-next-gold'
                        : 'border-white/30'
                    }`}>
                      {data.goals.includes(goal) && (
                        <CheckCircle className="w-4 h-4 text-next-deep-blue" />
                      )}
                    </div>
                    <div className="flex-1">
                      <Icon className="w-5 h-5 text-next-gold mb-1" />
                      <p className="text-white font-semibold">{goal}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleBack}
                className="flex-1 bg-white/10 hover:bg-white/20 text-white font-semibold py-3 rounded-lg transition-all border border-white/20"
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={data.goals.length === 0}
                className="flex-1 bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Learning Preferences */}
        {step === 4 && (
          <div className="space-y-8 animate-fade-in">
            <div>
              <h1 className="text-4xl font-heading font-bold text-white mb-3">
                How Do You Like to Learn?
              </h1>
              <p className="text-white/70 text-lg">
                We&apos;ll personalize your learning path
              </p>
            </div>

            <div className="space-y-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div className="space-y-3">
                {[
                  { style: 'videos' as const, label: 'Video Tutorials', desc: 'Learn through interactive videos' },
                  { style: 'articles' as const, label: 'Articles & Reading', desc: 'Prefer reading in-depth content' },
                  { style: 'courses' as const, label: 'Online Courses', desc: 'Structured learning paths' },
                  { style: 'interactive' as const, label: 'Interactive Exercises', desc: 'Hands-on practice' }
                ].map(({ style, label, desc }) => (
                  <button
                    key={style}
                    onClick={() => setData({ ...data, learningStyle: style })}
                    className={`w-full p-4 rounded-lg border transition-all text-left ${
                      data.learningStyle === style
                        ? 'bg-next-gold/20 border-next-gold/50'
                        : 'bg-white/5 border-white/10 hover:border-white/30'
                    }`}
                  >
                    <p className="text-white font-semibold">{label}</p>
                    <p className="text-white/60 text-sm mt-1">{desc}</p>
                  </button>
                ))}
              </div>

              <div className="bg-next-gold/10 border border-next-gold/30 rounded-lg p-4">
                <p className="text-white/90">
                  ✨ We&apos;ll use this to build your personalized learning roadmap
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleBack}
                className="flex-1 bg-white/10 hover:bg-white/20 text-white font-semibold py-3 rounded-lg transition-all border border-white/20"
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={isLoading}
                className="flex-1 bg-next-gold hover:bg-next-gold-light disabled:bg-next-gold/50 text-next-deep-blue font-heading font-bold py-3 rounded-lg transition-all shadow-next-gold hover:shadow-next-xl flex items-center justify-center gap-2"
              >
                {isLoading ? 'Building Your Path...' : 'Complete Setup'}
                {!isLoading && <ArrowRight className="w-5 h-5" />}
              </button>
            </div>

            <p className="text-center text-white/60 text-sm">
              This should only take a minute
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OnboardingSequence;
