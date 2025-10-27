'use client';

import { CheckCircle, AlertTriangle, Target, ArrowRight, BrainCircuit, MessageSquareQuote, TrendingUp, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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

export const RiskCard = ({ risk }: { risk: any }) => {
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
      {risk?.score !== undefined && (
        <div className="mt-2 text-sm text-gray-300">
          Risk Score: <span className="font-semibold">{risk.score}%</span>
        </div>
      )}
    </InfoCard>
  );
};

export const CompatibilityCard = ({ score, highlights }: { score: number; highlights: string[] }) => (
  <InfoCard title="Compatibility Score" icon={<Target className="h-5 w-5 text-blue-400" />}>
    <div className="text-2xl font-bold text-gold-500">{score}/100</div>
    {highlights && highlights.length > 0 && (
      <ul className="text-xs text-gray-400 mt-2 list-disc pl-4 space-y-1">
        {highlights.slice(0, 3).map((item, i) => <li key={i}>{item}</li>)}
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

export const TrajectoryCard = ({ paths }: { paths: any[] }) => (
  <InfoCard title="Career Trajectory Forecast" icon={<TrendingUp className="h-5 w-5 text-emerald-400" />}>
    {paths && paths.length > 0 ? (
      <div className="space-y-3">
        {paths.slice(0, 3).map((path, i) => (
          <div key={i} className="border-l-2 border-gold-500 pl-3">
            <div className="text-sm font-semibold text-white">{path.title || path.role}</div>
            <div className="text-xs text-gray-400">
              Probability: {path.probability}% • Timeline: {path.timeline || 'TBD'}
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p className="text-sm text-gray-400">Complete your profile for trajectory predictions.</p>
    )}
  </InfoCard>
);
