'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import CareerHealthGauge from '@/components/dashboard/CareerHealthGauge';
import PriorityActionCard from '@/components/dashboard/PriorityActionCard';
import JobMatchCard from '@/components/dashboard/JobMatchCard';
import HealthComponentBar from '@/components/dashboard/HealthComponentBar';
import AIGuidancePanel from '@/components/dashboard/AIGuidancePanel';
import AIProfileAssistant from '@/components/profile/AIProfileAssistant';
import SkillProfileWidget from '@/components/dashboard/SkillProfileWidget';
import SkillGapWidget from '@/components/dashboard/SkillGapWidget';
import { NoJobsEmptyState, NoActionsEmptyState } from '@/components/EmptyStates';
import { Loader2, TrendingUp, Shield, Target, Briefcase, ArrowRight, Zap, BarChart3, Brain } from 'lucide-react';

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
      <div className="min-h-screen bg-nci-bg flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-nci-primary mx-auto mb-4" />
          <p className="text-g-400 font-medium">Loading your career intelligence...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-nci-bg flex items-center justify-center">
        <div className="text-center">
          <p className="text-white mb-4">Failed to load dashboard data</p>
          <button
            onClick={fetchDashboardData}
            className="px-6 py-2 bg-nci-primary text-white rounded-xl shadow-glow-blue hover:bg-primary-600 transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: 'Career Health',
      val: data.healthScore || '--',
      chg: data.healthTrend ? `${data.healthTrend > 0 ? '+' : ''}${data.healthTrend} this quarter` : 'Calculating...',
      icon: <TrendingUp className="w-5 h-5" />,
      col: 'text-nci-accent',
      bg: 'bg-nci-accent-dim',
      border: 'border-l-nci-accent',
    },
    {
      label: 'AI Risk',
      val: 'Low',
      chg: '18% displacement',
      icon: <Shield className="w-5 h-5" />,
      col: 'text-nci-primary',
      bg: 'bg-nci-primary-dim',
      border: 'border-l-nci-primary',
    },
    {
      label: 'Matched Jobs',
      val: data.topMatches.length,
      chg: 'Active matches',
      icon: <Target className="w-5 h-5" />,
      col: 'text-nci-amber',
      bg: 'bg-nci-amber-dim',
      border: 'border-l-nci-amber',
    },
    {
      label: 'Actions',
      val: data.priorityActions.length,
      chg: 'Priority items',
      icon: <Zap className="w-5 h-5" />,
      col: 'text-nci-accent',
      bg: 'bg-nci-accent-dim',
      border: 'border-l-nci-accent',
    },
  ];

  return (
    <div className="min-h-screen bg-nci-bg relative">
      {/* Background glow */}
      <div className="absolute -top-[10%] -left-[5%] w-[500px] h-[500px] rounded-full pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(45,127,249,0.1), transparent 70%)', filter: 'blur(100px)' }} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 relative z-10 space-y-6">
        {/* Header */}
        <div className="animate-fade-in-up">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2 font-serif">
            Welcome back, {user?.email?.split('@')[0] || 'there'}
          </h1>
          <p className="text-g-400 text-base font-light">
            Here&apos;s your career intelligence for today
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          {stats.map((s) => (
            <div key={s.label} className={`glass-card p-5 border-l-[3px] ${s.border}`}>
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-xs text-g-500 mb-1.5 font-medium">{s.label}</div>
                  <div className="text-2xl font-bold font-mono text-white leading-none">{s.val}</div>
                </div>
                <div className={`w-9 h-9 rounded-lg ${s.bg} flex items-center justify-center ${s.col}`}>
                  {s.icon}
                </div>
              </div>
              <div className="mt-2.5 text-xs font-mono text-nci-accent font-medium">{s.chg}</div>
            </div>
          ))}
        </div>

        {/* Career Health Gauge */}
        <div className="animate-fade-in-up" style={{ animationDelay: '150ms' }}>
          <CareerHealthGauge
            score={data.healthScore}
            trend={data.healthTrend}
            onViewReport={() => router.push('/career-health')}
          />
        </div>

        {/* AI Proactive Guidance + Profile */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3.5 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-nci-primary" />
              <h2 className="text-lg font-semibold text-white">AI Career Guidance</h2>
            </div>
            <AIGuidancePanel maxMessages={3} showDismiss={true} />
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-nci-accent" />
              <h2 className="text-lg font-semibold text-white">Profile Intelligence</h2>
            </div>
            <AIProfileAssistant compact={true} showInferredSkills={false} />
          </div>
        </div>

        {/* Health Components Breakdown */}
        <div className="animate-fade-in-up" style={{ animationDelay: '250ms' }}>
          <h2 className="text-lg font-semibold text-white mb-4">
            Health Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
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

        {/* Skills & Gap Analysis */}
        <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <h2 className="text-lg font-semibold text-white mb-4">
            Skills & Gap Analysis
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3.5">
            <SkillProfileWidget />
            <SkillGapWidget />
          </div>
        </div>

        {/* Priority Actions */}
        <div className="animate-fade-in-up" style={{ animationDelay: '350ms' }}>
          <h2 className="text-lg font-semibold text-white mb-4">
            Priority Actions
          </h2>
          {data.priorityActions.length > 0 ? (
            <div className="space-y-3">
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
          ) : (
            <NoActionsEmptyState />
          )}
        </div>

        {/* Top Matches */}
        <div className="animate-fade-in-up" style={{ animationDelay: '400ms' }}>
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-nci-amber" />
              <h2 className="text-lg font-semibold text-white">Top Matched Opportunities</h2>
            </div>
            {data.topMatches.length > 0 && (
              <button
                onClick={() => router.push('/jobs/recommendations')}
                className="text-nci-primary text-sm font-semibold hover:text-nci-accent transition-colors flex items-center gap-1"
              >
                View All <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
          {data.topMatches.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
              {data.topMatches.map((job) => (
                <JobMatchCard
                  key={job.id}
                  job={job}
                  matchScore={job.matchScore}
                  onApply={() => router.push(`/jobs/${job.id}`)}
                />
              ))}
            </div>
          ) : (
            <NoJobsEmptyState onBrowseJobs={() => router.push('/jobs')} />
          )}
        </div>
      </div>
    </div>
  );
}
