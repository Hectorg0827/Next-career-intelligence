'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Loader2, DollarSign, TrendingUp, Scale, ChevronRight, BookOpen } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AnalysisResult {
  market_analysis: {
    median_salary: number;
    percentile_25: number;
    percentile_75: number;
    percentile_90: number;
    data_source: string;
  };
  fairness_score: number;
  fairness_label: string;
  lifetime_value_delta: number;
  leverage_points: string[];
  recommended_counter: { base_salary: number; bonus?: number; additional_requests?: string[] };
  negotiation_script: string;
  fallback_positions: string[];
  meso_offers: {
    label: string;
    description: string;
    base_salary: number;
    total_comp_estimate: number;
    batna_note: string;
  }[];
}

export default function NegotiationPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'script' | 'meso'>('analysis');

  // Form state
  const [role, setRole] = useState('');
  const [company, setCompany] = useState('');
  const [baseSalary, setBaseSalary] = useState('');
  const [bonus, setBonus] = useState('0');
  const [location, setLocation] = useState('National');

  const analyze = async () => {
    if (!user || !role || !baseSalary) return;
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/api/negotiation/analyze-offer?user_id=${user.uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role,
          company,
          base_salary: parseInt(baseSalary),
          bonus: parseInt(bonus) || 0,
          location,
        }),
      });
      if (res.ok) setResult(await res.json());
    } finally {
      setAnalyzing(false);
    }
  };

  const fairnessColor = (score: number) =>
    score >= 75 ? 'text-green-400' : score >= 55 ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-600 rounded-lg"><DollarSign className="w-6 h-6" /></div>
            <div>
              <h1 className="text-2xl font-bold">Salary Negotiation Coach</h1>
              <p className="text-gray-400 text-sm">Real market data • MESO tactics • Word-for-word scripts</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Offer Input Form */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h2 className="font-semibold mb-4">Enter Your Offer</h2>
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm mb-1 block">Job Title *</label>
                <input
                  value={role}
                  onChange={e => setRole(e.target.value)}
                  placeholder="e.g. Senior Software Engineer"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-500"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm mb-1 block">Company</label>
                <input
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                  placeholder="e.g. Stripe"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-500"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm mb-1 block">Base Salary (annual) *</label>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">$</span>
                  <input
                    value={baseSalary}
                    onChange={e => setBaseSalary(e.target.value)}
                    placeholder="130000"
                    type="number"
                    className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-400 text-sm mb-1 block">Target Bonus</label>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">$</span>
                  <input
                    value={bonus}
                    onChange={e => setBonus(e.target.value)}
                    placeholder="0"
                    type="number"
                    className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-400 text-sm mb-1 block">Location</label>
                <input
                  value={location}
                  onChange={e => setLocation(e.target.value)}
                  placeholder="San Francisco, CA"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-500"
                />
              </div>

              <button
                onClick={analyze}
                disabled={analyzing || !role || !baseSalary}
                className="w-full flex items-center justify-center gap-2 bg-green-700 hover:bg-green-600 disabled:opacity-50 py-2.5 rounded-lg font-medium transition-colors"
              >
                {analyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4" />}
                {analyzing ? 'Analyzing...' : 'Analyze Offer'}
              </button>
            </div>

            {/* Quick Links */}
            <div className="mt-4 pt-4 border-t border-gray-700 space-y-2">
              <button onClick={() => router.push('/negotiation/benchmarks')} className="w-full flex items-center justify-between text-sm text-gray-400 hover:text-white py-1">
                <span className="flex items-center gap-2"><Scale className="w-4 h-4" /> Salary Benchmarks</span>
                <ChevronRight className="w-4 h-4" />
              </button>
              <button onClick={() => router.push('/negotiation/scripts')} className="w-full flex items-center justify-between text-sm text-gray-400 hover:text-white py-1">
                <span className="flex items-center gap-2"><BookOpen className="w-4 h-4" /> Script Library</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Results */}
          {result && (
            <div className="space-y-4">
              {/* Fairness Score */}
              <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Fairness Score</span>
                  <span className="text-xs text-gray-500">Source: {result.market_analysis.data_source}</span>
                </div>
                <div className={`text-4xl font-bold ${fairnessColor(result.fairness_score)}`}>
                  {result.fairness_score}<span className="text-lg text-gray-500">/100</span>
                </div>
                <div className="text-sm text-gray-400 mt-1">{result.fairness_label}</div>

                <div className="grid grid-cols-3 gap-3 mt-4 text-center text-sm">
                  <div>
                    <div className="text-gray-500 text-xs">P25</div>
                    <div className="font-semibold">${result.market_analysis.percentile_25?.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Median</div>
                    <div className="font-semibold text-blue-400">${result.market_analysis.median_salary?.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">P75</div>
                    <div className="font-semibold">${result.market_analysis.percentile_75?.toLocaleString()}</div>
                  </div>
                </div>

                <div className={`mt-3 text-sm font-medium ${result.lifetime_value_delta >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  5-year value vs market: {result.lifetime_value_delta >= 0 ? '+' : ''}${result.lifetime_value_delta?.toLocaleString()}
                </div>
              </div>

              {/* Tabs */}
              <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                <div className="flex border-b border-gray-700">
                  {(['analysis', 'script', 'meso'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === tab ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}
                    >
                      {tab === 'analysis' ? 'Counter Offer' : tab === 'script' ? 'Script' : 'MESO Options'}
                    </button>
                  ))}
                </div>

                <div className="p-5">
                  {activeTab === 'analysis' && (
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-sm font-medium text-gray-400 mb-2">Recommended Counter</h3>
                        <div className="bg-green-900/30 border border-green-800 rounded-lg p-3">
                          <div className="text-2xl font-bold text-green-400">
                            ${result.recommended_counter.base_salary?.toLocaleString()}
                          </div>
                          <div className="text-sm text-gray-400">base salary target</div>
                          {result.recommended_counter.additional_requests?.map((req, i) => (
                            <div key={i} className="text-xs text-green-300 mt-1">+ {req}</div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-400 mb-2">Your Leverage Points</h3>
                        <ul className="space-y-1">
                          {result.leverage_points.map((point, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                              <span className="text-green-400 mt-0.5">•</span> {point}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-400 mb-2">Fallback Positions</h3>
                        <ul className="space-y-1">
                          {result.fallback_positions.map((pos, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                              <span className="text-yellow-400 mt-0.5">→</span> {pos}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {activeTab === 'script' && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-400 mb-2">Word-for-Word Script</h3>
                      <div className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap border border-gray-700">
                        {result.negotiation_script}
                      </div>
                    </div>
                  )}

                  {activeTab === 'meso' && (
                    <div className="space-y-3">
                      <p className="text-xs text-gray-500 mb-3">MESO = Multiple Equivalent Simultaneous Offers. Present these 3 options to give the employer choice while anchoring higher.</p>
                      {result.meso_offers.map((offer, i) => (
                        <div key={i} className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                          <div className="font-medium text-sm mb-1">{offer.label}</div>
                          <div className="text-xs text-gray-400 mb-2">{offer.description}</div>
                          <div className="text-lg font-bold">${offer.base_salary?.toLocaleString()}</div>
                          <div className="text-xs text-gray-500">est. total: ${offer.total_comp_estimate?.toLocaleString()}</div>
                          <div className="text-xs text-blue-400 mt-2 italic">{offer.batna_note}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
