'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2, Plus, X, Save, ArrowLeft } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SDRConfigurePage() {
  const { user } = useAuth();
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [roles, setRoles] = useState<string[]>(['']);
  const [salaryMin, setSalaryMin] = useState(100000);
  const [locations, setLocations] = useState<string[]>(['Remote']);
  const [blacklist, setBlacklist] = useState<string[]>([]);
  const [quota, setQuota] = useState(5);
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [isEnabled, setIsEnabled] = useState(true);
  const [newBlacklistEntry, setNewBlacklistEntry] = useState('');

  const addRole = () => setRoles([...roles, '']);
  const removeRole = (i: number) => setRoles(roles.filter((_, idx) => idx !== i));
  const updateRole = (i: number, val: string) => {
    const updated = [...roles];
    updated[i] = val;
    setRoles(updated);
  };

  const addLocation = () => setLocations([...locations, '']);
  const removeLocation = (i: number) => setLocations(locations.filter((_, idx) => idx !== i));
  const updateLocation = (i: number, val: string) => {
    const updated = [...locations];
    updated[i] = val;
    setLocations(updated);
  };

  const addBlacklist = () => {
    if (newBlacklistEntry.trim()) {
      setBlacklist([...blacklist, newBlacklistEntry.trim()]);
      setNewBlacklistEntry('');
    }
  };

  const save = async () => {
    if (!user) return;
    setSaving(true);
    try {
      const payload = {
        target_roles: roles.filter(Boolean),
        salary_min: salaryMin,
        salary_max: 0,
        locations: locations.filter(Boolean),
        company_blacklist: blacklist,
        company_whitelist: [],
        quota_weekly: quota,
        remote_required: remoteOnly,
        is_enabled: isEnabled,
      };

      const res = await fetch(`${API_BASE}/api/sdr/configure?user_id=${user.uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setSaved(true);
        setTimeout(() => router.push('/sdr'), 1000);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-2xl mx-auto">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h1 className="text-2xl font-bold mb-2">Configure SDR Pipeline</h1>
        <p className="text-gray-400 text-sm mb-8">Set your job search criteria. The AI will only show you opportunities that match.</p>

        <div className="space-y-6">
          {/* Target Roles */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h2 className="font-semibold mb-4">Target Roles</h2>
            <div className="space-y-2">
              {roles.map((role, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    value={role}
                    onChange={e => updateRole(i, e.target.value)}
                    placeholder="e.g. Senior Software Engineer"
                    className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  />
                  {roles.length > 1 && (
                    <button onClick={() => removeRole(i)} className="text-gray-500 hover:text-red-400">
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button onClick={addRole} className="mt-2 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
              <Plus className="w-3 h-3" /> Add role
            </button>
          </div>

          {/* Salary */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h2 className="font-semibold mb-4">Minimum Base Salary</h2>
            <div className="flex items-center gap-3">
              <span className="text-gray-400">$</span>
              <input
                type="number"
                value={salaryMin}
                onChange={e => setSalaryMin(parseInt(e.target.value) || 0)}
                className="w-40 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
              <span className="text-gray-400 text-sm">per year</span>
            </div>
          </div>

          {/* Locations */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h2 className="font-semibold mb-4">Locations</h2>
            <div className="space-y-2">
              {locations.map((loc, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    value={loc}
                    onChange={e => updateLocation(i, e.target.value)}
                    placeholder="e.g. Remote, San Francisco, New York"
                    className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  />
                  {locations.length > 1 && (
                    <button onClick={() => removeLocation(i)} className="text-gray-500 hover:text-red-400">
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button onClick={addLocation} className="mt-2 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
              <Plus className="w-3 h-3" /> Add location
            </button>
            <label className="flex items-center gap-2 mt-3 text-sm text-gray-400">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={e => setRemoteOnly(e.target.checked)}
                className="rounded"
              />
              Remote roles only
            </label>
          </div>

          {/* Weekly Quota */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h2 className="font-semibold mb-1">Weekly Application Quota</h2>
            <p className="text-gray-500 text-xs mb-4">Maximum applications to submit per week (1–10). Quality over volume.</p>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min={1}
                max={10}
                value={quota}
                onChange={e => setQuota(parseInt(e.target.value))}
                className="flex-1"
              />
              <span className="text-2xl font-bold w-8 text-center">{quota}</span>
            </div>
          </div>

          {/* Company Blacklist */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h2 className="font-semibold mb-4">Company Blacklist</h2>
            <p className="text-gray-500 text-xs mb-3">Companies you never want to apply to.</p>
            <div className="flex gap-2 mb-3">
              <input
                value={newBlacklistEntry}
                onChange={e => setNewBlacklistEntry(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addBlacklist()}
                placeholder="Company name..."
                className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
              <button onClick={addBlacklist} className="bg-gray-600 hover:bg-gray-500 px-3 py-2 rounded-lg text-sm">
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {blacklist.map((co, i) => (
                <span key={i} className="flex items-center gap-1 bg-red-900/40 border border-red-800 rounded-full px-3 py-1 text-sm text-red-300">
                  {co}
                  <button onClick={() => setBlacklist(blacklist.filter((_, idx) => idx !== i))}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Enable/Disable */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <label className="flex items-center justify-between">
              <div>
                <div className="font-semibold">Enable Autonomous SDR</div>
                <div className="text-gray-500 text-sm">Pipeline runs automatically every Monday morning</div>
              </div>
              <div
                onClick={() => setIsEnabled(!isEnabled)}
                className={`relative w-12 h-6 rounded-full cursor-pointer transition-colors ${isEnabled ? 'bg-blue-600' : 'bg-gray-600'}`}
              >
                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${isEnabled ? 'translate-x-7' : 'translate-x-1'}`} />
              </div>
            </label>
          </div>

          {/* Save */}
          <button
            onClick={save}
            disabled={saving || saved}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 py-3 rounded-xl font-medium transition-colors"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {saved ? 'Saved!' : saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  );
}
