'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Loader2, ArrowLeft, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface SDRRun {
  id: string;
  started_at: string;
  completed_at: string;
  status: string;
  jobs_discovered: number;
  jobs_filtered: number;
  applications_generated: number;
  applications_submitted: number;
  error: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SDRHistoryPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [runs, setRuns] = useState<SDRRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    fetch(`${API_BASE}/api/sdr/history?user_id=${user.uid}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => setRuns(d.runs || []))
      .catch(() => setError('Could not load run history. Is the backend running?'))
      .finally(() => setLoading(false));
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h1 className="text-2xl font-bold mb-8">SDR Run History</h1>

        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 mb-6 text-red-300 text-sm">
            {error}
          </div>
        )}

        {runs.length === 0 && !error ? (
          <div className="text-center py-16 text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No SDR runs yet. Trigger your first run from the dashboard.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {runs.map(run => (
              <div key={run.id} className="bg-gray-800 rounded-xl border border-gray-700 p-5">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="font-medium">{new Date(run.started_at).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</div>
                    <div className="text-gray-500 text-sm">{new Date(run.started_at).toLocaleTimeString()}</div>
                  </div>
                  <div className={`flex items-center gap-1.5 text-sm px-2.5 py-1 rounded-full ${
                    run.status === 'complete' ? 'bg-green-900/50 text-green-300' :
                    run.status === 'error' ? 'bg-red-900/50 text-red-300' :
                    'bg-yellow-900/50 text-yellow-300'
                  }`}>
                    {run.status === 'complete' ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                    {run.status}
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4 text-center">
                  {[
                    { label: 'Discovered', value: run.jobs_discovered },
                    { label: 'Filtered', value: run.jobs_filtered },
                    { label: 'Generated', value: run.applications_generated },
                    { label: 'Submitted', value: run.applications_submitted },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <div className="text-xl font-bold">{value ?? 0}</div>
                      <div className="text-gray-500 text-xs">{label}</div>
                    </div>
                  ))}
                </div>

                {run.error && (
                  <div className="mt-3 bg-red-900/30 border border-red-800 rounded-lg p-3 text-sm text-red-300">
                    Error: {run.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
