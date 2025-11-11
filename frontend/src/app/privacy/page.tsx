import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy | NEXT Career Intelligence',
  description: 'Privacy Policy for NEXT Career Intelligence Platform',
}

export default function PrivacyPolicyPage() {
  const lastUpdated = 'November 10, 2025'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
            <p className="text-gray-600">Last Updated: {lastUpdated}</p>
          </div>

          {/* Content */}
          <div className="prose prose-lg max-w-none">
            {/* Introduction */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Introduction</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Welcome to NEXT Career Intelligence ("NEXT", "we", "us", or "our"). We are committed to protecting your personal
                information and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard
                your information when you use our career intelligence platform.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                By using NEXT, you agree to the collection and use of information in accordance with this policy. If you do not
                agree with our policies and practices, please do not use our services.
              </p>
            </section>

            {/* Information We Collect */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Information We Collect</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.1 Personal Information</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We collect information that you voluntarily provide when registering, using our services, or communicating with us:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Account Information: Name, email address, password (encrypted)</li>
                <li>Profile Information: Current job title, experience level, skills, location, career goals</li>
                <li>Resume Data: Work history, education, certifications, accomplishments</li>
                <li>Application Data: Jobs applied to, interview history, application outcomes</li>
                <li>Payment Information: Billing address, payment method (processed securely via Stripe)</li>
                <li>Communications: Messages with our AI career coach, mock interview transcripts</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.2 Automatically Collected Information</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                When you use NEXT, we automatically collect certain information:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Usage Data: Pages visited, features used, time spent, click patterns</li>
                <li>Device Information: Browser type, operating system, device identifiers</li>
                <li>Log Data: IP address, timestamps, error logs, performance metrics</li>
                <li>Cookies and Tracking: Analytics cookies, authentication tokens, preferences</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">2.3 AI Training Data</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We collect feedback on AI-generated content (resume bullets, interview answers) to improve our models through
                Reinforcement Fine-Tuning (RFT). This includes:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>User acceptance/rejection of AI suggestions</li>
                <li>Ratings and edits to AI-generated content</li>
                <li>Success signals (interviews secured, offers received)</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Note:</strong> This data is anonymized and aggregated for model training purposes.
              </p>
            </section>

            {/* How We Use Your Information */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. How We Use Your Information</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We use your information for the following purposes:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Service Delivery:</strong> Provide resume tailoring, job matching, career coaching, mock interviews</li>
                <li><strong>Personalization:</strong> Customize job recommendations, career pathways, skill gap analysis</li>
                <li><strong>AI Improvement:</strong> Train our proprietary AI models to provide better suggestions</li>
                <li><strong>Analytics:</strong> Calculate Career Health Score, track application success, measure engagement</li>
                <li><strong>Communication:</strong> Send email notifications, weekly job digests, account updates</li>
                <li><strong>Payment Processing:</strong> Process subscription payments, manage billing</li>
                <li><strong>Security:</strong> Detect fraud, prevent abuse, ensure platform security</li>
                <li><strong>Compliance:</strong> Meet legal obligations, enforce our Terms of Service</li>
              </ul>
            </section>

            {/* Data Sharing and Disclosure */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Data Sharing and Disclosure</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>We do NOT sell your personal information.</strong> We may share your information in the following circumstances:
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">4.1 Service Providers</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We share data with trusted third-party vendors who help us operate our platform:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Supabase (Database):</strong> User data, resume content, application tracking</li>
                <li><strong>Google Gemini (AI):</strong> Resume content, job descriptions (for AI processing)</li>
                <li><strong>Stripe (Payments):</strong> Payment information, billing data</li>
                <li><strong>SendGrid (Emails):</strong> Email addresses, notification content</li>
                <li><strong>Sentry (Monitoring):</strong> Error logs, performance data</li>
                <li><strong>Cloudflare (CDN):</strong> IP addresses, request logs</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                All service providers are contractually obligated to protect your data and use it only for specified purposes.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">4.2 Legal Requirements</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may disclose your information if required by law, court order, or government request, or to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Comply with legal obligations</li>
                <li>Protect our rights, property, or safety</li>
                <li>Prevent fraud or security threats</li>
                <li>Respond to emergency situations</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">4.3 Business Transfers</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                If NEXT is acquired, merged, or undergoes a business transition, your information may be transferred to the
                successor entity. You will be notified via email of any such change.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">4.4 With Your Consent</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may share your information for other purposes with your explicit consent.
              </p>
            </section>

            {/* Data Retention */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. Data Retention</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We retain your information for as long as necessary to provide our services and comply with legal obligations:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Active Accounts:</strong> Data retained while account is active</li>
                <li><strong>Deleted Accounts:</strong> Most data deleted within 30 days (some anonymized data retained for analytics)</li>
                <li><strong>RFT Training Data:</strong> Anonymized feedback retained indefinitely for AI model improvement</li>
                <li><strong>Billing Records:</strong> Retained for 7 years for tax/accounting purposes</li>
                <li><strong>Legal Holds:</strong> Data subject to legal proceedings retained until resolved</li>
              </ul>
            </section>

            {/* Your Rights and Choices */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Your Rights and Choices</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">6.1 Access and Portability</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You have the right to access and download your personal data. Visit your account settings or contact us at
                privacy@nextcareer.ai to request a copy of your data in machine-readable format (JSON).
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">6.2 Correction and Update</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You can update your profile information, resume data, and preferences at any time through your account settings.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">6.3 Deletion (Right to be Forgotten)</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You can request deletion of your account and personal data at any time. We will delete your data within 30 days,
                except for:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Anonymized RFT training data (cannot be linked back to you)</li>
                <li>Billing records (required for tax/legal compliance)</li>
                <li>Data subject to legal holds</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">6.4 Opt-Out of Marketing</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You can unsubscribe from marketing emails by clicking the "unsubscribe" link in any email or updating your
                notification preferences.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">6.5 Cookie Management</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You can control cookie preferences through your browser settings or our cookie consent banner. Note that disabling
                essential cookies may impact platform functionality.
              </p>
            </section>

            {/* GDPR Rights (EU Users) */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. GDPR Rights (EU Users)</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you are located in the European Economic Area (EEA), you have additional rights under GDPR:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Right to Access:</strong> Request a copy of your personal data</li>
                <li><strong>Right to Rectification:</strong> Correct inaccurate data</li>
                <li><strong>Right to Erasure:</strong> Request deletion of your data</li>
                <li><strong>Right to Restriction:</strong> Limit how we use your data</li>
                <li><strong>Right to Data Portability:</strong> Receive your data in machine-readable format</li>
                <li><strong>Right to Object:</strong> Object to data processing for direct marketing</li>
                <li><strong>Right to Withdraw Consent:</strong> Withdraw consent at any time</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                To exercise these rights, contact us at privacy@nextcareer.ai. We will respond within 30 days.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                You also have the right to lodge a complaint with your local data protection authority.
              </p>
            </section>

            {/* Data Security */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">8. Data Security</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We implement industry-standard security measures to protect your information:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Encryption:</strong> Data encrypted in transit (TLS 1.3) and at rest (AES-256)</li>
                <li><strong>Authentication:</strong> Secure password hashing (bcrypt), optional 2FA</li>
                <li><strong>Access Control:</strong> Role-based access, row-level security in database</li>
                <li><strong>Monitoring:</strong> 24/7 security monitoring, intrusion detection</li>
                <li><strong>Backups:</strong> Daily automated backups with 30-day retention</li>
                <li><strong>Compliance:</strong> SOC 2 Type II, GDPR, CCPA compliant infrastructure</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                While we strive to protect your data, no method of transmission over the internet is 100% secure. We cannot
                guarantee absolute security.
              </p>
            </section>

            {/* Children's Privacy */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">9. Children's Privacy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                NEXT is not intended for individuals under 18 years of age. We do not knowingly collect personal information from
                children. If you are a parent or guardian and believe your child has provided us with personal information, please
                contact us at privacy@nextcareer.ai, and we will delete such information promptly.
              </p>
            </section>

            {/* International Data Transfers */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">10. International Data Transfers</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Your information may be transferred to and processed in countries other than your country of residence, including
                the United States. These countries may have data protection laws different from your jurisdiction.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                We ensure adequate safeguards are in place, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Standard Contractual Clauses (SCCs) approved by the European Commission</li>
                <li>Data Processing Agreements with all third-party vendors</li>
                <li>Compliance with applicable data transfer regulations</li>
              </ul>
            </section>

            {/* California Privacy Rights (CCPA) */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">11. California Privacy Rights (CCPA)</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you are a California resident, you have the following rights under CCPA:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Right to Know:</strong> Request disclosure of personal information collected</li>
                <li><strong>Right to Delete:</strong> Request deletion of personal information</li>
                <li><strong>Right to Opt-Out:</strong> Opt-out of the sale of personal information (we do not sell your data)</li>
                <li><strong>Right to Non-Discrimination:</strong> Not be discriminated against for exercising your rights</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                To exercise these rights, contact us at privacy@nextcareer.ai.
              </p>
            </section>

            {/* Changes to Privacy Policy */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">12. Changes to This Privacy Policy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last
                Updated" date. For material changes, we will notify you via email or prominent notice on our platform.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Your continued use of NEXT after changes constitutes acceptance of the updated Privacy Policy.
              </p>
            </section>

            {/* Contact Us */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">13. Contact Us</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
              </p>
              <div className="bg-gray-50 p-6 rounded-lg">
                <p className="text-gray-700 mb-2"><strong>NEXT Career Intelligence</strong></p>
                <p className="text-gray-700 mb-2">Email: privacy@nextcareer.ai</p>
                <p className="text-gray-700 mb-2">Support: hello@nextcareer.ai</p>
                <p className="text-gray-700">Response Time: Within 30 days</p>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              This Privacy Policy was last updated on {lastUpdated}. By using NEXT Career Intelligence, you acknowledge
              that you have read, understood, and agree to be bound by this Privacy Policy.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
