import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About Us | NEXT Career Intelligence',
  description: 'Learn about NEXT Career Intelligence and our mission to transform career development with AI',
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-5xl font-bold mb-6">About NEXT Career Intelligence</h1>
          <p className="text-xl leading-relaxed">
            Empowering professionals with AI-driven career intelligence to navigate the future of work with confidence.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          {/* Mission */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Mission</h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-4">
              NEXT Career Intelligence is on a mission to democratize access to world-class career guidance through artificial
              intelligence. We believe that everyone deserves personalized, data-driven career insights that were previously only
              available to executives and high-net-worth individuals.
            </p>
            <p className="text-lg text-gray-700 leading-relaxed">
              In an era of rapid technological change, we're building the tools that help professionals stay competitive, discover
              new opportunities, and achieve their career goals faster.
            </p>
          </section>

          {/* What We Do */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">What We Do</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-blue-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">🎯 Resume Intelligence</h3>
                <p className="text-gray-700">
                  AI-powered resume tailoring that adapts your experience to each job posting, maximizing your chances of landing
                  interviews.
                </p>
              </div>

              <div className="bg-green-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">💼 Job Matching</h3>
                <p className="text-gray-700">
                  Intelligent job recommendations based on your skills, experience, and career goals, not just keyword matching.
                </p>
              </div>

              <div className="bg-purple-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">🤖 AI Career Coach</h3>
                <p className="text-gray-700">
                  24/7 conversational AI guidance for career decisions, salary negotiations, and professional development.
                </p>
              </div>

              <div className="bg-yellow-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">🎤 Interview Prep</h3>
                <p className="text-gray-700">
                  Realistic mock interviews with AI-powered feedback to help you ace behavioral and technical interviews.
                </p>
              </div>

              <div className="bg-red-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">📊 Career Health Score</h3>
                <p className="text-gray-700">
                  Quantifiable metric that tracks your career vitality and provides actionable recommendations for improvement.
                </p>
              </div>

              <div className="bg-indigo-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">🕸️ Talent Graph</h3>
                <p className="text-gray-700">
                  Discover skill gaps and career pathways using our proprietary knowledge graph of career relationships.
                </p>
              </div>
            </div>
          </section>

          {/* Our Technology */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Technology</h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              NEXT is powered by cutting-edge AI technology that learns and improves with every interaction:
            </p>
            <ul className="space-y-4">
              <li className="flex items-start">
                <span className="text-blue-600 text-2xl mr-4">🧠</span>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Reinforcement Fine-Tuning (RFT)</h4>
                  <p className="text-gray-700">
                    Our AI learns from user success signals to provide increasingly better recommendations over time.
                  </p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 text-2xl mr-4">🌐</span>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Neo4j Talent Graph</h4>
                  <p className="text-gray-700">
                    Graph database technology that maps relationships between skills, roles, and career pathways.
                  </p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 text-2xl mr-4">🤖</span>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Multi-Agent AI System</h4>
                  <p className="text-gray-700">
                    Specialized AI agents for different tasks (resume writing, interview prep, career coaching) working in concert.
                  </p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="text-orange-600 text-2xl mr-4">📈</span>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Real-Time Job Intelligence</h4>
                  <p className="text-gray-700">
                    Scraping and analyzing job postings from hundreds of companies to provide up-to-date market insights.
                  </p>
                </div>
              </li>
            </ul>
          </section>

          {/* Our Values */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Values</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-blue-600 pl-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">🔒 Privacy First</h3>
                <p className="text-gray-700">
                  Your data is yours. We never sell your personal information and use industry-leading security to protect it.
                </p>
              </div>

              <div className="border-l-4 border-green-600 pl-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">🎯 Outcome-Focused</h3>
                <p className="text-gray-700">
                  Every feature is designed to help you achieve tangible career outcomes: more interviews, better offers, faster
                  growth.
                </p>
              </div>

              <div className="border-l-4 border-purple-600 pl-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">🚀 Continuous Innovation</h3>
                <p className="text-gray-700">
                  We're constantly improving our AI models and adding new features based on user feedback and the latest research.
                </p>
              </div>

              <div className="border-l-4 border-yellow-600 pl-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">🤝 User Empowerment</h3>
                <p className="text-gray-700">
                  AI augments human decision-making, not replaces it. You're always in control of your career journey.
                </p>
              </div>
            </div>
          </section>

          {/* Why Choose NEXT */}
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Why Choose NEXT?</h2>
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg">
              <ul className="space-y-4 text-gray-700">
                <li className="flex items-center">
                  <span className="text-green-600 text-xl mr-3">✓</span>
                  <span><strong>Self-Improving AI:</strong> Gets better with every user interaction through RFT</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-600 text-xl mr-3">✓</span>
                  <span><strong>Proprietary Career Intelligence:</strong> Unique insights from our Talent Graph</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-600 text-xl mr-3">✓</span>
                  <span><strong>Holistic Approach:</strong> Resume, jobs, coaching, and interview prep in one platform</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-600 text-xl mr-3">✓</span>
                  <span><strong>Data-Driven:</strong> Career Health Score quantifies your career vitality</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-600 text-xl mr-3">✓</span>
                  <span><strong>Real Jobs:</strong> Live job data from 500+ companies, not stale listings</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-600 text-xl mr-3">✓</span>
                  <span><strong>Privacy-Focused:</strong> GDPR compliant, never sell your data</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Contact */}
          <section className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Get in Touch</h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              Have questions or feedback? We'd love to hear from you.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">General Inquiries</h3>
                <p className="text-gray-700 mb-2">
                  <a href="mailto:hello@nextcareer.ai" className="text-blue-600 hover:underline">hello@nextcareer.ai</a>
                </p>
                <p className="text-gray-600 text-sm">Response within 24-48 hours</p>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Support</h3>
                <p className="text-gray-700 mb-2">
                  <a href="mailto:support@nextcareer.ai" className="text-blue-600 hover:underline">support@nextcareer.ai</a>
                </p>
                <p className="text-gray-600 text-sm">Priority support for Pro/Elite users</p>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Privacy & Data</h3>
                <p className="text-gray-700 mb-2">
                  <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a>
                </p>
                <p className="text-gray-600 text-sm">GDPR requests within 30 days</p>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Partnerships</h3>
                <p className="text-gray-700 mb-2">
                  <a href="mailto:partnerships@nextcareer.ai" className="text-blue-600 hover:underline">partnerships@nextcareer.ai</a>
                </p>
                <p className="text-gray-600 text-sm">Business inquiries & collaborations</p>
              </div>
            </div>
          </section>

          {/* CTA */}
          <section className="text-center py-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg">
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your Career?</h2>
            <p className="text-xl text-white mb-6">
              Join thousands of professionals using AI to accelerate their career growth.
            </p>
            <div className="flex justify-center gap-4">
              <a
                href="/signup"
                className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Get Started Free
              </a>
              <a
                href="/pricing"
                className="bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-600 transition"
              >
                View Pricing
              </a>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
