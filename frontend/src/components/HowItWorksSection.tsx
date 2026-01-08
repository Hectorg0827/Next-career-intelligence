'use client';

import { FileText, Brain, LayoutDashboard } from 'lucide-react';

const steps = [
  {
    icon: FileText,
    number: '1',
    title: 'Share Your Goals',
    description: 'Type your career question or upload your resume. Takes 30 seconds.',
  },
  {
    icon: Brain,
    number: '2',
    title: 'AI Analysis',
    description: 'Our AI evaluates opportunities, risks, and market trends specific to you.',
  },
  {
    icon: LayoutDashboard,
    number: '3',
    title: 'Get Your Plan',
    description: 'Receive actionable insights and next steps tailored to your situation.',
  }
];

export default function HowItWorksSection() {
  return (
    <section className="py-32 px-4 relative bg-slate-900/20" id="how-it-works">
      <div className="max-w-6xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            How It Works
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            From confusion to clarity in three simple steps.
          </p>
        </div>

        {/* Steps Grid - Clean 3 columns */}
        <div className="grid md:grid-cols-3 gap-12 md:gap-16">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div
                key={index}
                className="text-center max-w-[320px] mx-auto group"
              >
                {/* Icon */}
                <div className="w-20 h-20 mx-auto mb-8 flex items-center justify-center bg-slate-800 rounded-2xl shadow-lg border border-slate-700/50 group-hover:border-blue-500/50 group-hover:scale-110 transition-all duration-300">
                  <Icon className="w-10 h-10 text-blue-400 group-hover:text-blue-300 transition-colors" />
                </div>

                {/* Content */}
                <div className="relative">
                  <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-6xl font-bold text-slate-800/50 -z-10 select-none">
                    {step.number}
                  </span>
                  <h3 className="text-xl font-bold text-white mb-4 group-hover:text-blue-400 transition-colors">
                    {step.title}
                  </h3>
                  <p className="text-base text-white/70 leading-relaxed font-medium">
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
