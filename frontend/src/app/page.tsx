import Link from "next/link";
import { ArrowRight, Brain, TrendingUp, Shield, Zap } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              NEXT
            </span>
          </div>
          <div className="flex gap-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/login" className="text-gray-600 hover:text-gray-900">
              Sign In
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Adaptive Career Intelligence
          </h1>
          <p className="text-xl text-gray-700 mb-8 max-w-2xl mx-auto">
            Understand your AI displacement risk, discover future-proof career pathways, 
            and navigate the evolving job landscape with confidence.
          </p>
          
          <Link 
            href="/dashboard" 
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl"
          >
            Check Your AI Risk Now
            <ArrowRight className="w-5 h-5" />
          </Link>
          
          <p className="mt-4 text-sm text-gray-500">
            Free analysis • No credit card required • Real-time AI insights
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={<Brain className="w-8 h-8 text-blue-600" />}
            title="AI Risk Analysis"
            description="Get real-time assessment of your job's automation potential powered by GPT-5"
          />
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8 text-green-600" />}
            title="Career Pathways"
            description="Discover transition opportunities to future-proof roles with high human advantage"
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8 text-purple-600" />}
            title="Skill Gap Analysis"
            description="Identify missing skills and get personalized training recommendations"
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8 text-yellow-600" />}
            title="Real Data"
            description="Powered by O*NET, LinkedIn, and Coursera APIs - no mock data"
          />
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16 bg-white rounded-2xl shadow-xl my-16">
        <h2 className="text-4xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <StepCard
            number="1"
            title="Enter Your Info"
            description="Tell us your current job title, skills, and location"
          />
          <StepCard
            number="2"
            title="AI Analysis"
            description="Our AI analyzes displacement risk and compatibility using real labor market data"
          />
          <StepCard
            number="3"
            title="Get Your Plan"
            description="Receive personalized transition pathways and training recommendations"
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white shadow-2xl">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Future-Proof Your Career?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of professionals navigating the AI revolution
          </p>
          <Link 
            href="/dashboard" 
            className="inline-flex items-center gap-2 bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all shadow-lg"
          >
            Start Free Analysis
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 border-t border-gray-200 mt-20">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-600" />
            <span className="font-semibold">NEXT Career Intelligence</span>
          </div>
          <p className="text-gray-600 text-sm">
            © 2025 NEXT. Powered by OpenAI, O*NET, and Coursera.
          </p>
          <div className="flex gap-6 text-sm text-gray-600">
            <a href="#" className="hover:text-gray-900">Privacy</a>
            <a href="#" className="hover:text-gray-900">Terms</a>
            <a href="#" className="hover:text-gray-900">Support</a>
          </div>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
