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
  <Card className="bg-gray-800 border-gray-700 text-white">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      {icon}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
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
    if (lowerLevel.includes('low') || lowerLevel.includes('safe')) return 'text-green-500';
    if (lowerLevel.includes('medium') || lowerLevel.includes('moderate')) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getRiskIcon = (level: string) => {
    const lowerLevel = level.toLowerCase();
    if (lowerLevel.includes('low') || lowerLevel.includes('safe')) {
      return <Shield className="h-5 w-5 text-green-500" />;
    }
    return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
  };

  return (
    <InfoCard title="AI Displacement Risk" icon={getRiskIcon(risk?.level || 'Unknown')}>
      <div className={`text-2xl font-bold ${getRiskColor(risk?.level || 'Unknown')}`}>
        {risk?.level || 'Unknown'}
      </div>
      <p className="text-xs text-gray-400 mt-2">{risk?.justification || risk?.reasoning || 'No detailed analysis available.'}</p>
      {typeof risk?.score === 'number' && (
        <div className="mt-2 text-sm text-gray-300">
          Risk Score: <span className="font-semibold">{Math.round(risk.score)}%</span>
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
    <InfoCard title="Compatibility Score" icon={<Target className="h-5 w-5 text-blue-400" />}>
      <div className="text-2xl font-bold text-gold-500">{score}/100</div>
      {highlights.length > 0 && (
        <ul className="text-xs text-gray-400 mt-2 list-disc pl-4 space-y-1">
          {highlights.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      )}
      <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
        <div
          className="bg-gold-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </InfoCard>
  );
};

export const SkillGapsCard = ({ gaps }: { gaps: string[] }) => (
  <InfoCard title="Skill Gaps to Address" icon={<BrainCircuit className="h-5 w-5 text-purple-400" />}>
    {gaps && gaps.length > 0 ? (
      <ul className="text-sm text-gray-300 mt-1 list-disc pl-4 space-y-1">
        {gaps.map((gap, i) => <li key={i}>{gap}</li>)}
      </ul>
    ) : (
      <p className="text-sm text-green-500">✓ No significant skill gaps detected!</p>
    )}
  </InfoCard>
);

export const NextStepsCard = ({ steps }: { steps: string[] }) => (
  <InfoCard title="Your Next Steps" icon={<ArrowRight className="h-5 w-5 text-blue-400" />}>
    {steps && steps.length > 0 ? (
      <ol className="text-sm text-gray-300 mt-1 list-decimal pl-4 space-y-2">
        {steps.map((step, i) => <li key={i}>{step}</li>)}
      </ol>
    ) : (
      <p className="text-sm text-gray-400">Keep engaging with your AI coach for personalized guidance.</p>
    )}
  </InfoCard>
);

export const CoachQuestionsCard = ({ questions }: { questions: string[] }) => (
  <InfoCard title="For Your Next Coach Session" icon={<MessageSquareQuote className="h-5 w-5 text-indigo-400" />}>
    <p className="text-xs text-gray-400 mb-2">Your AI Coach will ask these to refine your profile:</p>
    {questions && questions.length > 0 ? (
      <ul className="text-sm text-gray-300 mt-1 list-disc pl-4 space-y-1">
        {questions.map((q, i) => <li key={i}>{q}</li>)}
      </ul>
    ) : (
      <p className="text-sm text-gray-400">No questions at this time.</p>
    )}
  </InfoCard>
);

export const HumanAdvantageCard = ({ factors }: { factors: string[] }) => (
  <InfoCard title="Human Advantage Factors" icon={<CheckCircle className="h-5 w-5 text-emerald-400" />}>
    {factors && factors.length > 0 ? (
      <ul className="text-sm text-gray-300 mt-1 list-disc pl-4 space-y-1">
        {factors.map((factor, i) => (
          <li key={i}>{factor}</li>
        ))}
      </ul>
    ) : (
      <p className="text-sm text-gray-400">No unique human advantages identified yet.</p>
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
    <InfoCard title="Industry Benchmarks" icon={<BarChart3 className="h-5 w-5 text-gold-400" />}>
      {benchmarks?.industry && (
        <p className="text-sm text-gray-300">
          Industry: <span className="font-semibold text-white">{benchmarks.industry}</span>
          {benchmarks.region ? ` • Region: ${benchmarks.region}` : ''}
        </p>
      )}
      {entries.length > 0 ? (
        <ul className="text-xs text-gray-400 mt-3 list-disc pl-4 space-y-1">
          {entries.map((entry, idx) => (
            <li key={idx}>{entry}</li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-gray-400 mt-2">Benchmarks are still loading for this role.</p>
      )}
      {benchmarks?.source && (
        <p className="text-[10px] text-gray-500 mt-3">Source: {benchmarks.source}</p>
      )}
    </InfoCard>
  );
};

export const TrajectoryCard = ({ paths = [] }: { paths?: Trajectory }) => (
  <InfoCard title="Career Trajectory Forecast" icon={<TrendingUp className="h-5 w-5 text-emerald-400" />}>
    {paths && paths.length > 0 ? (
      <div className="space-y-3">
        {paths.slice(0, 3).map((path, i) => (
          <div key={i} className="border-l-2 border-gold-500 pl-3">
            <div className="text-sm font-semibold text-white">{path.title || path.target_role || path.role || 'Future role'}</div>
            <div className="text-xs text-gray-400">
              Probability:{' '}
              {typeof path.probability === 'number'
                ? `${Math.round(path.probability)}%`
                : typeof path.probability === 'string'
                ? path.probability
                : 'Unknown'}{' '}
              • Timeline: {path.timeline || 'TBD'}
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p className="text-sm text-gray-400">Complete your profile for trajectory predictions.</p>
    )}
  </InfoCard>
);
