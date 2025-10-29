'use client';

import { useEffect, useRef, useState } from 'react';
import { Users, Target, TrendingUp, Award } from 'lucide-react';

interface Stat {
  icon: React.ComponentType<{ className?: string }>;
  value: number;
  suffix: string;
  label: string;
  prefix?: string;
  color: string;
}

const stats: Stat[] = [
  {
    icon: Users,
    value: 15000,
    suffix: '+',
    label: 'Careers Analyzed',
    color: 'text-gold-primary'
  },
  {
    icon: Target,
    value: 89,
    suffix: '%',
    label: 'Found New Opportunities',
    color: 'text-royal-blue-light'
  },
  {
    icon: TrendingUp,
    value: 95,
    suffix: '%',
    label: 'Career Confidence Boost',
    color: 'text-gold-accent'
  },
  {
    icon: Award,
    value: 4.9,
    suffix: '/5',
    label: 'Average Rating',
    color: 'text-gold-primary'
  }
];

function AnimatedNumber({ value, suffix = '', prefix = '' }: { value: number; suffix?: string; prefix?: string }) {
  const [count, setCount] = useState(0);
  const countRef = useRef<HTMLSpanElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    const currentRef = countRef.current;

    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    const duration = 2000; // 2 seconds
    const steps = 60;
    const stepValue = value / steps;
    const stepDuration = duration / steps;

    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const newCount = Math.min(stepValue * currentStep, value);
      setCount(newCount);

      if (currentStep >= steps) {
        clearInterval(timer);
        setCount(value);
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [isVisible, value]);

  // Format number based on value
  const formatNumber = (num: number) => {
    if (value >= 1000) {
      return Math.floor(num).toLocaleString();
    }
    return num.toFixed(1);
  };

  return (
    <span ref={countRef}>
      {prefix}{formatNumber(count)}{suffix}
    </span>
  );
}

export default function StatsSection() {
  return (
    <section className="py-20 px-4 relative">
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 md:p-12">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="text-center group hover:scale-105 transition-transform duration-300"
              >
                {/* Icon */}
                <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-2xl mb-4 group-hover:bg-white/20 transition-all">
                  <stat.icon className={`w-8 h-8 ${stat.color}`} />
                </div>

                {/* Value */}
                <div className={`text-4xl md:text-5xl font-bold ${stat.color} mb-2`}>
                  <AnimatedNumber 
                    value={stat.value} 
                    suffix={stat.suffix}
                    prefix={stat.prefix}
                  />
                </div>

                {/* Label */}
                <div className="text-white/70 text-sm md:text-base font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
