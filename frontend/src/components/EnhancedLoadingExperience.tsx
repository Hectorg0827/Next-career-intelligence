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
      color: 'text-premium-accent'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Shield,
      title: 'Risk Agent',
      text: 'Evaluating AI displacement probability and automation risks...',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Target,
      title: 'Match Agent',
      text: 'Calculating compatibility with emerging career opportunities...',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'agent',
    content: {
      icon: TrendingUp,
      title: 'Gap Agent',
      text: 'Identifying critical skill gaps and training opportunities...',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Lightbulb,
      title: 'Trajectory Agent',
      text: 'Forecasting your 5-year career path and growth potential...',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'agent',
    content: {
      icon: Zap,
      title: 'Orchestrator',
      text: 'Synthesizing insights from all 9 specialized AI agents...',
      color: 'text-premium-accent'
    }
  },
  // Stats
  {
    type: 'stat',
    content: {
      icon: Users,
      metric: '15,000+',
      text: 'professionals have discovered their AI-proof career path with NEXT',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'stat',
    content: {
      icon: Award,
      metric: '89%',
      text: 'of users found new opportunities they never knew existed',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'stat',
    content: {
      icon: TrendingUp,
      metric: '95%',
      text: 'reported increased confidence in their career direction',
      color: 'text-premium-accent'
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
      color: 'text-premium-accent'
    }
  },
  {
    type: 'insight',
    content: {
      icon: Sparkles,
      title: 'AI Insight',
      text: 'Roles combining human creativity with AI tools are growing 3x faster than traditional positions',
      color: 'text-premium-accent'
    }
  },
  {
    type: 'insight',
    content: {
      icon: TrendingUp,
      title: 'Career Tip',
      text: 'Focus on skills that complement AI rather than compete with it - collaboration is key',
      color: 'text-premium-accent'
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
    <div className="min-h-screen bg-premium-bg py-24 px-4 flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 premium-bg-gradient opacity-50" />

      <div className="max-w-3xl w-full relative z-10">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-premium-accent/10 border border-premium-accent/20 rounded-full mb-8">
            <Sparkles className="w-3.5 h-3.5 text-premium-accent animate-pulse" />
            <span className="text-premium-accent text-[10px] font-medium tracking-[0.2em] uppercase">Intelligence Engine Active</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-serif italic text-white mb-4">
            Analyzing <span className="text-premium-accent">{jobTitle}</span>
          </h1>
          <p className="text-premium-text-muted text-lg max-w-xl mx-auto">
            Our 9 specialized AI agents are synthesizing real-time market data to architect your career strategy.
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-20 max-w-md mx-auto">
          <div className="flex justify-between items-center mb-4">
            <span className="text-premium-text-muted/60 text-[10px] uppercase tracking-widest font-medium">System Progress</span>
            <span className="text-premium-accent text-sm font-serif italic">{Math.round(progress)}%</span>
          </div>
          <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-premium-accent transition-all duration-500 ease-out relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Rotating Content Card */}
        <div 
          className={`premium-card p-10 md:p-16 min-h-[320px] flex items-center justify-center transition-all duration-500 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}
        >
          {currentContent.type === 'agent' && (
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-8 bg-premium-accent/5 border border-premium-accent/10 rounded-2xl flex items-center justify-center">
                {currentContent.content.icon && (
                  <currentContent.content.icon className={`w-10 h-10 ${currentContent.content.color}`} />
                )}
              </div>
              <h3 className="text-2xl font-serif italic text-white mb-4">{currentContent.content.title}</h3>
              <p className="text-premium-text-muted text-lg leading-relaxed">{currentContent.content.text}</p>
            </div>
          )}

          {currentContent.type === 'stat' && (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 bg-premium-accent/5 border border-premium-accent/10 rounded-2xl flex items-center justify-center">
                {currentContent.content.icon && (
                  <currentContent.content.icon className={`w-8 h-8 ${currentContent.content.color}`} />
                )}
              </div>
              <div className={`text-6xl font-serif italic ${currentContent.content.color} mb-6`}>
                {currentContent.content.metric}
              </div>
              <p className="text-premium-text-muted text-lg max-w-xl mx-auto leading-relaxed">{currentContent.content.text}</p>
            </div>
          )}

          {currentContent.type === 'testimonial' && (
            <div className="text-center">
              <div className="text-6xl font-serif text-premium-accent/20 mb-4 leading-none">&ldquo;</div>
              <blockquote className="text-xl md:text-2xl text-white font-serif italic mb-8 leading-relaxed">
                {currentContent.content.text}
              </blockquote>
              <div className="flex items-center justify-center gap-4">
                <div className="w-12 h-12 rounded-full bg-premium-accent/10 border border-premium-accent/20 flex items-center justify-center text-premium-accent font-serif italic text-xl">
                  {currentContent.content.author?.charAt(0)}
                </div>
                <div className="text-left">
                  <div className="text-white font-medium">{currentContent.content.author}</div>
                  <div className="text-premium-text-muted/60 text-xs uppercase tracking-widest">{currentContent.content.role}</div>
                </div>
              </div>
            </div>
          )}

          {currentContent.type === 'insight' && (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-8 bg-premium-accent/5 border border-premium-accent/10 rounded-2xl flex items-center justify-center">
                {currentContent.content.icon && (
                  <currentContent.content.icon className={`w-8 h-8 ${currentContent.content.color}`} />
                )}
              </div>
              <h3 className={`text-xl font-serif italic text-white mb-4`}>
                {currentContent.content.title}
              </h3>
              <p className="text-premium-text-muted text-lg leading-relaxed max-w-xl mx-auto">
                {currentContent.content.text}
              </p>
            </div>
          )}
        </div>

        {/* Content Type Indicators */}
        <div className="flex justify-center gap-3 mt-12">
          {loadingContent.map((_, index) => (
            <div
              key={index}
              className={`h-1 rounded-full transition-all duration-500 ${
                index === currentIndex 
                  ? 'w-12 bg-premium-accent' 
                  : 'w-2 bg-white/10'
              }`}
            />
          ))}
        </div>

        {/* Footer Message */}
        <p className="text-center text-premium-text-muted/30 text-[10px] uppercase tracking-[0.3em] mt-16 animate-pulse">
          Synthesizing Intelligence...
        </p>
      </div>
    </div>
  );
}
