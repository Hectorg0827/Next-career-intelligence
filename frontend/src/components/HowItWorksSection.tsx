'use client';

import { Sparkles, Brain, Target, Rocket } from 'lucide-react';

const steps = [
  {
    icon: Sparkles,
    number: '01',
    title: 'Enter Your Job Title',
    description: 'Tell us what you do. Our AI instantly begins analyzing thousands of data points about your role.',
    color: 'from-gold-primary to-gold-accent',
    bgGlow: 'bg-gold-primary/20'
  },
  {
    icon: Brain,
    number: '02',
    title: 'AI Multi-Agent Analysis',
    description: 'Our specialized AI agents collaborate to assess automation risk, skill gaps, and career opportunities.',
    color: 'from-royal-blue to-royal-blue-light',
    bgGlow: 'bg-royal-blue/20'
  },
  {
    icon: Target,
    number: '03',
    title: 'Get Your Personalized Report',
    description: 'Receive actionable insights, skill recommendations, and a tailored roadmap to future-proof your career.',
    color: 'from-gold-accent to-gold-hover',
    bgGlow: 'bg-gold-accent/20'
  }
];

export default function HowItWorksSection() {
  return (
    <section className="py-24 px-4 relative" id="how-it-works">
      {/* Background Glow */}
      <div className="absolute inset-0 overflow-hidden opacity-10">
        <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-gold-primary rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-royal-blue rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-gold-primary/30 rounded-full mb-6">
            <Rocket className="w-4 h-4 text-gold-primary" />
            <span className="text-white/90 text-sm font-medium">Simple Process</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            How It Works
          </h2>
          <p className="text-xl text-white/70 max-w-2xl mx-auto">
            From job title to career clarity in 60 seconds
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {steps.map((step, index) => (
            <div
              key={index}
              className="group relative animate-fade-in"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              {/* Connection Line (desktop only) */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-20 left-[calc(50%+2rem)] w-[calc(100%-2rem)] h-0.5 bg-gradient-to-r from-gold-primary/50 to-transparent z-0" />
              )}

              {/* Card */}
              <div className="relative bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 hover:border-gold-primary/50 transition-all duration-300 hover:shadow-gold hover:-translate-y-2 h-full">
                {/* Step Number */}
                <div className={`absolute -top-4 -right-4 w-12 h-12 bg-gradient-to-br ${step.color} rounded-full flex items-center justify-center font-bold text-royal-navy text-lg shadow-lg`}>
                  {step.number}
                </div>

                {/* Icon */}
                <div className={`w-16 h-16 ${step.bgGlow} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <step.icon className={`w-8 h-8 bg-gradient-to-br ${step.color} bg-clip-text text-transparent`} strokeWidth={2.5} />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-gold-primary transition-colors">
                  {step.title}
                </h3>
                <p className="text-white/70 leading-relaxed">
                  {step.description}
                </p>

                {/* Hover Glow Effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-gold-primary/0 to-gold-primary/0 group-hover:from-gold-primary/10 group-hover:to-transparent transition-all duration-300 pointer-events-none" />
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
            className="px-8 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-2 group"
          >
            <span>Start Your Free Analysis</span>
            <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
          </button>
        </div>
      </div>
    </section>
  );
}
