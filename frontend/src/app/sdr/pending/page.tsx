'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2, CheckCircle, XCircle, Building2, MapPin, DollarSign, ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';

interface PendingApplication {
  application_id: string;
  job: {
    title: string;
    company: string;
    location: string;
    salary_min?: number;
    salary_max?: number;
    description: string;
    apply_url: string;
  };
  cover_letter: string;
  match_rationale: string;
  company_research: {
    summary?: string;
    key_insights?: string[];
    red_flags?: string[];
    growth_signals?: string[];
  } | null;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SDRPendingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [applications, setApplications] = useState<PendingApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [processing, setProcessing] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!user) return;
    fetchPending();
  }, [user]);

  const fetchPending = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sdr/pending?user_id=${user?.uid}`);
      if (res.ok) {
        const data = await res.json();
        setApplications(data.pending_applications || []);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (appId: string) => {
    setProcessing(prev => new Set([...prev, appId]));
    try {
      const res = await fetch(`${API_BASE}/api/sdr/approve/${appId}?user_id=${user?.uid}`, { method: 'POST' });
      if (res.ok) {
        setApplications(prev => prev.filter(a => a.application_id !== appId));
      }
    } finally {
      setProcessing(prev => { const s = new Set(prev); s.delete(appId); return s; });
    }
  };

  const handleReject = async (appId: string) => {
    setProcessing(prev => new Set([...prev, appId]));
    try {
      const res = await fetch(`${API_BASE}/api/sdr/reject/${appId}?user_id=${user?.uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback: null }),
      });
      if (res.ok) {
        setApplications(prev => prev.filter(a => a.application_id !== appId));
      }
    } finally {
      setProcessing(prev => { const s = new Set(prev); s.delete(appId); return s; });
    }
  };

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
          <ArrowLeft className="w-4 h-4" /> Back to SDR Dashboard
        </button>

        <h1 className="text-2xl font-bold mb-2">Applications Awaiting Approval</h1>
        <p className="text-gray-400 text-sm mb-8">
          Review each application. Approved ones will be tracked in your application pipeline.
        </p>

        {applications.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-600 opacity-50" />
            <p>No pending applications. Check back after the next SDR run.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.map(app => {
              const isExpanded = expandedId === app.application_id;
              const isProcessing = processing.has(app.application_id);

              return (
                <div key={app.application_id} className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                  {/* Header */}
                  <div className="p-5">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{app.job.title}</h3>
                        <div className="flex items-center gap-4 text-gray-400 text-sm mt-1">
                          <span className="flex items-center gap-1"><Building2 className="w-3 h-3" />{app.job.company}</span>
                          <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{app.job.location}</span>
                          {app.job.salary_min && (
                            <span className="flex items-center gap-1">
                              <DollarSign className="w-3 h-3" />
                              {app.job.salary_min.toLocaleString()}–{app.job.salary_max?.toLocaleString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Match Rationale */}
                    <div className="bg-blue-900/30 border border-blue-800 rounded-lg p-3 mb-4 text-sm text-blue-200">
                      <strong>Why this matches you:</strong> {app.match_rationale}
                    </div>

                    {/* Company Research Preview */}
                    {app.company_research?.summary && (
                      <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 mb-4">
                        {app.company_research.summary}
                        {app.company_research.red_flags && app.company_research.red_flags.length > 0 && (
                          <div className="mt-2 text-yellow-400 text-xs">
                            ⚠️ {app.company_research.red_flags[0]}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Expand/Collapse */}
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : app.application_id)}
                      className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1 mb-4"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      {isExpanded ? 'Hide' : 'View'} cover letter
                    </button>

                    {isExpanded && (
                      <div className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap mb-4 border border-gray-700">
                        {app.cover_letter}
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleApprove(app.application_id)}
                        disabled={isProcessing}
                        className="flex-1 flex items-center justify-center gap-2 bg-green-700 hover:bg-green-600 disabled:opacity-50 py-2.5 rounded-lg font-medium text-sm transition-colors"
                      >
                        {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                        Approve & Track
                      </button>
                      <button
                        onClick={() => handleReject(app.application_id)}
                        disabled={isProcessing}
                        className="flex-1 flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 py-2.5 rounded-lg font-medium text-sm transition-colors"
                      >
                        <XCircle className="w-4 h-4" />
                        Skip
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
