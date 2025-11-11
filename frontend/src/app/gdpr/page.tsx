import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GDPR Compliance | NEXT Career Intelligence',
  description: 'GDPR compliance information for NEXT Career Intelligence Platform',
}

export default function GDPRPage() {
  const lastUpdated = 'November 10, 2025'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">GDPR Compliance</h1>
            <p className="text-gray-600">Last Updated: {lastUpdated}</p>
            <p className="text-lg text-gray-700 mt-4">
              General Data Protection Regulation (GDPR) Information for EU Users
            </p>
          </div>

          {/* Content */}
          <div className="prose prose-lg max-w-none">
            {/* Introduction */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your Rights Under GDPR</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you are located in the European Economic Area (EEA), you have specific data protection rights under the General
                Data Protection Regulation (GDPR). NEXT Career Intelligence is committed to complying with GDPR and respecting your
                data privacy rights.
              </p>
            </section>

            {/* Your Rights */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Your GDPR Rights</h2>

              <div className="space-y-6">
                {/* Right to Access */}
                <div className="bg-blue-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    🔍 Right to Access (Article 15)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right to request a copy of your personal data we hold. This includes:
                  </p>
                  <ul className="list-disc pl-6 mb-3 text-gray-700 space-y-1">
                    <li>Profile information and account details</li>
                    <li>Resume content and work history</li>
                    <li>Application tracking data</li>
                    <li>AI interaction history</li>
                    <li>Payment and subscription history</li>
                  </ul>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Visit your{' '}
                    <a href="/settings" className="text-blue-600 hover:underline">Account Settings</a> or email{' '}
                    <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a>
                  </p>
                  <p className="text-gray-700 mt-2">
                    <strong>Response time:</strong> Within 30 days (may be extended to 60 days for complex requests)
                  </p>
                </div>

                {/* Right to Rectification */}
                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    ✏️ Right to Rectification (Article 16)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right to correct inaccurate or incomplete personal data.
                  </p>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Update your information directly in your{' '}
                    <a href="/settings" className="text-blue-600 hover:underline">Account Settings</a> or contact support
                  </p>
                </div>

                {/* Right to Erasure */}
                <div className="bg-red-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    🗑️ Right to Erasure / "Right to be Forgotten" (Article 17)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right to request deletion of your personal data when:
                  </p>
                  <ul className="list-disc pl-6 mb-3 text-gray-700 space-y-1">
                    <li>The data is no longer necessary for the purposes it was collected</li>
                    <li>You withdraw consent and there's no other legal basis</li>
                    <li>You object to processing and there are no overriding legitimate grounds</li>
                    <li>The data has been unlawfully processed</li>
                  </ul>
                  <p className="text-gray-700 mb-3">
                    <strong>Exceptions:</strong> We may retain certain data when required by law (e.g., financial records for tax
                    purposes) or for legitimate interests (e.g., defending legal claims).
                  </p>
                  <p className="text-gray-700 mb-3">
                    <strong>Anonymized data:</strong> RFT training data is anonymized and cannot be linked back to you, so it cannot
                    be deleted under GDPR.
                  </p>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Visit{' '}
                    <a href="/settings" className="text-blue-600 hover:underline">Account Settings → Delete Account</a> or email{' '}
                    <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a>
                  </p>
                  <p className="text-gray-700 mt-2">
                    <strong>Timeline:</strong> Data deleted within 30 days
                  </p>
                </div>

                {/* Right to Restriction */}
                <div className="bg-yellow-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    ⏸️ Right to Restriction of Processing (Article 18)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right to request we limit how we use your data when:
                  </p>
                  <ul className="list-disc pl-6 mb-3 text-gray-700 space-y-1">
                    <li>You contest the accuracy of your data</li>
                    <li>Processing is unlawful but you don't want data deleted</li>
                    <li>We no longer need the data but you need it for legal claims</li>
                    <li>You've objected to processing and await verification of legitimate grounds</li>
                  </ul>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Email{' '}
                    <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a> with
                    specific restrictions requested
                  </p>
                </div>

                {/* Right to Data Portability */}
                <div className="bg-purple-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    📦 Right to Data Portability (Article 20)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right to receive your personal data in a structured, commonly used, machine-readable format (JSON) and
                    transmit it to another service.
                  </p>
                  <p className="text-gray-700 mb-3">
                    <strong>What's included:</strong>
                  </p>
                  <ul className="list-disc pl-6 mb-3 text-gray-700 space-y-1">
                    <li>Profile and account data</li>
                    <li>Resume content (original + tailored versions)</li>
                    <li>Application tracking history</li>
                    <li>Career goals and preferences</li>
                  </ul>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Visit{' '}
                    <a href="/settings" className="text-blue-600 hover:underline">Account Settings → Export Data</a> or email{' '}
                    <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a>
                  </p>
                  <p className="text-gray-700 mt-2">
                    <strong>Format:</strong> JSON file download
                  </p>
                </div>

                {/* Right to Object */}
                <div className="bg-orange-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    ⛔ Right to Object (Article 21)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right to object to processing of your personal data for:
                  </p>
                  <ul className="list-disc pl-6 mb-3 text-gray-700 space-y-1">
                    <li><strong>Direct marketing:</strong> You can opt-out of marketing emails at any time (unsubscribe link)</li>
                    <li><strong>Profiling:</strong> Object to automated decision-making based on your data</li>
                    <li><strong>Legitimate interests:</strong> Object to processing based on our legitimate interests</li>
                  </ul>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Email{' '}
                    <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a> or
                    update notification preferences in settings
                  </p>
                </div>

                {/* Rights Related to Automated Decision-Making */}
                <div className="bg-indigo-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    🤖 Rights Related to Automated Decision-Making and Profiling (Article 22)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    You have the right not to be subject to decisions based solely on automated processing, including profiling,
                    which produces legal effects or similarly significantly affects you.
                  </p>
                  <p className="text-gray-700 mb-3">
                    <strong>NEXT's AI Usage:</strong>
                  </p>
                  <ul className="list-disc pl-6 mb-3 text-gray-700 space-y-1">
                    <li>Our AI provides <strong>suggestions</strong>, not automated decisions</li>
                    <li>All final decisions (resume content, applications) are made by you</li>
                    <li>You can always request human review of AI recommendations</li>
                  </ul>
                </div>

                {/* Right to Withdraw Consent */}
                <div className="bg-pink-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    🚫 Right to Withdraw Consent (Article 7)
                  </h3>
                  <p className="text-gray-700 leading-relaxed mb-3">
                    Where we process your data based on consent, you can withdraw consent at any time. This does not affect the
                    lawfulness of processing before withdrawal.
                  </p>
                  <p className="text-gray-700">
                    <strong>How to exercise:</strong> Update preferences in{' '}
                    <a href="/settings" className="text-blue-600 hover:underline">Account Settings</a> or email privacy@nextcareer.ai
                  </p>
                </div>
              </div>
            </section>

            {/* Legal Basis for Processing */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Legal Basis for Processing Your Data</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Under GDPR, we must have a legal basis to process your personal data. We process your data based on:
              </p>
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Legal Basis</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Providing our Services (resume tailoring, job matching)</td>
                      <td className="border border-gray-300 px-4 py-2"><strong>Contract Performance</strong> (Article 6(1)(b))</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Payment processing, subscription management</td>
                      <td className="border border-gray-300 px-4 py-2"><strong>Contract Performance</strong> (Article 6(1)(b))</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Improving AI models (RFT training)</td>
                      <td className="border border-gray-300 px-4 py-2"><strong>Legitimate Interests</strong> (Article 6(1)(f))</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Analytics and platform improvement</td>
                      <td className="border border-gray-300 px-4 py-2"><strong>Legitimate Interests</strong> (Article 6(1)(f))</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Marketing communications (if you opt-in)</td>
                      <td className="border border-gray-300 px-4 py-2"><strong>Consent</strong> (Article 6(1)(a))</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2">Fraud prevention, security, legal obligations</td>
                      <td className="border border-gray-300 px-4 py-2"><strong>Legal Obligation</strong> (Article 6(1)(c))</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            {/* Data Transfers */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. International Data Transfers</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Your data may be transferred to and processed in countries outside the EEA, including the United States. We ensure
                adequate safeguards through:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>
                  <strong>Standard Contractual Clauses (SCCs):</strong> Approved by the European Commission for data transfers
                </li>
                <li>
                  <strong>Data Processing Agreements:</strong> Signed with all third-party vendors (Supabase, Google, Stripe)
                </li>
                <li>
                  <strong>Adequate Protection:</strong> Ensuring recipients provide adequate data protection
                </li>
              </ul>
            </section>

            {/* Data Retention */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Data Retention</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We retain your data only as long as necessary for the purposes described in our Privacy Policy:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Active accounts:</strong> Data retained while account is active</li>
                <li><strong>Deleted accounts:</strong> Most data deleted within 30 days</li>
                <li><strong>Billing records:</strong> Retained for 7 years (tax/legal requirements)</li>
                <li><strong>Anonymized RFT data:</strong> Retained indefinitely (cannot be linked to you)</li>
              </ul>
            </section>

            {/* How to Exercise Your Rights */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. How to Exercise Your Rights</h2>

              <div className="bg-blue-100 border-l-4 border-blue-500 p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">📧 Contact Us</h3>
                <p className="text-gray-700 mb-3">
                  To exercise any of your GDPR rights, please contact us:
                </p>
                <div className="text-gray-700 space-y-1">
                  <p><strong>Email:</strong> <a href="mailto:privacy@nextcareer.ai" className="text-blue-600 hover:underline">privacy@nextcareer.ai</a></p>
                  <p><strong>Subject Line:</strong> "GDPR Request - [Your Right]"</p>
                  <p><strong>Response Time:</strong> Within 30 days (may be extended to 60 days for complex requests)</p>
                </div>
              </div>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">Required Information</h3>
              <p className="text-gray-700 leading-relaxed mb-3">
                To verify your identity and process your request, please provide:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Full name</li>
                <li>Email address associated with your account</li>
                <li>Specific right you wish to exercise</li>
                <li>Any additional details to help locate your data</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">We Will:</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Confirm receipt of your request within 72 hours</li>
                <li>Verify your identity to prevent unauthorized data disclosure</li>
                <li>Respond to your request within 30 days (or explain any delay)</li>
                <li>Provide information free of charge (unless request is excessive)</li>
              </ul>
            </section>

            {/* Complaints */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Right to Lodge a Complaint</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you believe we have not handled your personal data properly, you have the right to lodge a complaint with your
                local data protection authority (DPA).
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>EU Data Protection Authorities:</strong>
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>
                  <strong>Find your DPA:</strong>{' '}
                  <a href="https://edpb.europa.eu/about-edpb/about-edpb/members_en" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    European Data Protection Board - List of Members
                  </a>
                </li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                We encourage you to contact us first (privacy@nextcareer.ai) so we can address your concerns directly.
              </p>
            </section>

            {/* Contact */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. Contact Information</h2>
              <div className="bg-gray-50 p-6 rounded-lg">
                <p className="text-gray-700 mb-2"><strong>NEXT Career Intelligence</strong></p>
                <p className="text-gray-700 mb-2"><strong>Data Protection Contact:</strong></p>
                <p className="text-gray-700 mb-2">Email: privacy@nextcareer.ai</p>
                <p className="text-gray-700 mb-2">Support: hello@nextcareer.ai</p>
                <p className="text-gray-700">Response Time: Within 30 days</p>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              This GDPR information page was last updated on {lastUpdated}. For complete privacy information, please review our{' '}
              <a href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</a>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
