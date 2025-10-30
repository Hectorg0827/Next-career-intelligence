'use client';

import ComingSoonPage from '@/components/ComingSoonPage';

export default function InterviewerPage() {
  const interviewerFeature = {
    title: 'AI Interview Practice',
    subtitle: 'Master the STAR method with personalized AI coaching',
    icon: '🎤',
    description: 'Practice behavioral interviews with our AI interviewer, get real-time feedback on your STAR responses, and build confidence before your next big opportunity.',
    benefits: [
      'STAR method coaching with instant feedback',
      'Personalized questions based on your target role',
      'Voice or text-based practice sessions',
      'Achievement extraction from your experiences',
      'Compelling resume bullet generation',
      'Progress tracking and improvement analytics'
    ],
    launchTimeline: 'Q1 2026'
  };

  return <ComingSoonPage feature={interviewerFeature} />;
}
