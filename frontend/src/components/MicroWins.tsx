'use client';

import { useState, useEffect } from 'react';
import { Award, Star, Zap, TrendingUp } from 'lucide-react';

interface MicroWinProps {
  show: boolean;
  message: string;
  xp?: number;
}

export default function MicroWin({ show, message, xp = 10 }: MicroWinProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [show]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-24 right-6 z-50 animate-slide-in-right">
      <div className="bg-gradient-to-r from-gold-primary to-gold-accent rounded-2xl p-4 shadow-2xl border-2 border-gold-hover max-w-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-full">
            <Award className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="text-white font-semibold text-sm">{message}</p>
            <div className="flex items-center gap-2 mt-1">
              <Zap className="w-4 h-4 text-royal-navy" />
              <span className="text-royal-navy font-bold text-sm">+{xp} XP</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface ProgressTrackerProps {
  currentXP: number;
  level: number;
  nextLevelXP: number;
}

export function ProgressTracker({ currentXP, level, nextLevelXP }: ProgressTrackerProps) {
  const progress = (currentXP / nextLevelXP) * 100;

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Star className="w-5 h-5 text-gold-primary" />
          <span className="text-white font-semibold">Level {level}</span>
        </div>
        <span className="text-white/60 text-sm">{currentXP}/{nextLevelXP} XP</span>
      </div>
      
      <div className="h-3 bg-white/10 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-gold-primary to-gold-accent transition-all duration-500"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      
      <p className="text-white/60 text-xs mt-2">
        {nextLevelXP - currentXP} XP until next level
      </p>
    </div>
  );
}

interface FirstTaskSuggestionProps {
  jobTitle: string;
}

export function FirstTaskSuggestion({ jobTitle }: FirstTaskSuggestionProps) {
  const tasks = [
    { 
      icon: TrendingUp, 
      task: `Research 3 emerging skills in ${jobTitle}`,
      time: '3-5 min',
      xp: 25
    },
    { 
      icon: Star, 
      task: 'Update your LinkedIn headline',
      time: '2 min',
      xp: 15
    },
    { 
      icon: Award, 
      task: 'Identify one skill gap to close',
      time: '5 min',
      xp: 30
    }
  ];

  const selectedTask = tasks[Math.floor(Math.random() * tasks.length)];
  const Icon = selectedTask.icon;

  return (
    <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 backdrop-blur-md border border-purple-400/30 rounded-2xl p-6">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-purple-500/20 rounded-xl">
          <Icon className="w-6 h-6 text-purple-300" />
        </div>
        <div className="flex-1">
          <h4 className="text-white font-semibold mb-2">Your First Micro-Task</h4>
          <p className="text-white/80 text-sm mb-3">{selectedTask.task}</p>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-purple-300 font-medium">⏱️ {selectedTask.time}</span>
            <span className="text-gold-primary font-bold">+{selectedTask.xp} XP</span>
          </div>
        </div>
        <button className="px-4 py-2 bg-purple-500/30 hover:bg-purple-500/50 text-white rounded-lg text-sm font-medium transition-all">
          Start Now
        </button>
      </div>
    </div>
  );
}
