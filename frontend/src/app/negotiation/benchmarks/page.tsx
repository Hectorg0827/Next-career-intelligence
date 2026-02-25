'use client';

import { useState } from 'react';
import { Loader2, TrendingUp, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface BenchmarkData {
  role: string;
  location: string;
  seniority: string;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  sample_size: number | null;
  data_source: string;
}

export default function SalaryBenchmarksPage() {
  const router = useRouter();
  const [role, setRole] = useState('');
  const [location, setLocation] = useState('National');
  const [seniority, setSeniority] = useState('mid');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<BenchmarkData | null>(null);

  const fetch_benchmarks = async () => {
    if (!role) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ role, location, seniority });
      const res = await fetch(`${API_BASE}/api/negotiation/benchmarks?${params}`);
      if (res.ok) setData(await res.json());
    } finally {
      setLoading(false);
    }
  };

  const maxVal = data ? data.p90 : 1;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-2xl mx-auto">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h1 className="text-2xl font-bold mb-2">Salary Benchmarks</h1>
        <p className="text-gray-400 text-sm mb-8">Real compensation data from Levels.fyi and BLS OES</p>

        <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 mb-6">
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div>
              <label className="text-gray-400 text-xs mb-1 block">Role *</label>
              <input
                value={role}
                onChange={e => setRole(e.target.value)}
                placeholder="Software Engineer"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-gray-400 text-xs mb-1 block">Location</label>
              <input
                value={location}
                onChange={e => setLocation(e.target.value)}
                placeholder="San Francisco"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-gray-400 text-xs mb-1 block">Seniority</label>
              <select
                value={seniority}
                onChange={e => setSeniority(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="junior">Junior</option>
                <option value="mid">Mid-level</option>
                <option value="senior">Senior</option>
                <option value="staff">Staff/Principal</option>
              </select>
            </div>
          </div>

          <button
            onClick={fetch_benchmarks}
            disabled={loading || !role}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 py-2.5 rounded-lg font-medium transition-colors"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4" />}
            Get Benchmarks
          </button>
        </div>

        {data && (
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="font-semibold text-lg">{data.role}</h2>
                <p className="text-gray-400 text-sm">{data.location} · {data.seniority}</p>
              </div>
              <div className="text-xs text-gray-500 text-right">
                Source: {data.data_source}<br />
                {data.sample_size && `n=${data.sample_size}`}
              </div>
            </div>

            <div className="space-y-4">
              {[
                { label: 'P25 (Entry/Below Market)', value: data.p25, color: 'bg-gray-500' },
                { label: 'P50 (Median)', value: data.p50, color: 'bg-blue-500' },
                { label: 'P75 (Strong Offer)', value: data.p75, color: 'bg-green-500' },
                { label: 'P90 (Top of Market)', value: data.p90, color: 'bg-purple-500' },
              ].map(({ label, value, color }) => (
                <div key={label}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-400">{label}</span>
                    <span className="font-semibold">${value?.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`${color} rounded-full h-2 transition-all`}
                      style={{ width: `${Math.round((value / maxVal) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-700 text-sm text-gray-400">
              <strong className="text-white">Negotiation tip:</strong> Always aim for P75 as your counter-offer target.
              Employers expect negotiation — P50 is their starting point, not yours.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
