'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import CareerHealthGauge from '@/components/dashboard/CareerHealthGauge';
import PriorityActionCard from '@/components/dashboard/PriorityActionCard';
import JobMatchCard from '@/components/dashboard/JobMatchCard';
import HealthComponentBar from '@/components/dashboard/HealthComponentBar';
import { Loader2 } from 'lucide-react';

interface DashboardData {
  healthScore: number;
  healthTrend?: number;
  healthComponents: {
    name: string;
    score: number;
    description: string;
  }[];
  priorityActions: {
    type: 'warning' | 'opportunity';
    title: string;
    description: string;
  }[];
  topMatches: {
    id: string;
    title: string;
    company: string;
    location: string;
    isRemote?: boolean;
    salaryMin?: number;
    salaryMax?: number;
    matchScore: number;
    gaps?: string[];
  }[];
}

export default function Dashboard() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Fetch dashboard data
    fetchDashboardData();
  }, [authLoading, isAuthenticated, router]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Import the API client
      const { fetchDashboardData: fetchAPI } = await import('@/lib/dashboard-api');
      const apiData = await fetchAPI();

      // Transform API data to component format
      const healthScore = apiData.healthScore;
      const healthComponents = healthScore
        ? [
            {
              name: 'Profile Completeness',
              score: Math.round(healthScore.breakdown.profile_completeness),
              description: healthScore.breakdown.profile_completeness >= 80
                ? 'Your profile is nearly complete'
                : 'Complete your profile for better matches',
            },
            {
              name: 'Skill Currency',
              score: Math.round(healthScore.breakdown.skill_currency),
              description: healthScore.breakdown.skill_currency >= 70
                ? 'Your skills are up to date'
                : 'Some skills need updating',
            },
            {
              name: 'Market Activity',
              score: Math.round(healthScore.breakdown.market_activity),
              description: healthScore.breakdown.market_activity >= 80
                ? 'Good engagement with opportunities'
                : 'Increase your market activity',
            },
            {
              name: 'Goal Progress',
              score: Math.round(healthScore.breakdown.goal_progress),
              description: healthScore.breakdown.goal_progress >= 70
                ? 'Making steady progress'
                : 'Review your career goals',
            },
          ]
        : [];

      // Calculate trend from history (simplified)
      const historyTrend = healthScore?.trend === 'improving' ? 3 : healthScore?.trend === 'declining' ? -3 : 0;

      setData({
        healthScore: healthScore?.overall_score || 0,
        healthTrend: historyTrend,
        healthComponents,
        priorityActions: apiData.priorityActions.map((action) => ({
          type: action.type,
          title: action.title,
          description: action.description,
        })),
        topMatches: apiData.jobRecommendations.map((job) => ({
          id: job.id,
          title: job.title,
          company: job.company,
          location: job.location,
          isRemote: job.is_remote,
          salaryMin: job.salary_min,
          salaryMax: job.salary_max,
          matchScore: job.match_score,
          gaps: job.skill_gaps,
        })),
      });

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);

      // Fallback to empty/default state
      setData({
        healthScore: 0,
        healthComponents: [],
        priorityActions: [],
        topMatches: [],
      });
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen gradient-dark-glass flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-500 mx-auto mb-4" />
          <p className="text-white">Loading your career intelligence...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen gradient-dark-glass flex items-center justify-center">
        <div className="text-center">
          <p className="text-white">Failed to load dashboard data</p>
          <button
            onClick={fetchDashboardData}
            className="mt-4 px-6 py-2 bg-primary-500 text-white rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-dark-glass">
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.email?.split('@')[0] || 'there'}
          </h1>
          <p className="text-ink-300">
            Here's your career intelligence for today
          </p>
        </div>

        {/* Career Health Gauge */}
        <CareerHealthGauge
          score={data.healthScore}
          trend={data.healthTrend}
          onViewReport={() => router.push('/career-health')}
        />

        {/* Health Components Breakdown */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">
            Health Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.healthComponents.map((component, index) => (
              <HealthComponentBar
                key={index}
                name={component.name}
                score={component.score}
                description={component.description}
              />
            ))}
          </div>
        </div>

        {/* Priority Actions */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">
            Priority Actions
          </h2>
          <div className="space-y-4">
            {data.priorityActions.map((action, index) => (
              <PriorityActionCard
                key={index}
                type={action.type}
                title={action.title}
                description={action.description}
                onAction={() => {
                  if (action.type === 'warning') {
                    router.push('/skills');
                  } else {
                    router.push('/jobs/recommendations');
                  }
                }}
              />
            ))}
          </div>
        </div>

        {/* Top Matches */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-white">
              Top Matches
            </h2>
            <button
              onClick={() => router.push('/jobs/recommendations')}
              className="text-primary-500 font-medium hover:text-primary-400 transition-colors"
            >
              View All →
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.topMatches.map((job) => (
              <JobMatchCard
                key={job.id}
                job={job}
                matchScore={job.matchScore}
                onApply={() => router.push(`/jobs/${job.id}`)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
