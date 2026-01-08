'use client';

import { Zap, Target, TrendingUp, Briefcase } from 'lucide-react';

const benefits = [
  {
    icon: Zap,
    title: 'Instant Clarity',
    description: 'Know if a career move is right in minutes, not months of guessing.',
  },
  {
    icon: Target,
    title: 'Data-Driven',
    description: 'Decisions backed by real-time market data, not just gut feelings.',
  },
  {
    icon: TrendingUp,
    title: 'Future-Proof',
    description: 'Spot high-growth opportunities and risks before they become obvious.',
  },
  {
    icon: Briefcase,
    title: 'Career Partner',
    description: 'Guidance that evolves with you through every transition.',
  }
];

export default function BenefitsSection() {
  return (
    <section className="py-32 px-4 relative">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Why Top Performers Use NextCI
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Get the unfair advantage in your career journey.
          </p>
        </div>

        {/* Benefits Grid - 4 columns on large screens */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
          {benefits.map((benefit, index) => {
            const Icon = benefit.icon;
            return (
              <div
                key={index}
                className="bg-slate-800/20 backdrop-blur-sm p-8 rounded-2xl border border-white/5 hover:bg-slate-800/40 hover:border-blue-500/30 transition-all duration-300 hover:-translate-y-1 group"
              >
                {/* Icon */}
                <div className="mb-6 inline-flex p-3 rounded-lg bg-blue-500/10 text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-all duration-300">
                  <Icon className="w-8 h-8" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-white mb-3">
                  {benefit.title}
                </h3>
                <p className="text-base text-white/60 leading-relaxed font-medium group-hover:text-white/80 transition-colors">
                  {benefit.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
