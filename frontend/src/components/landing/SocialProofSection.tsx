import React from 'react';
import { Star, TrendingUp, Users, CheckCircle } from 'lucide-react';

export const SocialProofSection = () => {
  const metrics = [
    {
      value: '47%',
      label: 'Improve within 60 days',
      icon: TrendingUp
    },
    {
      value: '500K+',
      label: 'AI-proof career paths identified',
      icon: Users
    },
    {
      value: '4.9★',
      label: 'From 12,000+ professionals',
      icon: Star
    }
  ];

  const testimonials = [
    {
      text: 'Next identified that my marketing skills were at risk. I pivoted to growth strategy within 6 months and my salary increased by 30%.',
      author: 'Sarah Chen',
      role: 'Marketing Director',
      company: 'Tech Startup',
      avatar: '👩‍💼'
    },
    {
      text: 'The AI coaching sessions prepared me for interviews I didn\'t even know to apply for. I landed a role with 40% higher comp.',
      author: 'James Rodriguez',
      role: 'Software Engineer',
      company: 'Fortune 500',
      avatar: '👨‍💻'
    },
    {
      text: 'This platform revealed opportunities in AI/ML that aligned perfectly with my background. Game-changer for career planning.',
      author: 'Priya Patel',
      role: 'Data Analyst',
      company: 'Tech Scale-up',
      avatar: '👩‍🔬'
    }
  ];

  const companies = [
    { name: 'Google', initials: 'G' },
    { name: 'Amazon', initials: 'A' },
    { name: 'Microsoft', initials: 'MS' },
    { name: 'Apple', initials: 'APPL' },
    { name: 'Meta', initials: 'M' },
    { name: 'Tesla', initials: 'T' }
  ];

  return (
    <section className="py-20 bg-gradient-to-b from-next-deep-blue via-next-dark-bg to-next-deep-blue">
      <div className="container mx-auto px-4 max-w-6xl">
        
        {/* Metrics */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          {metrics.map((metric, i) => {
            const Icon = metric.icon;
            return (
              <div 
                key={i}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 hover:border-next-gold/30 transition-all group hover:shadow-next-lg"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl font-bold bg-gradient-next-gold bg-clip-text text-transparent group-hover:scale-110 transition-transform origin-left">
                    {metric.value}
                  </div>
                  <Icon className="w-6 h-6 text-next-gold group-hover:scale-125 transition-transform" />
                </div>
                <p className="text-white/70 text-sm">{metric.label}</p>
              </div>
            );
          })}
        </div>

        {/* Testimonials */}
        <div className="mb-20">
          <h3 className="text-3xl font-heading font-bold text-white text-center mb-12">
            Trusted by 12,000+ Professionals
          </h3>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, i) => (
              <div 
                key={i}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-next-gold/30 transition-all hover:shadow-next-lg"
              >
                {/* Stars */}
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, j) => (
                    <Star 
                      key={j}
                      className="w-4 h-4 fill-next-gold text-next-gold"
                    />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-white/90 mb-6 italic leading-relaxed">
                  &quot;{testimonial.text}&quot;
                </p>

                {/* Author */}
                <div className="flex items-center gap-3 pt-4 border-t border-white/10">
                  <div className="text-3xl">{testimonial.avatar}</div>
                  <div>
                    <p className="text-white font-semibold text-sm">{testimonial.author}</p>
                    <p className="text-white/60 text-xs">
                      {testimonial.role} @ {testimonial.company}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Company logos / users */}
        <div className="text-center">
          <p className="text-white/60 text-sm font-body mb-6">
            Used by professionals at leading companies
          </p>

          <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
            {companies.map((company, i) => (
              <div
                key={i}
                className="bg-white/5 hover:bg-white/10 border border-white/10 hover:border-next-gold/30 rounded-lg h-16 flex items-center justify-center transition-all group cursor-pointer"
              >
                <span className="text-white/60 group-hover:text-next-gold font-semibold text-xs transition-colors">
                  {company.initials}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Trust badges */}
        <div className="mt-16 grid md:grid-cols-2 gap-6">
          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0" />
            <span className="text-white/80 text-sm">SOC 2 Type II Certified</span>
          </div>
          
          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0" />
            <span className="text-white/80 text-sm">GDPR Compliant & Data Encrypted</span>
          </div>

          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0" />
            <span className="text-white/80 text-sm">10+ Years Combined AI Expertise</span>
          </div>

          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
            <CheckCircle className="w-5 h-5 text-next-gold flex-shrink-0" />
            <span className="text-white/80 text-sm">24/7 Customer Support</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SocialProofSection;
