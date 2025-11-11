import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Cookie Policy | NEXT Career Intelligence',
  description: 'Cookie Policy for NEXT Career Intelligence Platform',
}

export default function CookiePolicyPage() {
  const lastUpdated = 'November 10, 2025'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Cookie Policy</h1>
            <p className="text-gray-600">Last Updated: {lastUpdated}</p>
          </div>

          {/* Content */}
          <div className="prose prose-lg max-w-none">
            {/* Introduction */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. What Are Cookies?</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Cookies are small text files that are stored on your device (computer, tablet, smartphone) when you visit a website.
                They help websites remember your preferences, improve your experience, and provide analytics to website operators.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                NEXT Career Intelligence ("NEXT", "we", "us", or "our") uses cookies and similar tracking technologies to enhance
                your experience on our platform. This Cookie Policy explains what cookies we use, why we use them, and how you can
                control them.
              </p>
            </section>

            {/* Types of Cookies */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Types of Cookies We Use</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We use different types of cookies for different purposes:
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.1 Essential Cookies (Strictly Necessary)</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                These cookies are required for our platform to function properly. Without them, core features like login and
                navigation would not work.
              </p>
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left">Cookie Name</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>next_session</code></td>
                      <td className="border border-gray-300 px-4 py-2">Maintains your login session</td>
                      <td className="border border-gray-300 px-4 py-2">7 days</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>auth_token</code></td>
                      <td className="border border-gray-300 px-4 py-2">Authenticates your account access</td>
                      <td className="border border-gray-300 px-4 py-2">30 days</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>csrf_token</code></td>
                      <td className="border border-gray-300 px-4 py-2">Prevents cross-site request forgery attacks</td>
                      <td className="border border-gray-300 px-4 py-2">Session</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>cookie_consent</code></td>
                      <td className="border border-gray-300 px-4 py-2">Remembers your cookie preferences</td>
                      <td className="border border-gray-300 px-4 py-2">1 year</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Note:</strong> Essential cookies cannot be disabled as they are necessary for platform functionality.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.2 Performance and Analytics Cookies</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                These cookies help us understand how users interact with our platform, allowing us to improve performance and user
                experience.
              </p>
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left">Cookie Name</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>_ga</code></td>
                      <td className="border border-gray-300 px-4 py-2">Google Analytics: Distinguishes unique users</td>
                      <td className="border border-gray-300 px-4 py-2">2 years</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>_ga_*</code></td>
                      <td className="border border-gray-300 px-4 py-2">Google Analytics: Stores session state</td>
                      <td className="border border-gray-300 px-4 py-2">2 years</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>next_analytics</code></td>
                      <td className="border border-gray-300 px-4 py-2">Tracks feature usage and performance metrics</td>
                      <td className="border border-gray-300 px-4 py-2">1 year</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.3 Functional Cookies</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                These cookies enable enhanced functionality and personalization, such as remembering your preferences.
              </p>
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left">Cookie Name</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>theme_preference</code></td>
                      <td className="border border-gray-300 px-4 py-2">Remembers dark mode / light mode preference</td>
                      <td className="border border-gray-300 px-4 py-2">1 year</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>language_pref</code></td>
                      <td className="border border-gray-300 px-4 py-2">Stores your preferred language</td>
                      <td className="border border-gray-300 px-4 py-2">1 year</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2"><code>dashboard_layout</code></td>
                      <td className="border border-gray-300 px-4 py-2">Saves your custom dashboard configuration</td>
                      <td className="border border-gray-300 px-4 py-2">6 months</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.4 Marketing and Advertising Cookies (Currently Not Used)</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We currently do not use marketing or advertising cookies. If we choose to use them in the future, we will update
                this policy and obtain your consent.
              </p>
            </section>

            {/* Third-Party Cookies */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. Third-Party Cookies</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Some cookies are placed by third-party services we use to enhance our platform:
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">3.1 Google Analytics</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We use Google Analytics to understand how users interact with our platform. Google Analytics sets cookies to collect
                information such as:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Number of visitors and sessions</li>
                <li>Pages visited and time spent</li>
                <li>User demographics (age range, location)</li>
                <li>Device and browser information</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                Learn more: <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  Google Privacy Policy
                </a>
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">3.2 Stripe (Payment Processing)</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Stripe sets cookies when you make a payment to detect fraud and ensure secure transactions.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Learn more: <a href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  Stripe Privacy Policy
                </a>
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">3.3 Intercom (Customer Support)</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Intercom sets cookies to provide live chat support and remember your conversation history.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Learn more: <a href="https://www.intercom.com/legal/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  Intercom Privacy Policy
                </a>
              </p>
            </section>

            {/* Why We Use Cookies */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Why We Use Cookies</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We use cookies to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Authentication:</strong> Keep you logged in securely</li>
                <li><strong>Security:</strong> Detect and prevent fraud, protect against attacks</li>
                <li><strong>Performance:</strong> Analyze platform performance and identify bugs</li>
                <li><strong>Personalization:</strong> Remember your preferences (theme, language)</li>
                <li><strong>Analytics:</strong> Understand user behavior to improve features</li>
                <li><strong>User Experience:</strong> Provide seamless navigation and functionality</li>
              </ul>
            </section>

            {/* Managing Cookies */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. How to Manage Cookies</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.1 Cookie Consent Banner</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                When you first visit NEXT, you'll see a cookie consent banner. You can choose to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Accept All:</strong> Allow all cookies (essential, analytics, functional)</li>
                <li><strong>Essential Only:</strong> Only allow cookies necessary for platform functionality</li>
                <li><strong>Customize:</strong> Choose which cookie categories to allow</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                You can change your preferences at any time by clicking the "Cookie Settings" link in the footer.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.2 Browser Settings</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You can also control cookies through your browser settings. Most browsers allow you to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>View and delete cookies</li>
                <li>Block all cookies</li>
                <li>Block third-party cookies only</li>
                <li>Clear cookies when you close your browser</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Browser-specific instructions:</strong>
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>
                  <strong>Chrome:</strong> Settings → Privacy and security → Cookies and other site data
                  {' '}
                  <a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    (Learn more)
                  </a>
                </li>
                <li>
                  <strong>Firefox:</strong> Settings → Privacy & Security → Cookies and Site Data
                  {' '}
                  <a href="https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    (Learn more)
                  </a>
                </li>
                <li>
                  <strong>Safari:</strong> Preferences → Privacy → Manage Website Data
                  {' '}
                  <a href="https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    (Learn more)
                  </a>
                </li>
                <li>
                  <strong>Edge:</strong> Settings → Cookies and site permissions
                  {' '}
                  <a href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    (Learn more)
                  </a>
                </li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Important:</strong> Blocking or deleting essential cookies may impact platform functionality.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.3 Opt-Out of Analytics</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                To opt-out of Google Analytics across all websites:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>
                  Install the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    Google Analytics Opt-out Browser Add-on
                  </a>
                </li>
                <li>Enable "Do Not Track" in your browser settings</li>
              </ul>
            </section>

            {/* Do Not Track */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Do Not Track Signals</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Some browsers have a "Do Not Track" (DNT) feature that signals websites not to track your browsing activity. We
                currently do not respond to DNT signals, as there is no industry-wide standard for handling them.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                However, you can use our cookie consent banner and browser settings to control tracking on NEXT.
              </p>
            </section>

            {/* Updates */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. Updates to This Cookie Policy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may update this Cookie Policy from time to time to reflect changes in our practices or for legal reasons. Updates
                will be posted on this page with a revised "Last Updated" date.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                We encourage you to review this policy periodically to stay informed about our cookie usage.
              </p>
            </section>

            {/* Contact */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">8. Contact Us</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you have questions about our cookie practices, please contact us:
              </p>
              <div className="bg-gray-50 p-6 rounded-lg">
                <p className="text-gray-700 mb-2"><strong>NEXT Career Intelligence</strong></p>
                <p className="text-gray-700 mb-2">Email: privacy@nextcareer.ai</p>
                <p className="text-gray-700 mb-2">Support: hello@nextcareer.ai</p>
                <p className="text-gray-700">Response Time: Within 3-5 business days</p>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              This Cookie Policy was last updated on {lastUpdated}. By continuing to use NEXT Career Intelligence, you consent to
              our use of cookies as described in this policy.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
