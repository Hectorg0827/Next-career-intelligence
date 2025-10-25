'use client';

import { useEffect, useState } from 'react';
import { Sparkles, TrendingUp, Award, Target, CheckCircle2 } from 'lucide-react';
import { FirstTaskSuggestion } from './MicroWins';

interface InstantSnapshotProps {
  jobTitle: string;
}

export default function InstantSnapshot({ jobTitle }: InstantSnapshotProps) {
  const [progress, setProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState(0);

  const phases = [
    { label: 'Analyzing job market...', icon: TrendingUp, duration: 3000 },
    { label: 'Identifying key skills...', icon: Sparkles, duration: 4000 },
    { label: 'Calculating risk factors...', icon: Target, duration: 5000 },
    { label: 'Generating insights...', icon: Award, duration: 3000 }
  ];

  useEffect(() => {
    // Simulate progressive loading
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) return 100;
        return prev + 2;
      });
    }, 300);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const phaseInterval = setInterval(() => {
      setCurrentPhase(prev => {
        if (prev >= phases.length - 1) return prev;
        return prev + 1;
      });
    }, 4000);

    return () => clearInterval(phaseInterval);
  }, []);

  // Quick insights to show immediately
  const quickInsights = [
    { label: 'Industry Demand', value: 'High', color: 'text-green-400' },
    { label: 'Skill Transferability', value: 'Medium-High', color: 'text-blue-400' },
    { label: 'Future Outlook', value: 'Growing', color: 'text-purple-400' }
  ];

  return (
    <div className="space-y-6">
      {/* Instant Value - Show Immediately */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 animate-fade-in">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-gold-primary/20 rounded-lg">
            <Sparkles className="w-5 h-5 text-gold-primary" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg">Quick Snapshot</h3>
            <p className="text-white/60 text-sm">Initial insights for {jobTitle}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {quickInsights.map((insight, idx) => (
            <div 
              key={idx}
              className="bg-white/5 rounded-xl p-4 border border-white/10"
              style={{ animationDelay: `${idx * 200}ms` }}
            >
              <div className="text-white/60 text-xs mb-1">{insight.label}</div>
              <div className={`${insight.color} font-semibold text-lg`}>{insight.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Progressive Reveal - Analysis Phases */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-gold-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-gold-primary"></span>
          </span>
          Deep Analysis in Progress
        </h4>

        <div className="space-y-3">
          {phases.map((phase, idx) => {
            const Icon = phase.icon;
            const isCompleted = idx < currentPhase;
            const isCurrent = idx === currentPhase;

            return (
              <div 
                key={idx}
                className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                  isCurrent ? 'bg-gold-primary/10 border border-gold-primary/30' : 
                  isCompleted ? 'bg-white/5' : 'opacity-50'
                }`}
              >
                <div className={`p-2 rounded-lg ${
                  isCompleted ? 'bg-green-500/20' :
                  isCurrent ? 'bg-gold-primary/20' : 'bg-white/5'
                }`}>
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : (
                    <Icon className={`w-5 h-5 ${isCurrent ? 'text-gold-primary' : 'text-white/40'}`} />
                  )}
                </div>
                <span className={`flex-1 ${
                  isCurrent ? 'text-white font-medium' :
                  isCompleted ? 'text-white/70' : 'text-white/40'
                }`}>
                  {phase.label}
                </span>
                {isCurrent && (
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-gold-primary rounded-full animate-bounce"></div>
                    <div className="w-1.5 h-1.5 bg-gold-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-1.5 h-1.5 bg-gold-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-white/60 mb-2">
            <span>Analysis Progress</span>
            <span>{Math.min(progress, 100)}%</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-gold-primary to-gold-accent transition-all duration-300 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Engagement Section - Tips while waiting */}
      <div className="bg-gradient-to-r from-gold-primary/10 to-gold-accent/10 backdrop-blur-md border border-gold-primary/20 rounded-2xl p-6">
        <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
          <Award className="w-5 h-5 text-gold-primary" />
          Did You Know?
        </h4>
        <p className="text-white/80 text-sm leading-relaxed">
          Our AI analyzes over 50+ data points including job market trends, salary benchmarks, 
          skill demand, and automation probability to give you the most accurate career insights.
        </p>
        <div className="mt-4 flex items-center gap-2 text-gold-primary text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>Your personalized report will be ready in moments...</span>
        </div>
      </div>

      {/* First Micro-Task - Keep users engaged */}
      <FirstTaskSuggestion jobTitle={jobTitle} />
    </div>
  );
}
