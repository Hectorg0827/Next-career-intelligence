'use client'

import { useState } from 'react'
import { Metadata } from 'next'

// Note: This is a client component for interactivity
// Metadata export won't work here, will need to move to parent layout

export default function HelpCenterPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState<string | null>(null)

  const categories = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: '🚀',
      articles: [
        { title: 'How to create an account', link: '#create-account' },
        { title: 'Completing your profile', link: '#complete-profile' },
        { title: 'Uploading your first resume', link: '#upload-resume' },
        { title: 'Setting career goals', link: '#set-goals' },
      ],
    },
    {
      id: 'resume-studio',
      title: 'Resume Studio',
      icon: '📄',
      articles: [
        { title: 'How to tailor your resume to a job', link: '#tailor-resume' },
        { title: 'Understanding AI suggestions', link: '#ai-suggestions' },
        { title: 'Downloading your tailored resume', link: '#download-resume' },
        { title: 'Resume best practices', link: '#resume-best-practices' },
      ],
    },
    {
      id: 'job-search',
      title: 'Job Search & Applications',
      icon: '💼',
      articles: [
        { title: 'How job matching works', link: '#job-matching' },
        { title: 'Tracking your applications', link: '#track-applications' },
        { title: 'Saving jobs for later', link: '#save-jobs' },
        { title: 'Understanding compatibility scores', link: '#compatibility-scores' },
      ],
    },
    {
      id: 'career-coach',
      title: 'AI Career Coach',
      icon: '🤖',
      articles: [
        { title: 'Asking career questions', link: '#ask-questions' },
        { title: 'Getting salary negotiation advice', link: '#salary-advice' },
        { title: 'Career transition guidance', link: '#career-transition' },
        { title: 'Setting and tracking goals', link: '#goals' },
      ],
    },
    {
      id: 'interviewer',
      title: 'Interviewer AI',
      icon: '🎤',
      articles: [
        { title: 'Scheduling a mock interview', link: '#schedule-interview' },
        { title: 'Types of interviews available', link: '#interview-types' },
        { title: 'Understanding interview feedback', link: '#interview-feedback' },
        { title: 'Improving your interview skills', link: '#improve-skills' },
      ],
    },
    {
      id: 'career-health',
      title: 'Career Health Score',
      icon: '📊',
      articles: [
        { title: 'What is Career Health Score?', link: '#chs-what' },
        { title: 'How the score is calculated', link: '#chs-calculation' },
        { title: 'Improving your score', link: '#improve-score' },
        { title: 'Score history and trends', link: '#score-trends' },
      ],
    },
    {
      id: 'billing',
      title: 'Billing & Subscriptions',
      icon: '💳',
      articles: [
        { title: 'Subscription plans explained', link: '#plans' },
        { title: 'Upgrading or downgrading', link: '#upgrade-downgrade' },
        { title: 'Payment methods', link: '#payment-methods' },
        { title: 'Canceling your subscription', link: '#cancel' },
        { title: 'Refund policy', link: '#refunds' },
      ],
    },
    {
      id: 'account',
      title: 'Account & Security',
      icon: '🔒',
      articles: [
        { title: 'Changing your password', link: '#change-password' },
        { title: 'Enabling two-factor authentication', link: '#2fa' },
        { title: 'Privacy settings', link: '#privacy-settings' },
        { title: 'Exporting your data (GDPR)', link: '#export-data' },
        { title: 'Deleting your account', link: '#delete-account' },
      ],
    },
  ]

  const filteredCategories = categories.map(category => ({
    ...category,
    articles: category.articles.filter(article =>
      article.title.toLowerCase().includes(searchQuery.toLowerCase())
    ),
  })).filter(category => category.articles.length > 0 || searchQuery === '')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Help Center</h1>
          <p className="text-xl text-gray-600 mb-8">
            Find answers to common questions and learn how to make the most of NEXT
          </p>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Search for help..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-6 py-4 pl-12 rounded-lg border-2 border-gray-300 focus:border-blue-500 focus:outline-none text-lg"
              />
              <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-2xl">
                🔍
              </span>
            </div>
          </div>
        </div>

        {/* Categories Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredCategories.map((category) => (
            <div
              key={category.id}
              className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition cursor-pointer"
              onClick={() => setActiveCategory(category.id === activeCategory ? null : category.id)}
            >
              <div className="flex items-center mb-4">
                <span className="text-4xl mr-3">{category.icon}</span>
                <h2 className="text-2xl font-semibold text-gray-800">{category.title}</h2>
              </div>
              <ul className="space-y-2">
                {category.articles.map((article, index) => (
                  <li key={index}>
                    <a
                      href={article.link}
                      className="text-blue-600 hover:text-blue-800 hover:underline block"
                    >
                      {article.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Contact Support */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-xl p-8 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Can't find what you're looking for?</h2>
          <p className="text-xl mb-6">
            Our support team is here to help
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <a
              href="mailto:support@nextcareer.ai"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
            >
              Email Support
            </a>
            <button
              onClick={() => {
                // Intercom chat widget would open here
                alert('Live chat will open here (Intercom integration)')
              }}
              className="bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition"
            >
              Live Chat
            </button>
          </div>
          <p className="text-sm mt-4 opacity-90">
            Response time: &lt; 24 hours (Pro/Elite users: &lt; 4 hours)
          </p>
        </div>

        {/* Popular Articles */}
        <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Popular Articles</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <a href="#tailor-resume" className="flex items-start p-4 hover:bg-gray-50 rounded-lg transition">
              <span className="text-2xl mr-3">⭐</span>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">How to tailor your resume to a job</h3>
                <p className="text-sm text-gray-600">Learn how NEXT's AI optimizes your resume for each application</p>
              </div>
            </a>

            <a href="#chs-what" className="flex items-start p-4 hover:bg-gray-50 rounded-lg transition">
              <span className="text-2xl mr-3">⭐</span>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">What is Career Health Score?</h3>
                <p className="text-sm text-gray-600">Understand your career vitality metric and how to improve it</p>
              </div>
            </a>

            <a href="#schedule-interview" className="flex items-start p-4 hover:bg-gray-50 rounded-lg transition">
              <span className="text-2xl mr-3">⭐</span>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">Scheduling a mock interview</h3>
                <p className="text-sm text-gray-600">Practice interviews with AI feedback to ace your next real interview</p>
              </div>
            </a>

            <a href="#plans" className="flex items-start p-4 hover:bg-gray-50 rounded-lg transition">
              <span className="text-2xl mr-3">⭐</span>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">Subscription plans explained</h3>
                <p className="text-sm text-gray-600">Compare Free, Pro, and Elite plans to find the right fit</p>
              </div>
            </a>
          </div>
        </div>

        {/* Additional Resources */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-4xl mb-3">📚</div>
            <h3 className="font-semibold text-gray-800 mb-2">Documentation</h3>
            <p className="text-sm text-gray-600 mb-4">
              Comprehensive guides and API documentation
            </p>
            <a href="/docs" className="text-blue-600 hover:underline">
              View Docs →
            </a>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-4xl mb-3">🎥</div>
            <h3 className="font-semibold text-gray-800 mb-2">Video Tutorials</h3>
            <p className="text-sm text-gray-600 mb-4">
              Step-by-step video guides for all features
            </p>
            <a href="/tutorials" className="text-blue-600 hover:underline">
              Watch Videos →
            </a>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-4xl mb-3">💬</div>
            <h3 className="font-semibold text-gray-800 mb-2">Community Forum</h3>
            <p className="text-sm text-gray-600 mb-4">
              Connect with other NEXT users
            </p>
            <a href="/community" className="text-blue-600 hover:underline">
              Join Community →
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
