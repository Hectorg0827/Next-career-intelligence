'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2, Bot, CheckCircle, Clock, XCircle, TrendingUp, Settings, History, ChevronRight, Play } from 'lucide-react';

interface SDRStatus {
  is_enabled: boolean;
  criteria_configured: boolean;
  quota_used_this_week: number;
  quota_limit: number;
  pending_approvals: number;
  last_run: {
    started_at: string;
    completed_at: string;
    status: string;
    jobs_discovered: number;
    applications_generated: number;
    applications_submitted: number;
  } | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SDRDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [status, setStatus] = useState<SDRStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    fetchStatus();
  }, [user]);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sdr/status?user_id=${user?.uid}`);
      if (res.ok) {
        setStatus(await res.json());
        setError(null);
      } else {
        setError(`Failed to load SDR status (${res.status})`);
      }
    } catch (e) {
      setError('Could not connect to the server. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const triggerRun = async () => {
    if (!user || running) return;
    setRunning(true);
    try {
      await fetch(`${API_BASE}/api/sdr/run?user_id=${user.uid}`, { method: 'POST', body: JSON.stringify({}) });
      setTimeout(fetchStatus, 3000);
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  const quotaPct = status ? Math.round((status.quota_used_this_week / status.quota_limit) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Autonomous Job Search</h1>
              <p className="text-gray-400 text-sm">AI-powered SDR pipeline — finds, researches, and prepares applications for your approval</p>
            </div>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 mb-6 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Setup prompt if not configured */}
        {!status?.criteria_configured && (
          <div className="bg-yellow-900/30 border border-yellow-700 rounded-xl p-6 mb-6">
            <h2 className="font-semibold text-yellow-300 mb-2">Get Started</h2>
            <p className="text-gray-300 text-sm mb-4">Configure your job search criteria to start receiving autonomous applications.</p>
            <button
              onClick={() => router.push('/sdr/configure')}
              className="bg-yellow-600 hover:bg-yellow-500 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Configure SDR Criteria
            </button>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Weekly Quota */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-gray-400 text-sm">Weekly Quota</span>
              <TrendingUp className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-3xl font-bold mb-2">
              {status?.quota_used_this_week ?? 0}/{status?.quota_limit ?? 5}
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 rounded-full h-2 transition-all"
                style={{ width: `${Math.min(quotaPct, 100)}%` }}
              />
            </div>
            <p className="text-gray-500 text-xs mt-2">Applications submitted this week</p>
          </div>

          {/* Pending Approvals */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-gray-400 text-sm">Pending Approval</span>
              <Clock className="w-4 h-4 text-yellow-400" />
            </div>
            <div className="text-3xl font-bold mb-2 text-yellow-400">
              {status?.pending_approvals ?? 0}
            </div>
            {(status?.pending_approvals ?? 0) > 0 && (
              <button
                onClick={() => router.push('/sdr/pending')}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                Review applications <ChevronRight className="w-3 h-3" />
              </button>
            )}
            {(status?.pending_approvals ?? 0) === 0 && (
              <p className="text-gray-500 text-xs">No applications awaiting review</p>
            )}
          </div>

          {/* SDR Status */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-gray-400 text-sm">Pipeline Status</span>
              {status?.is_enabled ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400" />
              )}
            </div>
            <div className={`text-xl font-bold mb-2 ${status?.is_enabled ? 'text-green-400' : 'text-red-400'}`}>
              {status?.is_enabled ? 'Active' : 'Disabled'}
            </div>
            <p className="text-gray-500 text-xs">
              {status?.is_enabled ? 'Runs every Monday at 6 AM' : 'Enable in configuration'}
            </p>
          </div>
        </div>

        {/* Last Run Details */}
        {status?.last_run && (
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 mb-6">
            <h3 className="font-semibold mb-3 text-gray-200">Last Pipeline Run</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-400">{status.last_run.jobs_discovered}</div>
                <div className="text-gray-500 text-xs">Jobs Found</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-400">{status.last_run.applications_generated}</div>
                <div className="text-gray-500 text-xs">Applications Generated</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-400">{status.last_run.applications_submitted}</div>
                <div className="text-gray-500 text-xs">Submitted</div>
              </div>
            </div>
            <p className="text-gray-600 text-xs mt-3">
              Last run: {new Date(status.last_run.started_at).toLocaleDateString()}
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={triggerRun}
            disabled={running || !status?.criteria_configured}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg font-medium transition-colors"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Run Now
          </button>

          <button
            onClick={() => router.push('/sdr/configure')}
            className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-5 py-2.5 rounded-lg font-medium transition-colors"
          >
            <Settings className="w-4 h-4" />
            Configure
          </button>

          {(status?.pending_approvals ?? 0) > 0 && (
            <button
              onClick={() => router.push('/sdr/pending')}
              className="flex items-center gap-2 bg-yellow-700 hover:bg-yellow-600 px-5 py-2.5 rounded-lg font-medium transition-colors"
            >
              <Clock className="w-4 h-4" />
              Review {status?.pending_approvals} Pending
            </button>
          )}

          <button
            onClick={() => router.push('/sdr/history')}
            className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-5 py-2.5 rounded-lg font-medium transition-colors"
          >
            <History className="w-4 h-4" />
            History
          </button>
        </div>

        {/* How it works */}
        <div className="mt-8 bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="font-semibold mb-4 text-gray-300">How the SDR Pipeline Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { step: '1', label: 'Discovery', desc: 'Finds jobs matching your criteria from all aggregated sources', color: 'bg-blue-600' },
              { step: '2', label: 'Research', desc: 'Researches each company using news and funding data', color: 'bg-purple-600' },
              { step: '3', label: 'Synthesis', desc: 'Generates a tailored cover letter and match rationale', color: 'bg-pink-600' },
              { step: '4', label: 'Your Approval', desc: 'You review and approve before anything is submitted', color: 'bg-green-600' },
            ].map(({ step, label, desc, color }) => (
              <div key={step} className="flex flex-col items-center text-center">
                <div className={`${color} w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm mb-2`}>
                  {step}
                </div>
                <div className="font-medium text-sm mb-1">{label}</div>
                <div className="text-gray-500 text-xs">{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
