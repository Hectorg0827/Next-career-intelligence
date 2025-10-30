'use client';

import ComingSoonPage from '@/components/ComingSoonPage';

export default function JobsPage() {
  const jobsFeature = {
    title: 'AI-Powered Jobs Marketplace',
    subtitle: 'Find roles that match your skills and future-proof your career',
    icon: '💼',
    description: 'Our intelligent jobs marketplace uses AI to match you with opportunities that align with your skills, reduce automation risk, and accelerate your career growth.',
    benefits: [
      'Smart skill matching with compatibility scores',
      'AI risk analysis for every job posting',
      'Personalized job recommendations based on your goals',
      'Distance-based filtering and remote work options',
      'Salary insights and market trends',
      'One-click application tracking and management'
    ],
    launchTimeline: 'Q1 2026'
  };

  return <ComingSoonPage feature={jobsFeature} />;
}
