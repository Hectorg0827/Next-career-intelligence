'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import PathwayCard from './PathwayCard';
import ImmediateStepsCard from './ImmediateStepsCard';
import RiskMitigationCard from './RiskMitigationCard';
import PathwayVisualization from './PathwayVisualization';

interface PathwayDetail {
  target_role: string;
  milestone_title: string;
  skills_to_develop: string[];
  certifications: string[];
  key_projects: string[];
  estimated_salary_range: string;
  ai_resilience_score: number;
  why_this_path: string;
  success_metrics: string[];
  market_trends?: string[];
  leadership_focus?: string[];
}

interface AlternativePath {
  target_role: string;
  why_consider: string;
  skills_to_develop: string[];
  estimated_salary_range: string;
}

interface TimelineStage {
  primary_path: PathwayDetail;
  alternative_path: AlternativePath;
}

interface PathwayNode {
  stage: string;
  role: string;
  year: number;
}

interface PathwayEdge {
  from: string;
  to: string;
  skills_required: string[];
  confidence: number;
}

interface ImmediateSteps {
  month_1_3: string[];
  month_4_6: string[];
  month_7_12: string[];
  why_start_here: string;
}

interface RiskMitigation {
  automation_threats: string[];
  protective_skills: string[];
  pivot_options: string[];
  why_these_skills: string;
}

interface CareerRoadmap {
  '3_year': TimelineStage;
  '5_year': TimelineStage;
  '10_year': TimelineStage;
  pathway_visualization: {
    nodes: PathwayNode[];
    edges: PathwayEdge[];
  };
  immediate_next_steps: ImmediateSteps;
  risk_mitigation: RiskMitigation;
}

interface CareerRoadmapTimelineProps {
  roadmap: CareerRoadmap;
  currentRole: string;
}

const CareerRoadmapTimeline: React.FC<CareerRoadmapTimelineProps> = ({ 
  roadmap, 
  currentRole 
}) => {
  const [selectedTimeline, setSelectedTimeline] = useState<'3_year' | '5_year' | '10_year'>('3_year');
  const [showAlternative, setShowAlternative] = useState(false);

  const timelineConfig = {
    '3_year': {
      label: '3 Years',
      color: 'from-green-500 to-emerald-600',
      bgColor: 'from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20',
      borderColor: 'border-green-300 dark:border-green-600',
      textColor: 'text-green-700 dark:text-green-300',
      icon: '🎯'
    },
    '5_year': {
      label: '5 Years',
      color: 'from-blue-500 to-royal-blue',
      bgColor: 'from-blue-50 to-silver-light dark:from-blue-900/20 dark:to-royal-navy/20',
      borderColor: 'border-blue-300 dark:border-blue-600',
      textColor: 'text-blue-700 dark:text-blue-300',
      icon: '🚀'
    },
    '10_year': {
      label: '10 Years',
      color: 'from-royal-blue to-gold-accent',
      bgColor: 'from-silver-soft to-silver-soft dark:from-royal-navy/20 dark:to-pink-900/20',
      borderColor: 'border-purple-300 dark:border-gold-primary',
      textColor: 'text-gold-accent dark:text-purple-300',
      icon: '👑'
    }
  };

  const currentConfig = timelineConfig[selectedTimeline];
  const currentStage = roadmap[selectedTimeline];

  return (
    <div className="w-full max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <motion.div
        className="mb-8 text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-gold-primary to-gold-accent bg-clip-text text-transparent mb-2">
          Your Career Roadmap
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          From <span className="font-semibold text-gray-900 dark:text-white">{currentRole}</span> to your future success
        </p>
      </motion.div>

      {/* Pathway Visualization */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <PathwayVisualization 
          nodes={roadmap.pathway_visualization.nodes}
          edges={roadmap.pathway_visualization.edges}
          selectedTimeline={selectedTimeline}
        />
      </motion.div>

      {/* Timeline Selector */}
      <motion.div
        className="flex flex-col sm:flex-row gap-4 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {(['3_year', '5_year', '10_year'] as const).map((timeline, index) => {
          const config = timelineConfig[timeline];
          const isSelected = selectedTimeline === timeline;

          return (
            <motion.button
              key={timeline}
              onClick={() => setSelectedTimeline(timeline)}
              className={`flex-1 p-6 rounded-2xl border-2 transition-all ${
                isSelected
                  ? `${config.borderColor} bg-gradient-to-br ${config.bgColor} shadow-lg`
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-3xl">{config.icon}</span>
                <span className={`text-sm font-bold px-3 py-1 rounded-full ${
                  isSelected 
                    ? `bg-gradient-to-r ${config.color} text-white` 
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}>
                  {config.label}
                </span>
              </div>
              <div className={`text-left ${isSelected ? config.textColor : 'text-gray-700 dark:text-gray-300'}`}>
                <div className="font-bold text-lg mb-1">
                  {roadmap[timeline].primary_path.target_role}
                </div>
                <div className="text-sm opacity-80">
                  AI Resilience: {roadmap[timeline].primary_path.ai_resilience_score}/100
                </div>
              </div>
            </motion.button>
          );
        })}
      </motion.div>

      {/* Main Pathway Card */}
      <motion.div
        key={selectedTimeline}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-6"
      >
        <PathwayCard
          pathway={currentStage.primary_path}
          timeline={currentConfig.label}
          color={currentConfig.color}
          bgColor={currentConfig.bgColor}
          borderColor={currentConfig.borderColor}
          icon={currentConfig.icon}
          isPrimary={true}
        />
      </motion.div>

      {/* Alternative Path Toggle */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mb-8"
      >
        <button
          onClick={() => setShowAlternative(!showAlternative)}
          className="w-full p-4 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 transition-all bg-gray-50 dark:bg-gray-800/50"
        >
          <div className="flex items-center justify-center space-x-3">
            <span className="text-2xl">🔀</span>
            <span className="font-semibold text-gray-900 dark:text-white">
              {showAlternative ? 'Hide' : 'View'} Alternative Path
            </span>
            <motion.svg
              className="w-5 h-5 text-gray-600 dark:text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              animate={{ rotate: showAlternative ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </motion.svg>
          </div>
        </button>

        {showAlternative && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4"
          >
            <PathwayCard
              pathway={currentStage.alternative_path}
              timeline={currentConfig.label}
              color="from-orange-500 to-red-600"
              bgColor="from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20"
              borderColor="border-orange-300 dark:border-orange-600"
              icon="🔀"
              isPrimary={false}
            />
          </motion.div>
        )}
      </motion.div>

      {/* Two-column layout for next steps and risk mitigation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
        >
          <ImmediateStepsCard steps={roadmap.immediate_next_steps} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
        >
          <RiskMitigationCard mitigation={roadmap.risk_mitigation} />
        </motion.div>
      </div>

      {/* Encouragement footer */}
      <motion.div
        className="p-6 rounded-2xl bg-gradient-to-r from-blue-50 via-silver-soft to-silver-soft dark:from-blue-900/20 dark:via-royal-navy/20 dark:to-pink-900/20 border border-blue-200 dark:border-blue-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <div className="flex items-start space-x-4">
          <span className="text-3xl flex-shrink-0">✨</span>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
              Your Journey Starts Today
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              This roadmap is your strategic guide, not a rigid plan. Markets evolve, technologies change, 
              and your goals may shift—that&apos;s okay! Focus on building transferable skills, maintaining 
              AI resilience, and staying curious. Every small step forward compounds into extraordinary 
              career growth. 🚀
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default CareerRoadmapTimeline;
