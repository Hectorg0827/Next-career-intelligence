'use client';

import React from 'react';
import { motion } from 'framer-motion';
import SkillClustersCard from './SkillClustersCard';
import TransferableSkillsCard from './TransferableSkillsCard';
import HiddenSkillsBadge from './HiddenSkillsBadge';
import SkillGapsRoadmap from './SkillGapsRoadmap';
import SkillStrengthMeter from './SkillStrengthMeter';

interface SkillCluster {
  category: string;
  skills: string[];
  color: string;
}

interface AdjacentSkill {
  skill: string;
  confidence: number;
  reasoning: string;
  source_skills: string[];
}

interface SkillGap {
  skill: string;
  priority: string;
  learn_difficulty: string;
  market_demand: string;
  estimated_learning_time: string;
  confidence_score: number;
  why_important: string;
}

interface SkillStrength {
  overall_score: number;
  category_scores: Record<string, number>;
  total_skills: number;
  skill_diversity: number;
  interpretation: string;
}

interface SkillInsights {
  skill_clusters: SkillCluster[];
  transferable_skills: AdjacentSkill[];
  hidden_skills: string[];
  skill_gaps_for_growth: SkillGap[];
  skill_strength_score: SkillStrength;
}

interface SkillInsightsPanelProps {
  skillInsights: SkillInsights;
  jobTitle: string;
}

const SkillInsightsPanel: React.FC<SkillInsightsPanelProps> = ({ 
  skillInsights, 
  jobTitle 
}) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 15
      }
    }
  };

  return (
    <motion.div
      className="w-full max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Header with gradient */}
      <motion.div 
        className="mb-8 text-center"
        variants={itemVariants}
      >
        <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
          Your Skill Intelligence
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          AI-powered insights for <span className="font-semibold text-gray-900 dark:text-white">{jobTitle}</span>
        </p>
      </motion.div>

      {/* Skill Strength Meter - Top center, hero element */}
      <motion.div variants={itemVariants} className="mb-8">
        <SkillStrengthMeter skillStrength={skillInsights.skill_strength_score} />
      </motion.div>

      {/* Two-column grid for main content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Left column */}
        <motion.div variants={itemVariants} className="space-y-6">
          <SkillClustersCard skillClusters={skillInsights.skill_clusters} />
          <HiddenSkillsBadge hiddenSkills={skillInsights.hidden_skills} />
        </motion.div>

        {/* Right column */}
        <motion.div variants={itemVariants} className="space-y-6">
          <TransferableSkillsCard 
            transferableSkills={skillInsights.transferable_skills} 
          />
        </motion.div>
      </div>

      {/* Full-width roadmap at bottom */}
      <motion.div variants={itemVariants}>
        <SkillGapsRoadmap skillGaps={skillInsights.skill_gaps_for_growth} />
      </motion.div>

      {/* Beautiful footer with encouragement */}
      <motion.div 
        className="mt-12 p-6 rounded-2xl bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-700"
        variants={itemVariants}
      >
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <svg 
              className="w-8 h-8 text-blue-600 dark:text-blue-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" 
              />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              Your Career Growth Strategy
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              These insights are personalized to your unique skill profile. Focus on high-priority gaps first, 
              leverage your hidden skills, and explore transferable opportunities. Remember: every expert was 
              once a beginner. 🚀
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default SkillInsightsPanel;
