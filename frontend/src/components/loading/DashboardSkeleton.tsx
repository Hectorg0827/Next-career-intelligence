/**
 * NEXT Career Intelligence - Dashboard Skeleton Loaders
 * Super-Premium Design System
 *
 * Beautiful loading states for dashboard pages using the Skeleton component.
 */

'use client';

import React from 'react';
import { Skeleton, SkeletonCard } from '../../../components/ui/Skeleton';

/**
 * Dashboard Analysis Form Skeleton
 */
export const DashboardFormSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8 border border-next-bg-light">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Skeleton variant="rounded" width={48} height={48} />
        <Skeleton variant="text" width="40%" height={32} />
      </div>

      {/* Form Fields */}
      <div className="space-y-6">
        {/* First Row */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <Skeleton variant="text" width="30%" height={20} className="mb-2" />
            <Skeleton variant="rounded" width="100%" height={42} />
          </div>
          <div>
            <Skeleton variant="text" width="25%" height={20} className="mb-2" />
            <Skeleton variant="rounded" width="100%" height={42} />
          </div>
        </div>

        {/* Skills textarea */}
        <div>
          <Skeleton variant="text" width="35%" height={20} className="mb-2" />
          <Skeleton variant="rounded" width="100%" height={84} />
        </div>

        {/* Second Row */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <Skeleton variant="text" width="40%" height={20} className="mb-2" />
            <Skeleton variant="rounded" width="100%" height={42} />
          </div>
          <div>
            <Skeleton variant="text" width="45%" height={20} className="mb-2" />
            <Skeleton variant="rounded" width="100%" height={42} />
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-4 mt-6">
          <Skeleton variant="rounded" width="50%" height={48} />
          <Skeleton variant="rounded" width="50%" height={48} />
        </div>
      </div>
    </div>
  );
};

/**
 * AI Displacement Risk Analysis Skeleton
 */
export const RiskAnalysisSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8 border border-next-bg-light">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Skeleton variant="rounded" width={40} height={40} />
        <Skeleton variant="text" width="45%" height={28} />
      </div>

      {/* Risk Score */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Skeleton variant="rounded" width={140} height={52} />
          <Skeleton variant="text" width={80} height={48} />
        </div>

        {/* Details */}
        <div className="space-y-3">
          <Skeleton variant="text" width="70%" height={20} />
          <Skeleton variant="text" width="75%" height={20} />
          <Skeleton variant="rounded" width="100%" height={80} className="mt-4" />
        </div>
      </div>

      {/* Comparison Card */}
      <div className="mt-6">
        <Skeleton variant="text" width="30%" height={24} className="mb-4" />
        <Skeleton variant="rounded" width="100%" height={120} />
      </div>
    </div>
  );
};

/**
 * Industry Benchmarks Section Skeleton
 */
export const BenchmarksSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8">
      <Skeleton variant="text" width="35%" height={28} className="mb-6" />

      <div className="space-y-8">
        {/* Skill Demand */}
        <div>
          <Skeleton variant="text" width="40%" height={24} className="mb-4" />
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton variant="text" width="30%" height={20} />
                <Skeleton variant="rounded" width="60%" height={24} />
              </div>
            ))}
          </div>
        </div>

        {/* Salary Benchmarking */}
        <div>
          <Skeleton variant="text" width="40%" height={24} className="mb-4" />
          <Skeleton variant="rounded" width="100%" height={240} />
        </div>

        {/* Market Trends */}
        <div>
          <Skeleton variant="text" width="50%" height={24} className="mb-4" />
          <div className="grid md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} variant="rounded" width="100%" height={100} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Skill Insights Skeleton
 */
export const SkillInsightsSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8">
      <Skeleton variant="text" width="35%" height={28} className="mb-6" />

      {/* Overall Score */}
      <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 to-silver-soft rounded-xl">
        <Skeleton variant="text" width="40%" height={24} className="mb-3" />
        <div className="flex items-center gap-4">
          <Skeleton variant="text" width={80} height={60} />
          <div className="flex-1">
            <Skeleton variant="rounded" width="100%" height={16} className="mb-2" />
            <Skeleton variant="text" width="85%" height={20} />
          </div>
        </div>
      </div>

      {/* Transferable Skills */}
      <div className="mb-6">
        <Skeleton variant="text" width="40%" height={24} className="mb-3" />
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} variant="rounded" width="100%" height={120} />
          ))}
        </div>
      </div>

      {/* Hidden Skills */}
      <div className="mb-6">
        <Skeleton variant="text" width="40%" height={24} className="mb-3" />
        <div className="flex flex-wrap gap-2">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} variant="rounded" width={100} height={36} />
          ))}
        </div>
      </div>

      {/* Skill Gaps */}
      <div>
        <Skeleton variant="text" width="35%" height={24} className="mb-3" />
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} variant="rounded" width="100%" height={120} />
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Visual Career Map Skeleton
 */
export const CareerMapSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8">
      <Skeleton variant="text" width="40%" height={28} className="mb-4" />
      <Skeleton variant="text" width="75%" height={20} className="mb-6" />

      {/* Sankey Diagram Placeholder */}
      <Skeleton variant="rounded" width="100%" height={400} className="mb-6" />

      {/* Share Buttons */}
      <div className="flex gap-3">
        <Skeleton variant="rounded" width={120} height={40} />
        <Skeleton variant="rounded" width={120} height={40} />
        <Skeleton variant="rounded" width={120} height={40} />
      </div>
    </div>
  );
};

/**
 * Career Roadmap Details Skeleton
 */
export const RoadmapDetailsSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8">
      <Skeleton variant="text" width="35%" height={28} className="mb-6" />

      {[...Array(3)].map((_, i) => (
        <div key={i} className="mb-8 last:mb-0">
          <Skeleton variant="text" width="25%" height={24} className="mb-4" />

          {/* Primary Path Card */}
          <div className="bg-gradient-to-r from-blue-50 to-silver-soft p-6 rounded-xl mb-4">
            <Skeleton variant="text" width="50%" height={24} className="mb-2" />
            <Skeleton variant="text" width="70%" height={20} className="mb-4" />

            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <Skeleton variant="text" width="40%" height={18} className="mb-2" />
                {[...Array(3)].map((_, j) => (
                  <Skeleton key={j} variant="text" width="90%" height={16} className="mb-1" />
                ))}
              </div>
              <div>
                <Skeleton variant="text" width="35%" height={18} className="mb-2" />
                {[...Array(2)].map((_, j) => (
                  <Skeleton key={j} variant="text" width="85%" height={16} className="mb-1" />
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-blue-200 flex justify-between">
              <Skeleton variant="text" width="40%" height={18} />
              <Skeleton variant="text" width="30%" height={18} />
            </div>
          </div>

          {/* Alternative Paths */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <Skeleton variant="text" width="35%" height={20} className="mb-2" />
            {[...Array(3)].map((_, j) => (
              <Skeleton key={j} variant="text" width="75%" height={16} className="mb-1" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * Transition Pathways Skeleton
 */
export const TransitionPathwaysSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl shadow-next-lg p-8">
      <Skeleton variant="text" width="50%" height={28} className="mb-6" />

      <div className="grid md:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="p-6 border-2 border-gray-200 rounded-xl">
            <Skeleton variant="text" width="60%" height={24} className="mb-2" />

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between mb-1">
                <Skeleton variant="text" width="40%" height={16} />
                <Skeleton variant="text" width="20%" height={16} />
              </div>
              <Skeleton variant="rounded" width="100%" height={8} />
            </div>

            {/* Details */}
            <div className="space-y-3">
              <div>
                <Skeleton variant="text" width="35%" height={16} className="mb-2" />
                <div className="flex flex-wrap gap-2">
                  {[...Array(4)].map((_, j) => (
                    <Skeleton key={j} variant="rounded" width={80} height={28} />
                  ))}
                </div>
              </div>
              <Skeleton variant="text" width="70%" height={16} />
              <Skeleton variant="text" width="65%" height={16} />
              <Skeleton variant="text" width="60%" height={16} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Full Dashboard Loading State
 * Shows all sections with skeleton loaders
 */
export const FullDashboardSkeleton: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-8">
        <DashboardFormSkeleton />
        <RiskAnalysisSkeleton />
        <BenchmarksSkeleton />
        <SkillInsightsSkeleton />
        <CareerMapSkeleton />
        <RoadmapDetailsSkeleton />
        <TransitionPathwaysSkeleton />
      </div>
    </div>
  );
};

export default {
  DashboardFormSkeleton,
  RiskAnalysisSkeleton,
  BenchmarksSkeleton,
  SkillInsightsSkeleton,
  CareerMapSkeleton,
  RoadmapDetailsSkeleton,
  TransitionPathwaysSkeleton,
  FullDashboardSkeleton,
};
