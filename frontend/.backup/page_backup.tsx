'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [jobTitle, setJobTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) return;

    setIsAnalyzing(true);
    // Redirect to analysis page or modal
    router.push(`/analyze?job=${encodeURIComponent(jobTitle)}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-500 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-indigo-500 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12">
        <div className="max-w-4xl w-full text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-yellow-400" />
            <span className="text-white/90 text-sm font-medium">Powered by AI</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Is Your Job
            <span className="block bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              AI-Proof?
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-white/80 mb-12 max-w-2xl mx-auto">
            Get a free AI-powered analysis of your career's automation risk and discover skills that future-proof your career
          </p>

          {/* Input Form */}
          <form onSubmit={handleAnalyze} className="max-w-2xl mx-auto mb-8">
            <div className="flex flex-col sm:flex-row gap-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-3 shadow-2xl">
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Enter your job title (e.g., Software Engineer)"
                className="flex-1 px-6 py-4 bg-white/90 border-0 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                disabled={isAnalyzing}
              />
              <button
                type="submit"
                disabled={!jobTitle.trim() || isAnalyzing}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap shadow-lg hover:shadow-xl"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    Analyze Free
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-8 text-white/60 text-sm mb-16">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              <span>100% Free Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              <span>AI-Powered Insights</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              <span>Personalized Roadmap</span>
            </div>
          </div>

          {/* Social Proof */}
          <div className="max-w-3xl mx-auto bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <div className="grid md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-4xl font-bold text-white mb-2">10k+</div>
                <div className="text-white/60">Careers Analyzed</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white mb-2">87%</div>
                <div className="text-white/60">Found Skills to Learn</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white mb-2">4.9/5</div>
                <div className="text-white/60">User Rating</div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="mt-16 text-center">
          <p className="text-white/50 text-sm mb-4">
            Join thousands of professionals taking control of their careers
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <a href="#" className="text-white/60 hover:text-white text-sm transition-colors">
              How It Works
            </a>
            <span className="text-white/30">•</span>
            <a href="#" className="text-white/60 hover:text-white text-sm transition-colors">
              Success Stories
            </a>
            <span className="text-white/30">•</span>
            <a href="/dashboard" className="text-white/60 hover:text-white text-sm transition-colors">
              Sign In
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
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
