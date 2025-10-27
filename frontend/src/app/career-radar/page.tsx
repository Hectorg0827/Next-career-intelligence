'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { intelligenceApi } from '@/lib/api';
import { useAuth } from '@/lib/firebase';
import { Loader2, ShieldAlert, TrendingUp, Users, Bot, AlertCircle, Trophy, Sparkles } from 'lucide-react';
import { TrajectoryCard } from '@/components/analysis/AnalysisCards';

const DashboardCard = ({ 
  title, 
  icon, 
  children, 
  gradient = 'from-blue-600 to-purple-600' 
}: { 
  title: string; 
  icon: React.ReactNode; 
  children: React.ReactNode;
  gradient?: string;
}) => (
  <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
    <div className={`bg-gradient-to-r ${gradient} px-4 py-3 flex items-center text-white`}>
      {icon}
      <h3 className="ml-2 font-semibold">{title}</h3>
    </div>
    <div className="p-4">{children}</div>
  </div>
);

export default function CareerRadarPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    
    if (!user) {
      router.push('/login');
      return;
    }

    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const userId = user.uid;

        // Fetch all intelligence data in parallel
        const [forecast, warnings, market, peers] = await Promise.allSettled([
          intelligenceApi.getCareerForecast(userId),
          intelligenceApi.getEarlyWarnings(userId),
          intelligenceApi.getMarketPulse(),
          intelligenceApi.getPeerBenchmark(userId),
        ]);

        setData({
          forecast: forecast.status === 'fulfilled' ? forecast.value : null,
          warnings: warnings.status === 'fulfilled' ? warnings.value : null,
          market: market.status === 'fulfilled' ? market.value : null,
          peers: peers.status === 'fulfilled' ? peers.value : null,
        });
      } catch (err) {
        console.error('Failed to load dashboard data', err);
        setError('Failed to load some dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-gold-500 mx-auto mb-4" />
          <p className="text-white">Loading your career intelligence...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <div className="container mx-auto p-4 md:p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center mb-2">
            <Sparkles className="h-8 w-8 text-gold-500 mr-3" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gold-500 to-yellow-300 bg-clip-text text-transparent">
              Career Radar Dashboard
            </h1>
          </div>
          <p className="text-gray-400">Your AI-powered career intelligence command center</p>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-6 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Career Forecast */}
          <div className="lg:col-span-2">
            <DashboardCard 
              title="Career Trajectory Forecast" 
              icon={<TrendingUp className="h-5 w-5" />}
              gradient="from-emerald-600 to-teal-600"
            >
              {data?.forecast?.paths && data.forecast.paths.length > 0 ? (
                <div className="space-y-4">
                  {data.forecast.paths.slice(0, 3).map((path: any, i: number) => (
                    <div key={i} className="bg-gray-700/50 rounded-lg p-4 border-l-4 border-gold-500">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-white text-lg">{path.title || path.role}</h4>
                        <span className="text-xs bg-gold-500/20 text-gold-300 px-2 py-1 rounded">
                          {path.probability}% likely
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 mb-2">{path.description || 'Career path analysis'}</p>
                      <div className="flex gap-4 text-xs text-gray-400">
                        <span>⏱️ Timeline: {path.timeline || '1-2 years'}</span>
                        <span>💰 Salary: {path.salary_potential || 'TBD'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400">Complete your profile and analyze some jobs to see your career forecast.</p>
              )}
            </DashboardCard>
          </div>

          {/* Early Warnings */}
          <DashboardCard 
            title="Early Warning System" 
            icon={<ShieldAlert className="h-5 w-5" />}
            gradient="from-red-600 to-orange-600"
          >
            {data?.warnings?.alerts && data.warnings.alerts.length > 0 ? (
              <div className="space-y-3">
                {data.warnings.alerts.slice(0, 3).map((alert: any, i: number) => (
                  <div key={i} className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                    <div className="flex items-start">
                      <AlertCircle className="h-4 w-4 text-red-400 mr-2 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm text-red-200">{alert.message || alert.alert}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Confidence: {alert.confidence || 'High'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <ShieldAlert className="h-12 w-12 text-green-500 mx-auto mb-2 opacity-50" />
                <p className="text-green-400">✓ No critical warnings</p>
                <p className="text-xs text-gray-400 mt-1">Your career path looks stable</p>
              </div>
            )}
          </DashboardCard>

          {/* Market Pulse */}
          <DashboardCard 
            title="Market Intelligence" 
            icon={<Bot className="h-5 w-5" />}
            gradient="from-blue-600 to-cyan-600"
          >
            {data?.market?.insights && data.market.insights.length > 0 ? (
              <div className="space-y-2">
                {data.market.insights.slice(0, 4).map((insight: any, i: number) => (
                  <div key={i} className="flex items-start space-x-2 text-sm">
                    <span className="text-blue-400">•</span>
                    <p className="text-gray-300">{typeof insight === 'string' ? insight : insight.message}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">Live market data will appear here as you engage with the system.</p>
            )}
          </DashboardCard>

          {/* Peer Benchmarking */}
          <DashboardCard 
            title="Peer Insights" 
            icon={<Users className="h-5 w-5" />}
            gradient="from-purple-600 to-pink-600"
          >
            {data?.peers?.cohort_stats ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Your Cohort Size</span>
                  <span className="text-lg font-bold text-white">{data.peers.cohort_stats.count || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Salary Percentile</span>
                  <span className="text-lg font-bold text-gold-400">{data.peers.cohort_stats.salary_percentile || 'N/A'}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Career Velocity</span>
                  <span className="text-lg font-bold text-emerald-400">{data.peers.cohort_stats.velocity || 'Steady'}</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-400">Peer data will be available once you complete your profile.</p>
            )}
          </DashboardCard>

          {/* Quick Actions */}
          <DashboardCard 
            title="Quick Actions" 
            icon={<Trophy className="h-5 w-5" />}
            gradient="from-gold-600 to-yellow-600"
          >
            <div className="space-y-2">
              <button 
                onClick={() => router.push('/jobs/browse')}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg text-sm transition"
              >
                Browse Jobs
              </button>
              <button 
                onClick={() => router.push('/career-coach')}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg text-sm transition"
              >
                Talk to AI Coach
              </button>
              <button 
                onClick={() => router.push('/settings')}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg text-sm transition"
              >
                Update Profile
              </button>
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
}
