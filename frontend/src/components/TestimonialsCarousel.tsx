'use client';

import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Star, Quote } from 'lucide-react';

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Data Analyst',
    company: 'Tech Corp',
    image: '👩‍💼',
    rating: 5,
    text: 'NEXT helped me identify Python and ML skills I needed to stay competitive. Within 6 months, I transitioned to a Machine Learning Engineer role with a 40% salary increase!',
    outcome: 'Career Pivot Success'
  },
  {
    name: 'Michael Rodriguez',
    role: 'Marketing Manager',
    company: 'Retail Solutions',
    image: '👨‍💻',
    rating: 5,
    text: 'I was worried about AI replacing marketing roles. The analysis showed me how to pivot into AI-powered marketing strategy. Now I lead a team implementing marketing automation.',
    outcome: 'Future-Proofed Career'
  },
  {
    name: 'Emily Thompson',
    role: 'Accountant',
    company: 'Finance Group',
    image: '👩‍💼',
    rating: 5,
    text: 'The instant career scan revealed automation risks in traditional accounting. I upskilled in financial analytics and data visualization. My value to the company has skyrocketed!',
    outcome: 'Skill Gap Closed'
  },
  {
    name: 'David Park',
    role: 'Customer Service Rep',
    company: 'E-commerce Inc',
    image: '👨‍💼',
    rating: 5,
    text: 'NEXT showed me the high automation risk but also opportunities in customer success strategy. I invested in training and now I manage our customer experience platform.',
    outcome: 'Promoted 2x'
  },
  {
    name: 'Jessica Wu',
    role: 'Graphic Designer',
    company: 'Creative Agency',
    image: '👩‍🎨',
    rating: 5,
    text: 'AI design tools were threatening my career. The roadmap helped me specialize in UX strategy and design systems. I now work on projects AI cannot replicate.',
    outcome: 'Found My Niche'
  }
];

export default function TestimonialsCarousel() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  useEffect(() => {
    if (!isAutoPlaying) return;
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [isAutoPlaying]);

  const goToPrevious = () => {
    setIsAutoPlaying(false);
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const goToNext = () => {
    setIsAutoPlaying(false);
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const goToSlide = (index: number) => {
    setIsAutoPlaying(false);
    setCurrentIndex(index);
  };

  const currentTestimonial = testimonials[currentIndex];

  return (
    <section className="py-24 px-4 relative">
      {/* Background Glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full animate-pulse-slow" style={{ background: 'radial-gradient(circle, rgba(45,127,249,0.1), transparent 70%)', filter: 'blur(100px)' }} />
      </div>

      <div className="max-w-5xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16 animate-fade-in">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nci-accent-dim border border-nci-accent/20 text-[11px] font-semibold text-nci-accent uppercase tracking-wide font-mono mb-6">
            <Star className="w-3.5 h-3.5 fill-nci-accent" />
            Success Stories
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 font-serif">
            Trusted by Professionals
          </h2>
          <p className="text-lg text-g-400 max-w-2xl mx-auto font-light">
            Real people, real career transformations
          </p>
        </div>

        {/* Carousel */}
        <div className="relative">
          {/* Main Card */}
          <div className="glass-card rounded-3xl p-8 md:p-12 relative overflow-hidden group">
            {/* Quote Icon */}
            <div className="absolute top-8 right-8 opacity-[0.06]">
              <Quote className="w-24 h-24 text-nci-primary" />
            </div>

            <div className="relative z-10">
              {/* Rating */}
              <div className="flex gap-1 mb-6">
                {[...Array(currentTestimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-nci-amber fill-nci-amber" />
                ))}
              </div>

              {/* Testimonial Text */}
              <blockquote className="text-xl md:text-2xl text-white font-medium leading-relaxed mb-8">
                &quot;{currentTestimonial.text}&quot;
              </blockquote>

              {/* Author */}
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-gradient-primary flex items-center justify-center text-2xl shadow-glow-blue">
                    {currentTestimonial.image}
                  </div>
                  <div>
                    <div className="text-white font-semibold text-lg">{currentTestimonial.name}</div>
                    <div className="text-g-400 text-sm">{currentTestimonial.role} at {currentTestimonial.company}</div>
                  </div>
                </div>

                {/* Outcome Badge */}
                <div className="px-4 py-2 bg-nci-accent-dim border border-nci-accent/20 rounded-full">
                  <span className="text-nci-accent font-semibold text-sm">✨ {currentTestimonial.outcome}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Arrows */}
          <button
            onClick={goToPrevious}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-16 w-12 h-12 bg-white/[0.06] hover:bg-white/10 backdrop-blur-md border border-nci-border rounded-full items-center justify-center transition-all group hover:scale-110 hidden md:flex"
            aria-label="Previous testimonial"
          >
            <ChevronLeft className="w-6 h-6 text-g-400 group-hover:text-white" />
          </button>

          <button
            onClick={goToNext}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-16 w-12 h-12 bg-white/[0.06] hover:bg-white/10 backdrop-blur-md border border-nci-border rounded-full items-center justify-center transition-all group hover:scale-110 hidden md:flex"
            aria-label="Next testimonial"
          >
            <ChevronRight className="w-6 h-6 text-g-400 group-hover:text-white" />
          </button>

          {/* Mobile Navigation */}
          <div className="flex md:hidden justify-center gap-4 mt-6">
            <button
              onClick={goToPrevious}
              className="w-12 h-12 bg-white/[0.06] hover:bg-white/10 border border-nci-border rounded-full flex items-center justify-center transition-all"
              aria-label="Previous testimonial"
            >
              <ChevronLeft className="w-6 h-6 text-g-400" />
            </button>
            <button
              onClick={goToNext}
              className="w-12 h-12 bg-white/[0.06] hover:bg-white/10 border border-nci-border rounded-full flex items-center justify-center transition-all"
              aria-label="Next testimonial"
            >
              <ChevronRight className="w-6 h-6 text-g-400" />
            </button>
          </div>

          {/* Dots Indicator */}
          <div className="flex justify-center gap-2 mt-8">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentIndex
                    ? 'w-8 bg-nci-primary'
                    : 'w-2 bg-g-600 hover:bg-g-500'
                }`}
                aria-label={`Go to testimonial ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
