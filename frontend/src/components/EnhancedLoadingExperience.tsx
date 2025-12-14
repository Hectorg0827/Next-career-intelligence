'use client';

import { useEffect, useState } from 'react';
import { Brain, Target, TrendingUp, Zap, Shield, Sparkles, Users, Award, Lightbulb, Rocket } from 'lucide-react';

interface LoadingContent {
  type: 'stat' | 'testimonial' | 'insight' | 'agent';
  content: {
    icon?: React.ComponentType<{ className?: string }>;
    title?: string;
    text: string;
    author?: string;
    role?: string;
    metric?: string;
    color?: string;
  };
}

const loadingContent: LoadingContent[] = [
  // Agent Updates
  {
    type: 'agent',
    content: {
      icon: Brain,
      title: 'Profile Agent',
      text: 'Analyzing your career background and experience level...',
      color: 'text-gold-primary'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Shield,
      title: 'Risk Agent',
      text: 'Evaluating AI displacement probability and automation risks...',
      color: 'text-red-400'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Target,
      title: 'Match Agent',
      text: 'Calculating compatibility with emerging career opportunities...',
      color: 'text-royal-blue-light'
    }
  },
  {
    type: 'agent',
    content: {
      icon: TrendingUp,
      title: 'Gap Agent',
      text: 'Identifying critical skill gaps and training opportunities...',
      color: 'text-gold-accent'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Lightbulb,
      title: 'Trajectory Agent',
      text: 'Forecasting your 5-year career path and growth potential...',
      color: 'text-gold-primary'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Zap,
      title: 'Orchestrator',
      text: 'Synthesizing insights from all 9 specialized AI agents...',
      color: 'text-gold-primary'
    }
  },
  // Stats
  {
    type: 'stat',
    content: {
      icon: Users,
      metric: '15,000+',
      text: 'professionals have discovered their AI-proof career path with NEXT',
      color: 'text-gold-primary'
    }
  },
  {
    type: 'stat',
    content: {
      icon: Award,
      metric: '89%',
      text: 'of users found new opportunities they never knew existed',
      color: 'text-royal-blue-light'
    }
  },
  {
    type: 'stat',
    content: {
      icon: TrendingUp,
      metric: '95%',
      text: 'reported increased confidence in their career direction',
      color: 'text-gold-accent'
    }
  },
  // Testimonials
  {
    type: 'testimonial',
    content: {
      text: 'NEXT helped me pivot from data analyst to ML engineer. 6 months later, I got a 40% raise!',
      author: 'Sarah Chen',
      role: 'Machine Learning Engineer'
    }
  },
  {
    type: 'testimonial',
    content: {
      text: 'I was worried about AI replacing my role. The analysis showed me how to become irreplaceable.',
      author: 'Michael Rodriguez',
      role: 'Marketing Strategy Lead'
    }
  },
  {
    type: 'testimonial',
    content: {
      text: 'The skill gap analysis was spot-on. I upskilled and now lead our automation projects.',
      author: 'Emily Thompson',
      role: 'Financial Analytics Manager'
    }
  },
  // Insights
  {
    type: 'insight',
    content: {
      icon: Rocket,
      title: 'Did you know?',
      text: 'The average analysis reveals 3-5 high-impact skills that can be learned in under 6 months',
      color: 'text-gold-primary'
    }
  },
  {
    type: 'insight',
    content: {
      icon: Sparkles,
      title: 'AI Insight',
      text: 'Roles combining human creativity with AI tools are growing 3x faster than traditional positions',
      color: 'text-royal-blue-light'
    }
  },
  {
    type: 'insight',
    content: {
      icon: TrendingUp,
      title: 'Career Tip',
      text: 'Focus on skills that complement AI rather than compete with it - collaboration is key',
      color: 'text-gold-accent'
    }
  }
];

interface EnhancedLoadingExperienceProps {
  jobTitle: string;
}

export default function EnhancedLoadingExperience({ jobTitle }: EnhancedLoadingExperienceProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  // Rotate content every 4 seconds
  useEffect(() => {
    const contentInterval = setInterval(() => {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % loadingContent.length);
        setIsVisible(true);
      }, 300);
    }, 4000);

    return () => clearInterval(contentInterval);
  }, []);

  // Progress bar animation (simulated)
  useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) return 95; // Stop at 95% until real completion
        return prev + Math.random() * 2;
      });
    }, 500);

    return () => clearInterval(progressInterval);
  }, []);

  const currentContent = loadingContent[currentIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-navy via-royal-navy to-blue-900 py-12 px-4 flex items-center justify-center">
      {/* Background Animation */}
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gold-primary rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-royal-blue rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="max-w-3xl w-full relative z-10">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 border border-gold-primary/30 rounded-full mb-6">
            <Sparkles className="w-4 h-4 text-gold-primary animate-pulse" />
            <span className="text-white/90 text-sm font-medium">AI Analysis In Progress</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Analyzing <span className="text-gold-primary">{jobTitle}</span>
          </h1>
          <p className="text-white/70 text-lg">
            Our 9 specialized AI agents are working together to create your personalized career intelligence report
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-12">
          <div className="flex justify-between items-center mb-3">
            <span className="text-white/70 text-sm font-medium">Analysis Progress</span>
            <span className="text-gold-primary text-sm font-bold">{Math.round(progress)}%</span>
          </div>
          <div className="h-3 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
            <div 
              className="h-full bg-gradient-to-r from-gold-primary via-gold-accent to-gold-hover rounded-full transition-all duration-500 ease-out relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white/30 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Rotating Content Card */}
        <div 
          className={`bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 md:p-12 min-h-[280px] flex items-center justify-center transition-all duration-300 ${
            isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
          }`}
        >
          {currentContent.type === 'agent' && (
            <div className="text-center">
              <div className={`w-20 h-20 mx-auto mb-6 bg-white/10 rounded-2xl flex items-center justify-center`}>
                {currentContent.content.icon && (
                  <currentContent.content.icon className={`w-10 h-10 ${currentContent.content.color}`} />
                )}
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">{currentContent.content.title}</h3>
              <p className="text-white/80 text-lg">{currentContent.content.text}</p>
            </div>
          )}

          {currentContent.type === 'stat' && (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-white/10 rounded-2xl flex items-center justify-center">
                {currentContent.content.icon && (
                  <currentContent.content.icon className={`w-8 h-8 ${currentContent.content.color}`} />
                )}
              </div>
              <div className={`text-5xl font-bold ${currentContent.content.color} mb-4`}>
                {currentContent.content.metric}
              </div>
              <p className="text-white/80 text-lg max-w-xl mx-auto">{currentContent.content.text}</p>
            </div>
          )}

          {currentContent.type === 'testimonial' && (
            <div className="text-center">
              <div className="text-6xl mb-6 opacity-30">&ldquo;</div>
              <blockquote className="text-xl md:text-2xl text-white/90 font-medium mb-6 leading-relaxed">
                {currentContent.content.text}
              </blockquote>
              <div className="flex items-center justify-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gold-primary to-gold-accent flex items-center justify-center text-xl">
                  {currentContent.content.author?.charAt(0)}
                </div>
                <div className="text-left">
                  <div className="text-white font-semibold">{currentContent.content.author}</div>
                  <div className="text-white/60 text-sm">{currentContent.content.role}</div>
                </div>
              </div>
            </div>
          )}

          {currentContent.type === 'insight' && (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 bg-white/10 rounded-2xl flex items-center justify-center">
                {currentContent.content.icon && (
                  <currentContent.content.icon className={`w-8 h-8 ${currentContent.content.color}`} />
                )}
              </div>
              <h3 className={`text-xl font-bold ${currentContent.content.color} mb-4`}>
                {currentContent.content.title}
              </h3>
              <p className="text-white/80 text-lg leading-relaxed max-w-xl mx-auto">
                {currentContent.content.text}
              </p>
            </div>
          )}
        </div>

        {/* Content Type Indicators */}
        <div className="flex justify-center gap-2 mt-8">
          {loadingContent.map((_, index) => (
            <div
              key={index}
              className={`h-1.5 rounded-full transition-all ${
                index === currentIndex 
                  ? 'w-8 bg-gold-primary' 
                  : 'w-1.5 bg-white/30'
              }`}
            />
          ))}
        </div>

        {/* Footer Message */}
        <p className="text-center text-white/50 text-sm mt-12 animate-pulse">
          This usually takes 30-60 seconds. Hang tight! 🚀
        </p>
      </div>
    </div>
  );
}
