/**
 * NEXT Career Intelligence - Jobs Marketplace Skeleton Loaders
 * Super-Premium Design System
 *
 * Beautiful loading states for jobs pages using the Skeleton component.
 */

'use client';

import React from 'react';
import { Skeleton, SkeletonJobCard } from '../../../components/ui/Skeleton';

/**
 * Jobs Search Bar Skeleton
 */
export const JobsSearchSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <div className="grid md:grid-cols-4 gap-4">
        {/* Search Input */}
        <div className="md:col-span-2">
          <Skeleton variant="text" width="30%" height={16} className="mb-2" />
          <Skeleton variant="rounded" width="100%" height={42} />
        </div>

        {/* Location */}
        <div>
          <Skeleton variant="text" width="40%" height={16} className="mb-2" />
          <Skeleton variant="rounded" width="100%" height={42} />
        </div>

        {/* Search Button */}
        <div className="flex items-end">
          <Skeleton variant="rounded" width="100%" height={42} />
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mt-4">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} variant="rounded" width={100} height={32} />
        ))}
      </div>
    </div>
  );
};

/**
 * Jobs Filter Sidebar Skeleton
 */
export const JobsFilterSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <Skeleton variant="text" width="40%" height={24} className="mb-6" />

      {/* Filter Groups */}
      {[...Array(5)].map((_, i) => (
        <div key={i} className="mb-6 pb-6 border-b border-gray-200 last:border-b-0">
          <Skeleton variant="text" width="50%" height={20} className="mb-3" />
          <div className="space-y-2">
            {[...Array(4)].map((_, j) => (
              <div key={j} className="flex items-center gap-2">
                <Skeleton variant="rounded" width={20} height={20} />
                <Skeleton variant="text" width="70%" height={16} />
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Clear Filters Button */}
      <Skeleton variant="rounded" width="100%" height={40} className="mt-4" />
    </div>
  );
};

/**
 * Job Card Skeleton
 */
export const JobCardSkeleton: React.FC = () => {
  return <SkeletonJobCard />;
};

/**
 * Jobs List Skeleton
 * Shows multiple job cards
 */
export const JobsListSkeleton: React.FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <div className="space-y-4">
      {[...Array(count)].map((_, i) => (
        <JobCardSkeleton key={i} />
      ))}
    </div>
  );
};

/**
 * Job Details Header Skeleton
 */
export const JobDetailsHeaderSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-md p-8 border border-gray-200">
      <div className="flex items-start gap-6">
        {/* Company Logo */}
        <Skeleton variant="rounded" width={80} height={80} />

        {/* Job Info */}
        <div className="flex-1">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <Skeleton variant="text" width="60%" height={32} className="mb-2" />
              <Skeleton variant="text" width="40%" height={24} className="mb-3" />
              <div className="flex items-center gap-4">
                <Skeleton variant="text" width={120} height={20} />
                <Skeleton variant="text" width={100} height={20} />
                <Skeleton variant="text" width={90} height={20} />
              </div>
            </div>
            <div className="flex gap-3">
              <Skeleton variant="rounded" width={40} height={40} />
              <Skeleton variant="rounded" width={120} height={40} />
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} variant="rounded" width={80} height={28} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Job Details Content Skeleton
 */
export const JobDetailsContentSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-md p-8 border border-gray-200">
      <div className="space-y-8">
        {/* Description Section */}
        <div>
          <Skeleton variant="text" width="30%" height={24} className="mb-4" />
          <Skeleton variant="text" width="100%" height={16} className="mb-2" />
          <Skeleton variant="text" width="95%" height={16} className="mb-2" />
          <Skeleton variant="text" width="98%" height={16} className="mb-2" />
          <Skeleton variant="text" width="92%" height={16} className="mb-2" />
        </div>

        {/* Requirements Section */}
        <div>
          <Skeleton variant="text" width="35%" height={24} className="mb-4" />
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-start gap-2 mb-2">
              <Skeleton variant="rounded" width={6} height={6} className="mt-2" />
              <Skeleton variant="text" width="90%" height={16} />
            </div>
          ))}
        </div>

        {/* Benefits Section */}
        <div>
          <Skeleton variant="text" width="25%" height={24} className="mb-4" />
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-start gap-2 mb-2">
              <Skeleton variant="rounded" width={6} height={6} className="mt-2" />
              <Skeleton variant="text" width="85%" height={16} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Job Details Sidebar Skeleton
 */
export const JobDetailsSidebarSkeleton: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Apply Card */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
        <Skeleton variant="rounded" width="100%" height={48} className="mb-4" />
        <Skeleton variant="text" width="80%" height={16} className="mb-2" />
        <Skeleton variant="text" width="70%" height={16} />
      </div>

      {/* Company Info Card */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
        <Skeleton variant="text" width="50%" height={24} className="mb-4" />
        <div className="flex items-center gap-3 mb-4">
          <Skeleton variant="rounded" width={60} height={60} />
          <div className="flex-1">
            <Skeleton variant="text" width="80%" height={20} className="mb-2" />
            <Skeleton variant="text" width="60%" height={16} />
          </div>
        </div>
        <div className="space-y-3">
          <Skeleton variant="text" width="70%" height={16} />
          <Skeleton variant="text" width="65%" height={16} />
          <Skeleton variant="text" width="75%" height={16} />
        </div>
      </div>

      {/* Similar Jobs Card */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
        <Skeleton variant="text" width="60%" height={24} className="mb-4" />
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="pb-4 border-b border-gray-200 last:border-b-0">
              <Skeleton variant="text" width="90%" height={20} className="mb-2" />
              <Skeleton variant="text" width="70%" height={16} className="mb-2" />
              <div className="flex gap-2">
                {[...Array(3)].map((_, j) => (
                  <Skeleton key={j} variant="rounded" width={60} height={24} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Jobs Statistics Banner Skeleton
 */
export const JobsStatsSkeleton: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-xl p-6 mb-6">
      <div className="grid md:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="text-center">
            <Skeleton
              variant="text"
              width={80}
              height={40}
              className="mx-auto mb-2"
            />
            <Skeleton
              variant="text"
              width={120}
              height={16}
              className="mx-auto"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Full Jobs Page Skeleton
 * Shows complete jobs marketplace loading state
 */
export const FullJobsPageSkeleton: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <JobsStatsSkeleton />
      <JobsSearchSkeleton />

      <div className="grid lg:grid-cols-4 gap-6 mt-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <JobsFilterSkeleton />
        </div>

        {/* Jobs List */}
        <div className="lg:col-span-3">
          <div className="flex items-center justify-between mb-6">
            <Skeleton variant="text" width={200} height={24} />
            <Skeleton variant="rounded" width={150} height={40} />
          </div>
          <JobsListSkeleton count={8} />
        </div>
      </div>
    </div>
  );
};

/**
 * Full Job Details Page Skeleton
 */
export const FullJobDetailsPageSkeleton: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <Skeleton variant="text" width={60} height={20} />
        <Skeleton variant="text" width={20} height={20} />
        <Skeleton variant="text" width={80} height={20} />
        <Skeleton variant="text" width={20} height={20} />
        <Skeleton variant="text" width={150} height={20} />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <JobDetailsHeaderSkeleton />
          <JobDetailsContentSkeleton />
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <JobDetailsSidebarSkeleton />
        </div>
      </div>
    </div>
  );
};

export default {
  JobsSearchSkeleton,
  JobsFilterSkeleton,
  JobCardSkeleton,
  JobsListSkeleton,
  JobDetailsHeaderSkeleton,
  JobDetailsContentSkeleton,
  JobDetailsSidebarSkeleton,
  JobsStatsSkeleton,
  FullJobsPageSkeleton,
  FullJobDetailsPageSkeleton,
};
