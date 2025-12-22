'use client';

import { useMemo } from 'react';
import { CheckCircle, AlertTriangle, Target, ArrowRight, BrainCircuit, MessageSquareQuote, TrendingUp, Shield, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type {
  AnalysisResult,
  CompatibilityInsight,
  IndustryBenchmarks,
  RiskAssessment,
  Trajectory,
} from '@/types/intelligence';

// A generic card for displaying analysis sections
const InfoCard = ({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) => (
  <div className="premium-card p-6">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-sm font-bold text-premium-text-muted uppercase tracking-widest">{title}</h3>
      <div className="p-2 rounded-lg bg-white/5 text-premium-accent">
        {icon}
      </div>
    </div>
    <div>{children}</div>
  </div>
);
const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const formatLabel = (label: string) =>
  label
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());

const toReadableList = (value: unknown): string[] => {
  if (value === undefined || value === null) {
    return [];
  }

  if (Array.isArray(value)) {
    return value.flatMap((item) => toReadableList(item)).filter(Boolean);
  }

  if (typeof value === 'string') {
    return [value.trim()];
  }

  if (typeof value === 'number') {
    return [value.toString()];
  }

  if (isRecord(value)) {
    const prioritizedKey = ['summary', 'description', 'insight', 'text', 'statement'].find(
      (key) => typeof value[key] === 'string'
    );

    if (prioritizedKey) {
      return [String(value[prioritizedKey]).trim()];
    }

    return Object.entries(value)
      .flatMap(([key, nested]) => {
        const nestedValues = toReadableList(nested).slice(0, 3);
        if (!nestedValues.length) {
          return [];
        }
        return [`${formatLabel(key)}: ${nestedValues.join(', ')}`];
      })
      .filter(Boolean);
  }

  return [];
};

export const RiskCard = ({ risk }: { risk?: RiskAssessment | AnalysisResult['risk'] }) => {
  const getRiskColor = (level: string) => {
    const lowerLevel = level.toLowerCase();
    if (lowerLevel.includes('low') || lowerLevel.includes('safe')) return 'text-emerald-400';
    if (lowerLevel.includes('medium') || lowerLevel.includes('moderate')) return 'text-amber-400';
    return 'text-rose-400';
  };

  const getRiskIcon = (level: string) => {
    const lowerLevel = level.toLowerCase();
    if (lowerLevel.includes('low') || lowerLevel.includes('safe')) {
      return <Shield className="h-5 w-5 text-emerald-400" />;
    }
    return <AlertTriangle className="h-5 w-5 text-amber-400" />;
  };

  return (
    <InfoCard title="AI Displacement Risk" icon={getRiskIcon(risk?.level || 'Unknown')}>
      <div className={`text-3xl font-serif italic ${getRiskColor(risk?.level || 'Unknown')}`}>
        {risk?.level || 'Unknown'}
      </div>
      <p className="text-sm text-premium-text-muted mt-4 leading-relaxed">{risk?.justification || risk?.reasoning || 'No detailed analysis available.'}</p>
      {typeof risk?.score === 'number' && (
        <div className="mt-6">
          <div className="flex justify-between text-xs mb-2">
            <span className="text-premium-text-muted">Risk Probability</span>
            <span className="text-white font-bold">{Math.round(risk.score)}%</span>
          </div>
          <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-1000 ${
                risk.score < 30 ? 'bg-emerald-400' : risk.score < 70 ? 'bg-amber-400' : 'bg-rose-400'
              }`}
              style={{ width: `${risk.score}%` }}
            />
          </div>
        </div>
      )}
    </InfoCard>
  );
};

export const CompatibilityCard = ({
  compatibility,
  fallbackScore = 0,
  fallbackHighlights = [],
}: {
  compatibility?: CompatibilityInsight;
  fallbackScore?: number;
  fallbackHighlights?: string[];
}) => {
  const score = useMemo(() => {
    const rawScore = compatibility?.score ?? fallbackScore ?? 0;
    return Math.max(0, Math.min(100, Math.round(rawScore)));
  }, [compatibility?.score, fallbackScore]);

  const highlights = useMemo(() => {
    const merged = [...(compatibility?.highlights ?? []), ...(fallbackHighlights ?? [])];
    return Array.from(new Set(merged.filter(Boolean))).slice(0, 5);
  }, [compatibility?.highlights, fallbackHighlights]);

  return (
    <InfoCard title="Compatibility Score" icon={<Target className="h-5 w-5" />}>
      <div className="text-3xl font-serif italic text-premium-accent">{score}%</div>
      {highlights.length > 0 && (
        <ul className="text-sm text-premium-text-muted mt-4 space-y-2">
          {highlights.map((item, i) => (
            <li key={i} className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-premium-accent shrink-0 mt-0.5" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
      <div className="mt-6">
        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
          <div
            className="bg-premium-accent h-full transition-all duration-1000"
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    </InfoCard>
  );
};

export const SkillGapsCard = ({ gaps }: { gaps: string[] }) => (
  <InfoCard title="Skill Gaps to Address" icon={<BrainCircuit className="h-5 w-5 text-premium-accent" />}>
    {gaps && gaps.length > 0 ? (
      <ul className="text-sm text-premium-text-muted mt-4 space-y-3">
        {gaps.map((gap, i) => (
          <li key={i} className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-premium-accent mt-1.5 shrink-0" />
            <span>{gap}</span>
          </li>
        ))}
      </ul>
    ) : (
      <p className="text-sm text-premium-accent mt-4 flex items-center gap-2">
        <CheckCircle className="w-4 h-4" />
        No significant skill gaps detected!
      </p>
    )}
  </InfoCard>
);

export const NextStepsCard = ({ steps }: { steps: string[] }) => (
  <InfoCard title="Your Next Steps" icon={<ArrowRight className="h-5 w-5 text-premium-accent" />}>
    {steps && steps.length > 0 ? (
      <ol className="text-sm text-premium-text-muted mt-4 space-y-4">
        {steps.map((step, i) => (
          <li key={i} className="flex gap-3">
            <span className="font-serif italic text-premium-accent shrink-0">{i + 1}.</span>
            <span>{step}</span>
          </li>
        ))}
      </ol>
    ) : (
      <p className="text-sm text-premium-text-muted mt-4 italic">Keep engaging with your AI coach for personalized guidance.</p>
    )}
  </InfoCard>
);

export const CoachQuestionsCard = ({ questions }: { questions: string[] }) => (
  <InfoCard title="For Your Next Coach Session" icon={<MessageSquareQuote className="h-5 w-5 text-premium-accent" />}>
    <p className="text-xs text-premium-text-muted/60 mb-4 italic">Your AI Coach will ask these to refine your profile:</p>
    {questions && questions.length > 0 ? (
      <ul className="text-sm text-premium-text-muted space-y-3">
        {questions.map((q, i) => (
          <li key={i} className="flex items-start gap-2">
            <div className="w-1 h-1 rounded-full bg-premium-accent mt-2 shrink-0" />
            <span>{q}</span>
          </li>
        ))}
      </ul>
    ) : (
      <p className="text-sm text-premium-text-muted italic">No questions at this time.</p>
    )}
  </InfoCard>
);

export const HumanAdvantageCard = ({ factors }: { factors: string[] }) => (
  <InfoCard title="Human Advantage Factors" icon={<CheckCircle className="h-5 w-5 text-premium-accent" />}>
    {factors && factors.length > 0 ? (
      <ul className="text-sm text-premium-text-muted mt-4 space-y-3">
        {factors.map((factor, i) => (
          <li key={i} className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-premium-accent shrink-0 mt-0.5" />
            <span>{factor}</span>
          </li>
        ))}
      </ul>
    ) : (
      <p className="text-sm text-premium-text-muted mt-4 italic">No unique human advantages identified yet.</p>
    )}
  </InfoCard>
);

export const BenchmarksCard = ({ benchmarks }: { benchmarks?: IndustryBenchmarks }) => {
  const entries = useMemo(() => {
    if (!benchmarks) {
      return [];
    }

    if (!benchmarks.benchmarks || !isRecord(benchmarks.benchmarks)) {
      return [];
    }

    return Object.entries(benchmarks.benchmarks)
      .flatMap(([key, value]) => {
        const metrics = toReadableList(value).slice(0, 3);
        if (!metrics.length) {
          return [];
        }
        return [`${formatLabel(key)}: ${metrics.join(', ')}`];
      })
      .filter(Boolean)
      .slice(0, 6);
  }, [benchmarks]);

  return (
    <InfoCard title="Industry Benchmarks" icon={<BarChart3 className="h-5 w-5 text-premium-accent" />}>
      {benchmarks?.industry && (
        <div className="text-sm text-premium-text-muted mt-4 mb-4">
          Industry: <span className="font-serif italic text-premium-accent">{benchmarks.industry}</span>
          {benchmarks.region ? (
            <>
              <span className="mx-2 opacity-30">|</span>
              Region: <span className="font-serif italic text-premium-accent">{benchmarks.region}</span>
            </>
          ) : ''}
        </div>
      )}
      {entries.length > 0 ? (
        <ul className="text-sm text-premium-text-muted space-y-3">
          {entries.map((entry, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <div className="w-1 h-1 rounded-full bg-premium-accent mt-2 shrink-0" />
              <span>{entry}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-premium-text-muted mt-2 italic">Benchmarks are still loading for this role.</p>
      )}
      {benchmarks?.source && (
        <p className="text-[10px] text-premium-text-muted/40 mt-6 uppercase tracking-widest">Source: {benchmarks.source}</p>
      )}
    </InfoCard>
  );
};

export const TrajectoryCard = ({ paths = [] }: { paths?: Trajectory }) => (
  <InfoCard title="Career Trajectory Forecast" icon={<TrendingUp className="h-5 w-5 text-premium-accent" />}>
    {paths && paths.length > 0 ? (
      <div className="space-y-6 mt-4">
        {paths.slice(0, 3).map((path, i) => (
          <div key={i} className="relative pl-6 border-l border-white/10">
            <div className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-premium-accent to-transparent" />
            <div className="text-sm font-serif italic text-white mb-1">
              {path.title || path.target_role || path.role || 'Future role'}
            </div>
            <div className="text-xs text-premium-text-muted flex items-center gap-3">
              <span className="flex items-center gap-1">
                <Target className="w-3 h-3 text-premium-accent" />
                {typeof path.probability === 'number'
                  ? `${Math.round(path.probability)}%`
                  : typeof path.probability === 'string'
                  ? path.probability
                  : 'Unknown'}
              </span>
              <span className="w-1 h-1 rounded-full bg-white/20" />
              <span>{path.timeline || 'TBD'}</span>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p className="text-sm text-premium-text-muted mt-4 italic">Complete your profile for trajectory predictions.</p>
    )}
  </InfoCard>
);
