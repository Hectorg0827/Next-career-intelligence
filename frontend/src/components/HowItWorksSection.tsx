'use client';

import { Sparkles, Brain, Target, Rocket } from 'lucide-react';

const steps = [
  {
    emoji: '📝',
    number: '1',
    title: 'Share Your Goals',
    description: 'Type your career question or upload your resume. Takes 30 seconds.',
  },
  {
    emoji: '🤖',
    number: '2',
    title: 'AI Analysis',
    description: 'Our AI evaluates opportunities, risks, and market trends specific to you.',
  },
  {
    emoji: '📊',
    number: '3',
    title: 'Get Your Plan',
    description: 'Receive actionable insights and next steps tailored to your situation.',
  }
];

export default function HowItWorksSection() {
  return (
    <section className="py-24 px-4 relative bg-white/5" id="how-it-works">
      <div className="max-w-6xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            How It Works
          </h2>
        </div>

        {/* Steps Grid - Clean 3 columns */}
        <div className="grid md:grid-cols-3 gap-12">
          {steps.map((step, index) => (
            <div
              key={index}
              className="text-center max-w-[280px] mx-auto"
            >
              {/* Emoji Icon */}
              <div className="w-20 h-20 mx-auto mb-6 text-6xl flex items-center justify-center bg-gradient-to-br from-blue-600/20 to-blue-700/20 rounded-full">
                {step.emoji}
              </div>

              {/* Content */}
              <h3 className="text-xl font-semibold text-white mb-3">
                {step.number}. {step.title}
              </h3>
              <p className="text-white/70 leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
