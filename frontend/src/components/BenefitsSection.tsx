'use client';

const benefits = [
  {
    emoji: '⚡',
    title: 'Instant Clarity',
    description: 'Know if a career move is right in minutes, not months of guessing.',
  },
  {
    emoji: '🎯',
    title: 'Data-Driven',
    description: 'Decisions backed by market data, not just gut feelings.',
  },
  {
    emoji: '🚀',
    title: 'Future-Proof',
    description: 'Spot opportunities and risks before they\'re obvious.',
  },
  {
    emoji: '💼',
    title: 'Career Partner',
    description: 'Guidance that evolves with you through every transition.',
  }
];

export default function BenefitsSection() {
  return (
    <section className="py-20 px-4 bg-slate-900/30">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Why Top Performers Use NextCI
          </h2>
        </div>

        {/* Benefits Grid - 2x2 */}
        <div className="grid sm:grid-cols-2 gap-6 md:gap-8">
          {benefits.map((benefit, index) => (
            <div
              key={index}
              className="bg-slate-800/50 p-6 sm:p-8 rounded-xl hover:bg-slate-800/70 transition-all duration-300 hover:-translate-y-1 shadow-lg hover:shadow-xl"
            >
              {/* Icon */}
              <div className="text-4xl sm:text-5xl mb-3 sm:mb-4">{benefit.emoji}</div>

              {/* Content */}
              <h3 className="text-xl sm:text-2xl font-semibold text-white mb-2 sm:mb-3">
                {benefit.title}
              </h3>
              <p className="text-sm sm:text-base text-white/70 leading-relaxed">
                {benefit.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
