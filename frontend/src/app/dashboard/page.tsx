'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import AIGuidancePanel from '@/components/dashboard/AIGuidancePanel';
import JobMatchCard from '@/components/dashboard/JobMatchCard';
import { NoJobsEmptyState } from '@/components/EmptyStates';
import { Loader2, TrendingUp, Shield, Briefcase, ArrowRight, Zap, Target } from 'lucide-react';

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

  const formatCurrency = (value?: number) => {
    if (!value) return null;
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  };

  const topMatch = data.topMatches[0];
  const marketValue = topMatch?.salaryMin && topMatch?.salaryMax
    ? `${formatCurrency(topMatch.salaryMin)} - ${formatCurrency(topMatch.salaryMax)}`
    : '—';
  const nextAction = data.priorityActions[0];
  const dueThisWeek = data.priorityActions.slice(1, 3);

  const todayCards = [
    {
      title: 'Next action',
      body: nextAction ? nextAction.title : 'Set your next career goal',
      meta: nextAction ? nextAction.description : 'Complete your profile to unlock tailored actions.',
      cta: nextAction ? 'Start now' : 'Review profile',
      onClick: () => {
        if (!nextAction) {
          router.push('/profile');
          return;
        }
        if (nextAction.type === 'warning') {
          router.push('/skills');
        } else {
          router.push('/jobs/recommendations');
        }
      },
    },
    {
      title: 'Due this week',
      body: dueThisWeek.length
        ? dueThisWeek.map((item) => item.title).join(' • ')
        : 'No upcoming tasks',
      meta: dueThisWeek.length ? 'Stay on track with your plan.' : 'We will update as new tasks arrive.',
      cta: 'View roadmap',
      onClick: () => router.push('/roadmap'),
    },
    {
      title: 'Progress',
      body: `${data.healthScore || 0}% complete`,
      meta: data.healthTrend ? `${data.healthTrend > 0 ? '+' : ''}${data.healthTrend} this quarter` : 'Career health trend updating.',
      cta: 'View report',
      onClick: () => router.push('/career-health'),
    },
  ];

  const coreTiles = [
    {
      label: 'Market Value',
      value: marketValue,
      note: topMatch ? `${topMatch.title} range` : 'Add a role to see your range.',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'text-nci-accent',
      bg: 'bg-nci-accent-dim',
    },
    {
      label: 'AI Risk',
      value: 'Low',
      note: '18% displacement risk',
      icon: <Shield className="w-5 h-5" />,
      color: 'text-nci-primary',
      bg: 'bg-nci-primary-dim',
    },
    {
      label: 'Top Match',
      value: topMatch ? `${topMatch.matchScore}%` : '—',
      note: topMatch ? `${topMatch.title} @ ${topMatch.company}` : 'No active matches yet.',
      icon: <Target className="w-5 h-5" />,
      color: 'text-nci-amber',
      bg: 'bg-nci-amber-dim',
    },
    {
      label: 'Career Health',
      value: data.healthScore || 0,
      note: 'Updated today',
      icon: <Zap className="w-5 h-5" />,
      color: 'text-nci-accent',
      bg: 'bg-nci-accent-dim',
    },
  ];

  return (
    <div className="min-h-screen bg-nci-bg relative">
      {/* Background glow */}
      <div className="absolute -top-[10%] -left-[5%] w-[500px] h-[500px] rounded-full pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(45,127,249,0.1), transparent 70%)', filter: 'blur(100px)' }} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 relative z-10 space-y-10">
        {/* Header */}
        <div className="animate-fade-in-up">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2 font-serif">
            Career Command Center
          </h1>
          <p className="text-g-400 text-base font-light">
            Welcome back, {user?.email?.split('@')[0] || 'there'}. Here&apos;s what to focus on today.
          </p>
        </div>

        {/* Today Strip */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          {todayCards.map((card) => (
            <div key={card.title} className="glass-card p-6 flex flex-col gap-4">
              <div>
                <p className="text-xs uppercase tracking-wide text-g-500 mb-2">{card.title}</p>
                <h2 className="text-lg font-semibold text-white mb-1">{card.body}</h2>
                <p className="text-sm text-g-400">{card.meta}</p>
              </div>
              <button
                onClick={card.onClick}
                className="text-sm font-semibold text-nci-primary hover:text-nci-accent transition-colors inline-flex items-center gap-2"
              >
                {card.cta} <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        {/* Core Tiles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in-up" style={{ animationDelay: '150ms' }}>
          {coreTiles.map((tile) => (
            <div key={tile.label} className="glass-card p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-g-500 mb-2 uppercase tracking-wide">{tile.label}</p>
                  <p className="text-2xl font-bold text-white">{tile.value}</p>
                </div>
                <div className={`w-10 h-10 rounded-lg ${tile.bg} ${tile.color} flex items-center justify-center`}>
                  {tile.icon}
                </div>
              </div>
              <p className="mt-3 text-sm text-g-400">{tile.note}</p>
            </div>
          ))}
        </div>

        {/* Command Center */}
        <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Command Center</h2>
            <button
              onClick={() => router.push('/roadmap')}
              className="text-sm font-semibold text-nci-primary hover:text-nci-accent transition-colors inline-flex items-center gap-2"
            >
              View roadmap <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                title: 'Resume Tailor',
                description: 'Upload your resume and generate a role-specific version in minutes.',
                cta: 'Open Resume Studio',
                onClick: () => router.push('/resume-studio'),
              },
              {
                title: 'Interview Prep',
                description: 'Practice with AI interviewer sessions and get instant feedback.',
                cta: 'Start practice',
                onClick: () => router.push('/interviewer'),
              },
              {
                title: 'Skill Builder',
                description: 'Choose one skill to level up and get a guided plan.',
                cta: 'View skills',
                onClick: () => router.push('/skills'),
              },
              {
                title: 'Career Coach',
                description: 'Ask your AI coach anything and get next-step guidance.',
                cta: 'Ask the coach',
                onClick: () => router.push('/coach'),
              },
            ].map((tool) => (
              <div key={tool.title} className="glass-card p-6 flex flex-col justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">{tool.title}</h3>
                  <p className="text-sm text-g-400">{tool.description}</p>
                </div>
                <button
                  onClick={tool.onClick}
                  className="text-sm font-semibold text-nci-primary hover:text-nci-accent transition-colors inline-flex items-center gap-2"
                >
                  {tool.cta} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* AI Guidance */}
        <div className="animate-fade-in-up" style={{ animationDelay: '250ms' }}>
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-nci-primary" />
            <h2 className="text-lg font-semibold text-white">AI Career Guidance</h2>
          </div>
          <AIGuidancePanel maxMessages={3} showDismiss={true} />
        </div>

        {/* Top Matches */}
        <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
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
