'use client';

import { Sparkles, Brain, Target, Rocket } from 'lucide-react';

const steps = [
  {
    icon: Sparkles,
    number: '01',
    title: 'Enter Your Job Title',
    description: 'Tell us what you do. Our AI instantly begins analyzing thousands of data points about your role.',
    color: 'text-nci-accent',
    bgGlow: 'bg-nci-accent-dim',
    borderColor: 'border-l-nci-accent',
  },
  {
    icon: Brain,
    number: '02',
    title: 'AI Multi-Agent Analysis',
    description: 'Our specialized AI agents collaborate to assess automation risk, skill gaps, and career opportunities.',
    color: 'text-nci-primary',
    bgGlow: 'bg-nci-primary-dim',
    borderColor: 'border-l-nci-primary',
  },
  {
    icon: Target,
    number: '03',
    title: 'Get Your Personalized Report',
    description: 'Receive actionable insights, skill recommendations, and a tailored roadmap to future-proof your career.',
    color: 'text-nci-amber',
    bgGlow: 'bg-nci-amber-dim',
    borderColor: 'border-l-nci-amber',
  }
];

export default function HowItWorksSection() {
  return (
    <section className="py-24 px-4 relative" id="how-it-works">
      {/* Background Glow */}
      <div className="absolute inset-0 overflow-hidden opacity-30 pointer-events-none">
        <div className="absolute top-1/2 left-1/4 w-96 h-96 rounded-full animate-pulse-slow" style={{ background: 'radial-gradient(circle, rgba(45,127,249,0.15), transparent 70%)', filter: 'blur(80px)' }} />
        <div className="absolute top-1/2 right-1/4 w-96 h-96 rounded-full animate-pulse-slow" style={{ background: 'radial-gradient(circle, rgba(0,210,182,0.12), transparent 70%)', filter: 'blur(80px)' }} />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16 animate-fade-in">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nci-primary-dim border border-nci-primary/20 text-[11px] font-semibold text-nci-primary uppercase tracking-wide font-mono mb-6">
            <Rocket className="w-3.5 h-3.5" />
            Simple Process
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 font-serif">
            How It Works
          </h2>
          <p className="text-lg text-g-400 max-w-2xl mx-auto font-light">
            From job title to career clarity in 60 seconds
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid md:grid-cols-3 gap-4 mb-12 md:items-stretch">
          {steps.map((step, index) => (
            <div
              key={index}
              className="group relative animate-fade-in flex"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              <div className={`relative glass-card border-l-[3px] ${step.borderColor} p-8 transition-all duration-300 hover:-translate-y-1 flex-1`}>
                {/* Step Number */}
                <div className={`absolute top-6 right-6 ${step.bgGlow} w-10 h-10 rounded-lg flex items-center justify-center font-bold font-mono text-sm ${step.color}`}>
                  {step.number}
                </div>

                {/* Icon */}
                <div className={`w-14 h-14 ${step.bgGlow} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <step.icon className={`w-7 h-7 ${step.color}`} strokeWidth={2} />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-nci-primary transition-colors">
                  {step.title}
                </h3>
                <p className="text-g-400 leading-relaxed text-sm">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center animate-fade-in" style={{ animationDelay: '450ms' }}>
          <button
            onClick={() => {
              const form = document.querySelector('form');
              form?.scrollIntoView({ behavior: 'smooth', block: 'center' });
              const input = form?.querySelector('input');
              input?.focus();
            }}
            className="px-8 py-4 bg-white text-nci-bg font-bold rounded-xl transition-all shadow-glass-lg hover:shadow-glass-xl inline-flex items-center gap-2 group"
          >
            <span>Start Your Free Analysis</span>
            <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
          </button>
        </div>
      </div>
    </section>
  );
}
