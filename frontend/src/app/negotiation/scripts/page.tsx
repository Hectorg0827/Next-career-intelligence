'use client';

import { useEffect, useState } from 'react';
import { ArrowLeft, Copy, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Script {
  scenario: string;
  context: string;
  script: string;
  notes: string;
}

export default function NegotiationScriptsPage() {
  const router = useRouter();
  const [scripts, setScripts] = useState<Script[]>([]);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/negotiation/scripts`)
      .then(r => r.json())
      .then(d => setScripts(d.scripts || []));
  }, []);

  const copyScript = (script: string, scenario: string) => {
    navigator.clipboard.writeText(script);
    setCopied(scenario);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h1 className="text-2xl font-bold mb-2">Negotiation Script Library</h1>
        <p className="text-gray-400 text-sm mb-8">Word-for-word scripts for common negotiation scenarios. Adapt to your situation.</p>

        <div className="space-y-4">
          {scripts.map((script, i) => (
            <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-5">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold">{script.scenario}</h3>
                  <p className="text-gray-500 text-sm mt-0.5">{script.context}</p>
                </div>
                <button
                  onClick={() => copyScript(script.script, script.scenario)}
                  className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white bg-gray-700 hover:bg-gray-600 px-2.5 py-1.5 rounded-lg transition-colors ml-4 shrink-0"
                >
                  {copied === script.scenario ? (
                    <><CheckCircle className="w-3 h-3 text-green-400" /> Copied</>
                  ) : (
                    <><Copy className="w-3 h-3" /> Copy</>
                  )}
                </button>
              </div>

              <div className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 border border-gray-700 my-3 italic">
                "{script.script}"
              </div>

              <div className="text-xs text-blue-400">
                💡 {script.notes}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
