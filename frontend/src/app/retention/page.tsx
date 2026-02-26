'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2, TrendingUp, TrendingDown, DollarSign, AlertTriangle, CheckCircle, FileText } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CompensationDrift {
  role: string;
  location: string;
  current_salary: number;
  market_p50: number;
  market_p75: number;
  drift_vs_p50_pct: number;
  alert_level: 'high' | 'medium' | 'none';
  alert_message: string;
  data_source: string;
}

interface MarketPulse {
  role: string;
  demand_trend: string;
  salary_distribution: { p25: number; p50: number; p75: number };
  emerging_skills: string[];
}

export default function RetentionPage() {
  const { user } = useAuth();
  const [drift, setDrift] = useState<CompensationDrift | null>(null);
  const [pulse, setPulse] = useState<MarketPulse | null>(null);
  const [loading, setLoading] = useState(false);
  const [isPlaced, setIsPlaced] = useState(false);

  // Place form state
  const [role, setRole] = useState('');
  const [company, setCompany] = useState('');
  const [salary, setSalary] = useState('');
  const [startDate, setStartDate] = useState('');
  const [placing, setPlacing] = useState(false);

  const [fetchError, setFetchError] = useState<string | null>(null);

  // Raise case state
  const [raiseCaseMode, setRaiseCaseMode] = useState(false);
  const [targetSalary, setTargetSalary] = useState('');
  const [achievements, setAchievements] = useState('');
  const [raiseResult, setRaiseResult] = useState<string | null>(null);
  const [generatingRaise, setGeneratingRaise] = useState(false);

  const fetchCompensationData = async () => {
    if (!user) return;
    setLoading(true);
    setFetchError(null);
    try {
      const [driftRes, pulseRes] = await Promise.allSettled([
        fetch(`${API_BASE}/api/retention/compensation?user_id=${user.uid}`),
        fetch(`${API_BASE}/api/retention/market-pulse?user_id=${user.uid}`),
      ]);

      if (driftRes.status === 'fulfilled' && driftRes.value.ok) {
        setDrift(await driftRes.value.json());
        setIsPlaced(true);
      }
      if (pulseRes.status === 'fulfilled' && pulseRes.value.ok) {
        setPulse(await pulseRes.value.json());
      }
      if (driftRes.status === 'rejected' && pulseRes.status === 'rejected') {
        setFetchError('Could not connect to the server. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) fetchCompensationData();
  }, [user]);

  const recordPlacement = async () => {
    if (!user || !role || !salary || !startDate) return;
    setPlacing(true);
    try {
      const res = await fetch(`${API_BASE}/api/retention/placed?user_id=${user.uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role, company, base_salary: parseInt(salary),
          start_date: startDate, location: 'National',
        }),
      });
      if (res.ok) {
        await fetchCompensationData();
      }
    } finally {
      setPlacing(false);
    }
  };

  const generateRaiseCase = async () => {
    if (!drift || !targetSalary) return;
    setGeneratingRaise(true);
    try {
      const achList = achievements.split('\n').filter(Boolean);
      const startDateMs = new Date(drift?.role ? '2024-01-01' : '2024-01-01').getTime();
      const tenureMonths = Math.floor((Date.now() - startDateMs) / (1000 * 60 * 60 * 24 * 30));

      const res = await fetch(`${API_BASE}/api/retention/raise-case?user_id=${user?.uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: drift.role,
          company: 'Current employer',
          current_salary: drift.current_salary,
          target_salary: parseInt(targetSalary),
          tenure_months: Math.max(tenureMonths, 6),
          key_achievements: achList,
          location: drift.location,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setRaiseResult(data.raise_justification_email);
      }
    } finally {
      setGeneratingRaise(false);
    }
  };

  const alertColor = (level: string) =>
    level === 'high' ? 'border-red-700 bg-red-900/30' :
    level === 'medium' ? 'border-yellow-700 bg-yellow-900/30' :
    'border-green-700 bg-green-900/30';

  const driftColor = (pct: number) =>
    pct < -15 ? 'text-red-400' : pct < -5 ? 'text-yellow-400' : 'text-green-400';

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-600 rounded-lg"><DollarSign className="w-6 h-6" /></div>
            <div>
              <h1 className="text-2xl font-bold">Compensation Monitor</h1>
              <p className="text-gray-400 text-sm">Track if your salary is keeping pace with the market after placement</p>
            </div>
          </div>
        </div>

        {fetchError && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 mb-6 text-red-300 text-sm">
            {fetchError}
          </div>
        )}

        {!isPlaced && !loading && (
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 mb-6">
            <h2 className="font-semibold mb-4">Record Your Placement</h2>
            <p className="text-gray-500 text-sm mb-4">Tell us about your current role to start monitoring your compensation.</p>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <input value={role} onChange={e => setRole(e.target.value)} placeholder="Job Title" className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500" />
              <input value={company} onChange={e => setCompany(e.target.value)} placeholder="Company" className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500" />
              <input value={salary} onChange={e => setSalary(e.target.value)} placeholder="Base Salary" type="number" className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500" />
              <input value={startDate} onChange={e => setStartDate(e.target.value)} type="date" className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500" />
            </div>
            <button onClick={recordPlacement} disabled={placing || !role || !salary || !startDate} className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 py-2.5 rounded-lg font-medium transition-colors">
              {placing ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              Record Placement
            </button>
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-purple-400" /></div>
        )}

        {drift && (
          <>
            {/* Compensation Drift Alert */}
            <div className={`rounded-xl border p-5 mb-4 ${alertColor(drift.alert_level)}`}>
              <div className="flex items-start gap-3">
                {drift.alert_level === 'none' ? (
                  <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold mb-1">{drift.alert_message}</div>
                  <div className="text-sm text-gray-400">Source: {drift.data_source}</div>
                </div>
              </div>
            </div>

            {/* Salary Comparison */}
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 mb-4">
              <h3 className="font-semibold mb-4">{drift.role} · {drift.location}</h3>
              <div className="grid grid-cols-3 gap-4 text-center mb-4">
                <div>
                  <div className="text-gray-500 text-xs mb-1">Your Salary</div>
                  <div className="text-xl font-bold">${drift.current_salary.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-xs mb-1">Market P50</div>
                  <div className="text-xl font-bold text-blue-400">${drift.market_p50.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-xs mb-1">Market P75</div>
                  <div className="text-xl font-bold text-green-400">${drift.market_p75.toLocaleString()}</div>
                </div>
              </div>
              <div className="text-center">
                <span className={`text-2xl font-bold ${driftColor(drift.drift_vs_p50_pct)}`}>
                  {drift.drift_vs_p50_pct >= 0 ? '+' : ''}{drift.drift_vs_p50_pct.toFixed(1)}%
                </span>
                <span className="text-gray-500 text-sm ml-2">vs market median</span>
              </div>
            </div>

            {/* Market Pulse */}
            {pulse && (
              <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 mb-4">
                <h3 className="font-semibold mb-3">Market Pulse</h3>
                <div className="flex items-center gap-2 mb-3">
                  {pulse.demand_trend === 'growing' ? (
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-yellow-400" />
                  )}
                  <span className="text-sm capitalize">{pulse.demand_trend} demand</span>
                </div>
                {pulse.emerging_skills.length > 0 && (
                  <div>
                    <div className="text-xs text-gray-500 mb-2">In-demand skills for your role:</div>
                    <div className="flex flex-wrap gap-2">
                      {pulse.emerging_skills.slice(0, 6).map((skill, i) => (
                        <span key={i} className="bg-gray-700 text-gray-300 text-xs rounded-full px-2.5 py-1">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Raise Case Builder */}
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Build Raise Case</h3>
                <button
                  onClick={() => setRaiseCaseMode(!raiseCaseMode)}
                  className="text-sm text-purple-400 hover:text-purple-300"
                >
                  {raiseCaseMode ? 'Hide' : 'Open Builder'}
                </button>
              </div>

              {raiseCaseMode && (
                <div className="space-y-3">
                  <div>
                    <label className="text-gray-400 text-xs mb-1 block">Target Salary</label>
                    <input value={targetSalary} onChange={e => setTargetSalary(e.target.value)} type="number" placeholder="e.g. 150000" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500" />
                  </div>
                  <div>
                    <label className="text-gray-400 text-xs mb-1 block">Key Achievements (one per line)</label>
                    <textarea value={achievements} onChange={e => setAchievements(e.target.value)} rows={4} placeholder="Led migration to new architecture that reduced latency by 40%&#10;Mentored 3 junior engineers&#10;Shipped X feature ahead of schedule" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500 resize-none" />
                  </div>
                  <button onClick={generateRaiseCase} disabled={generatingRaise || !targetSalary} className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 py-2.5 rounded-lg font-medium transition-colors">
                    {generatingRaise ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                    Generate Raise Justification
                  </button>

                  {raiseResult && (
                    <div className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap border border-gray-700 mt-3">
                      {raiseResult}
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
