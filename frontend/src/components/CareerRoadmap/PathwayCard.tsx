'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface PathwayCardProps {
  pathway: any;
  timeline: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
  isPrimary: boolean;
}

const PathwayCard: React.FC<PathwayCardProps> = ({
  pathway,
  timeline,
  color,
  bgColor,
  borderColor,
  icon,
  isPrimary
}) => {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className={`rounded-3xl border-2 ${borderColor} bg-gradient-to-br ${bgColor} shadow-xl overflow-hidden`}>
      {/* Header */}
      <div className={`p-6 bg-gradient-to-r ${color}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className="text-4xl">{icon}</span>
            <div>
              <h3 className="text-2xl font-bold text-white">
                {pathway.target_role}
              </h3>
              <p className="text-white/90 text-sm mt-1">
                {isPrimary ? 'Recommended Path' : 'Alternative Option'} • {timeline}
              </p>
            </div>
          </div>
          
          {pathway.ai_resilience_score && (
            <div className="text-right">
              <div className="text-3xl font-bold text-white">
                {pathway.ai_resilience_score}
              </div>
              <div className="text-white/80 text-xs font-medium">
                AI Resilience
              </div>
            </div>
          )}
        </div>

        {pathway.milestone_title && (
          <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
            <div className="text-white/80 text-xs font-semibold mb-1">MILESTONE</div>
            <div className="text-white font-medium">{pathway.milestone_title}</div>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="p-6 space-y-4">
        {/* Why This Path - Always visible for primary, part of alternative */}
        {isPrimary && pathway.why_this_path && (
          <div className="p-4 rounded-xl bg-white dark:bg-gray-800 border-2 border-blue-200 dark:border-blue-700">
            <div className="flex items-start space-x-3">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h4 className="font-bold text-gray-900 dark:text-white mb-1">
                  💡 Why This Path?
                </h4>
                <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                  {pathway.why_this_path}
                </p>
              </div>
            </div>
          </div>
        )}

        {!isPrimary && pathway.why_consider && (
          <div className="p-4 rounded-xl bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-200 dark:border-orange-700">
            <div className="flex items-start space-x-3">
              <span className="text-2xl flex-shrink-0">🤔</span>
              <div className="flex-1">
                <h4 className="font-bold text-gray-900 dark:text-white mb-1">
                  Why Consider This?
                </h4>
                <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                  {pathway.why_consider}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Salary Range */}
        {pathway.estimated_salary_range && (
          <div className="flex items-center justify-between p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">💰</span>
              <div>
                <div className="text-xs font-semibold text-green-700 dark:text-green-300 uppercase tracking-wide">
                  Estimated Salary
                </div>
                <div className="text-lg font-bold text-green-900 dark:text-green-100">
                  {pathway.estimated_salary_range}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Expandable Sections */}
        <div className="space-y-2">
          {/* Skills to Develop */}
          {pathway.skills_to_develop && pathway.skills_to_develop.length > 0 && (
            <ExpandableSection
              title="Skills to Develop"
              icon="🎓"
              count={pathway.skills_to_develop.length}
              isExpanded={expandedSection === 'skills'}
              onToggle={() => toggleSection('skills')}
            >
              <div className="flex flex-wrap gap-2">
                {pathway.skills_to_develop.map((skill: string, index: number) => (
                  <motion.span
                    key={skill}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="px-3 py-1.5 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium border border-blue-200 dark:border-blue-700"
                  >
                    {skill}
                  </motion.span>
                ))}
              </div>
            </ExpandableSection>
          )}

          {/* Certifications */}
          {pathway.certifications && pathway.certifications.length > 0 && (
            <ExpandableSection
              title="Recommended Certifications"
              icon="📜"
              count={pathway.certifications.length}
              isExpanded={expandedSection === 'certs'}
              onToggle={() => toggleSection('certs')}
            >
              <ul className="space-y-2">
                {pathway.certifications.map((cert: string, index: number) => (
                  <motion.li
                    key={cert}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center space-x-2 text-gray-700 dark:text-gray-300"
                  >
                    <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm">{cert}</span>
                  </motion.li>
                ))}
              </ul>
            </ExpandableSection>
          )}

          {/* Key Projects */}
          {pathway.key_projects && pathway.key_projects.length > 0 && (
            <ExpandableSection
              title="Key Projects to Lead"
              icon="🚧"
              count={pathway.key_projects.length}
              isExpanded={expandedSection === 'projects'}
              onToggle={() => toggleSection('projects')}
            >
              <ul className="space-y-2">
                {pathway.key_projects.map((project: string, index: number) => (
                  <motion.li
                    key={project}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-start space-x-2 text-gray-700 dark:text-gray-300"
                  >
                    <span className="text-gold-primary dark:text-gold-hover mt-0.5">▸</span>
                    <span className="text-sm">{project}</span>
                  </motion.li>
                ))}
              </ul>
            </ExpandableSection>
          )}

          {/* Success Metrics */}
          {pathway.success_metrics && pathway.success_metrics.length > 0 && (
            <ExpandableSection
              title="Success Metrics"
              icon="📊"
              count={pathway.success_metrics.length}
              isExpanded={expandedSection === 'metrics'}
              onToggle={() => toggleSection('metrics')}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {pathway.success_metrics.map((metric: string, index: number) => (
                  <motion.div
                    key={metric}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-3 rounded-lg bg-silver-soft dark:bg-royal-navy/20 border border-silver-soft dark:border-gold-accent"
                  >
                    <div className="text-sm font-medium text-royal-navy dark:text-silver-light">
                      {metric}
                    </div>
                  </motion.div>
                ))}
              </div>
            </ExpandableSection>
          )}

          {/* Market Trends */}
          {pathway.market_trends && pathway.market_trends.length > 0 && (
            <ExpandableSection
              title="Market Trends"
              icon="📈"
              count={pathway.market_trends.length}
              isExpanded={expandedSection === 'trends'}
              onToggle={() => toggleSection('trends')}
            >
              <div className="flex flex-wrap gap-2">
                {pathway.market_trends.map((trend: string, index: number) => (
                  <motion.span
                    key={trend}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="px-3 py-1.5 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-sm font-medium"
                  >
                    {trend}
                  </motion.span>
                ))}
              </div>
            </ExpandableSection>
          )}
        </div>
      </div>
    </div>
  );
};

// Reusable Expandable Section Component
interface ExpandableSectionProps {
  title: string;
  icon: string;
  count: number;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const ExpandableSection: React.FC<ExpandableSectionProps> = ({
  title,
  icon,
  count,
  isExpanded,
  onToggle,
  children
}) => {
  return (
    <div className="rounded-xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <span className="text-xl">{icon}</span>
          <span className="font-semibold text-gray-900 dark:text-white">{title}</span>
          <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-bold">
            {count}
          </span>
        </div>
        <motion.svg
          className="w-5 h-5 text-gray-600 dark:text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 bg-gray-50 dark:bg-gray-800/50">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PathwayCard;
