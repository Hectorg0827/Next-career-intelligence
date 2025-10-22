'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Menu, X } from 'lucide-react';
import { NextLogo } from '@/components/branding/NextLogo';
import { EnhancedHeroSection } from '@/components/landing/EnhancedHeroSection';
import { CareerRiskScanModal } from '@/components/landing/CareerRiskScanModal';
import { SocialProofSection } from '@/components/landing/SocialProofSection';

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <main className="min-h-screen bg-next-deep-blue">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-next-deep-blue/95 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-4 py-4 relative">
          <nav className="flex justify-between items-center">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <NextLogo variant="text" size="md" animated />
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex gap-8 items-center">
              <a 
                href="#how-it-works" 
                className="text-white/80 hover:text-white font-body transition-colors text-sm"
              >
                How It Works
              </a>
              <a 
                href="#pricing" 
                className="text-white/80 hover:text-white font-body transition-colors text-sm"
              >
                Pricing
              </a>
              <a 
                href="#features" 
                className="text-white/80 hover:text-white font-body transition-colors text-sm"
              >
                Features
              </a>
              <Link 
                href="/dashboard" 
                className="px-6 py-2 bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-semibold rounded-lg transition-all shadow-next-gold hover:shadow-next-xl"
              >
                Sign In
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-white"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </nav>

          {/* Mobile Nav */}
          {isMenuOpen && (
            <div className="md:hidden absolute top-full left-0 right-0 bg-next-deep-blue border-b border-white/10 p-4 space-y-4">
              <a 
                href="#how-it-works" 
                className="block text-white/80 hover:text-white font-body transition-colors"
              >
                How It Works
              </a>
              <a 
                href="#pricing" 
                className="block text-white/80 hover:text-white font-body transition-colors"
              >
                Pricing
              </a>
              <a 
                href="#features" 
                className="block text-white/80 hover:text-white font-body transition-colors"
              >
                Features
              </a>
              <Link 
                href="/dashboard" 
                className="block px-6 py-2 bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-semibold rounded-lg transition-all text-center"
              >
                Sign In
              </Link>
            </div>
          )}
        </div>
      </header>

      {/* Enhanced Hero Section */}
      <EnhancedHeroSection />

      {/* CTA to open modal */}
      <section className="py-12 text-center border-t border-white/10">
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 px-8 py-3 bg-white/10 hover:bg-white/20 text-white border border-white/30 rounded-lg transition-all hover:shadow-next-md"
        >
          Open Career Scan
          <ArrowRight className="w-4 h-4" />
        </button>
      </section>

      {/* Social Proof Section */}
      <SocialProofSection />

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 border-t border-white/10">
        <div className="container mx-auto px-4 max-w-6xl">
          <h2 className="text-4xl font-heading font-bold text-center text-white mb-16">
            Your AI-Powered Career Journey
          </h2>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              {
                step: '1',
                title: 'Take Your Scan',
                description: 'Get a free AI analysis of your career risk in 2 minutes'
              },
              {
                step: '2',
                title: 'Get Insights',
                description: 'Discover strengths, gaps, and emerging job opportunities'
              },
              {
                step: '3',
                title: 'Build Your Path',
                description: 'Receive a personalized roadmap with learning resources'
              },
              {
                step: '4',
                title: 'Level Up',
                description: 'Chat with AI coach and track your career progress'
              }
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 h-full hover:border-next-gold/30 transition-all">
                  <div className="text-4xl font-bold text-next-gold mb-4">{item.step}</div>
                  <h3 className="text-xl font-heading font-bold text-white mb-3">{item.title}</h3>
                  <p className="text-white/60">{item.description}</p>
                </div>
                
                {i < 3 && (
                  <div className="hidden md:flex absolute -right-4 top-1/2 -translate-y-1/2 text-next-gold">
                    <ArrowRight className="w-6 h-6" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 border-t border-white/10 bg-white/5">
        <div className="container mx-auto px-4 max-w-6xl">
          <h2 className="text-4xl font-heading font-bold text-center text-white mb-16">
            Everything You Need to Thrive
          </h2>

          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                title: 'AI Career Coach',
                description: 'Chat with your personal AI mentor powered by GPT-4. Ask questions, get advice, practice interviews.'
              },
              {
                title: 'Real-Time Market Intelligence',
                description: 'See which skills are gaining demand, which roles are growing, and what companies are hiring.'
              },
              {
                title: 'Personalized Job Matching',
                description: 'Get curated job recommendations based on your skills, experience, and career goals.'
              },
              {
                title: 'Skill Gap Analysis',
                description: 'Know exactly what to learn to land your next role. We map the path and recommend resources.'
              },
              {
                title: 'Learning Roadmap',
                description: 'Custom learning paths with vetted courses, books, and practice projects to close gaps fast.'
              },
              {
                title: 'Achievement Tracking',
                description: 'Track your progress, celebrate milestones, and stay motivated on your journey.'
              }
            ].map((feature, i) => (
              <div key={i} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 hover:border-next-gold/30 transition-all hover:shadow-next-lg">
                <h3 className="text-xl font-heading font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-white/70">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 border-t border-white/10">
        <div className="container mx-auto px-4 max-w-6xl">
          <h2 className="text-4xl font-heading font-bold text-center text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-center text-white/60 mb-16">
            Start free. Upgrade as you grow.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: 'Free',
                price: 'Free',
                description: 'Perfect for getting started',
                features: [
                  'Free career risk scan',
                  'Job market insights',
                  '2 AI coach sessions/month',
                  'Basic job matching',
                  'Community access'
                ]
              },
              {
                name: 'Pro',
                price: '$19/mo',
                description: 'For serious career builders',
                features: [
                  'Everything in Free',
                  'Unlimited AI coach sessions',
                  'Advanced job matching',
                  'Learning roadmap',
                  'Priority support',
                  'Monthly insights report'
                ],
                highlighted: true
              },
              {
                name: 'Enterprise',
                price: '$99/mo',
                description: 'For maximum career growth',
                features: [
                  'Everything in Pro',
                  'Resume optimizer',
                  'Mock interview training',
                  'Job alert system',
                  '1-on-1 career coaching',
                  'Custom learning plans',
                  'Dedicated support'
                ]
              }
            ].map((plan, i) => (
              <div 
                key={i} 
                className={`relative rounded-xl border transition-all ${
                  plan.highlighted 
                    ? 'bg-gradient-to-b from-next-gold/20 to-next-royal-blue/20 border-next-gold/50 shadow-next-gold'
                    : 'bg-white/5 border-white/10 hover:border-next-gold/30'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-next-gold text-next-deep-blue px-4 py-1 rounded-full text-sm font-bold">
                    Most Popular
                  </div>
                )}

                <div className="p-8">
                  <h3 className="text-2xl font-heading font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-white/60 text-sm mb-6">{plan.description}</p>
                  
                  <div className="mb-6">
                    <span className="text-3xl font-bold text-white">{plan.price}</span>
                  </div>

                  <button 
                    onClick={() => setIsModalOpen(true)}
                    className={`w-full py-3 rounded-lg font-semibold transition-all mb-8 ${
                      plan.highlighted
                        ? 'bg-next-gold hover:bg-next-gold-light text-next-deep-blue shadow-next-gold hover:shadow-next-xl'
                        : 'bg-white/10 hover:bg-white/20 text-white border border-white/30'
                    }`}
                  >
                    Get Started
                  </button>

                  <ul className="space-y-3">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-start gap-2 text-white/80">
                        <span className="text-next-gold mt-1">✓</span>
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 border-t border-white/10 bg-gradient-to-b from-transparent to-next-gold/10">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-heading font-bold text-white mb-6">
            Ready to Future-Proof Your Career?
          </h2>
          <p className="text-white/70 mb-8 max-w-2xl mx-auto">
            Join thousands of professionals who&apos;ve already discovered their AI-proof path. 
            Start your free career risk scan today.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 px-8 py-4 bg-next-gold hover:bg-next-gold-light text-next-deep-blue font-heading font-bold rounded-lg transition-all shadow-next-gold hover:shadow-next-xl transform hover:scale-105 active:scale-95"
          >
            Find My Future
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-next-dark-bg">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <NextLogo variant="text" size="sm" />
              <p className="text-white/60 text-sm mt-4">
                AI-powered career intelligence for the future of work.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-white/60 text-sm">
                <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
                <li><Link href="/voice-coach" className="hover:text-white transition-colors">AI Coach</Link></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-white/60 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-white/60 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8">
            <p className="text-white/60 text-center text-sm">
              © {new Date().getFullYear()} Next. All rights reserved. Made for the future.
            </p>
          </div>
        </div>
      </footer>

      {/* Career Scan Modal */}
      <CareerRiskScanModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </main>
  );
}
