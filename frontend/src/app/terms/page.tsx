import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service | NEXT Career Intelligence',
  description: 'Terms of Service for NEXT Career Intelligence Platform',
}

export default function TermsOfServicePage() {
  const lastUpdated = 'November 10, 2025'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
            <p className="text-gray-600">Last Updated: {lastUpdated}</p>
          </div>

          {/* Content */}
          <div className="prose prose-lg max-w-none">
            {/* Introduction */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Welcome to NEXT Career Intelligence ("NEXT", "we", "us", or "our"). These Terms of Service ("Terms") govern your
                access to and use of our website, platform, and services (collectively, the "Services").
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                By accessing or using our Services, you agree to be bound by these Terms and our Privacy Policy. If you do not agree
                to these Terms, you may not use our Services.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Important:</strong> These Terms contain an arbitration clause and class action waiver (Section 14) that affect
                your legal rights. Please read carefully.
              </p>
            </section>

            {/* Eligibility */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Eligibility</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                You must be at least 18 years old to use our Services. By using NEXT, you represent and warrant that:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>You are at least 18 years of age</li>
                <li>You have the legal capacity to enter into these Terms</li>
                <li>You will provide accurate, current, and complete information</li>
                <li>You will not use the Services for any illegal or unauthorized purpose</li>
              </ul>
            </section>

            {/* Account Registration */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. Account Registration and Security</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">3.1 Account Creation</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                To access certain features, you must create an account. You agree to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Provide accurate and complete registration information</li>
                <li>Maintain and promptly update your account information</li>
                <li>Keep your password confidential</li>
                <li>Notify us immediately of any unauthorized account access</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">3.2 Account Responsibility</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You are solely responsible for all activity that occurs under your account. We are not liable for any loss or damage
                arising from unauthorized account use.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">3.3 One Account Per User</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You may only create one account. Multiple accounts for the same individual are prohibited.
              </p>
            </section>

            {/* Services Description */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Description of Services</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                NEXT provides AI-powered career intelligence services, including but not limited to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Resume Studio:</strong> Resume analysis, tailoring, and optimization</li>
                <li><strong>Job Marketplace:</strong> Job recommendations and application tracking</li>
                <li><strong>Career Coach:</strong> AI-powered career guidance and goal setting</li>
                <li><strong>Interviewer AI:</strong> Mock interviews and feedback</li>
                <li><strong>Career Health Score:</strong> Career vitality assessment and recommendations</li>
                <li><strong>Talent Graph:</strong> Skill gap analysis and career pathway discovery</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                We reserve the right to modify, suspend, or discontinue any feature at any time without notice.
              </p>
            </section>

            {/* Subscription Plans */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. Subscription Plans and Billing</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.1 Free and Paid Plans</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                NEXT offers both free and paid subscription plans:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Free Tier:</strong> Limited access to core features</li>
                <li><strong>Pro Plan:</strong> Full access to all features, priority support</li>
                <li><strong>Elite Plan:</strong> Advanced features, dedicated account manager</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.2 Payment Terms</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                By subscribing to a paid plan, you agree that:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Payments are processed securely via Stripe</li>
                <li>Subscriptions automatically renew unless canceled</li>
                <li>You authorize us to charge your payment method on each billing cycle</li>
                <li>Pricing is subject to change with 30 days' notice</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.3 Cancellation and Refunds</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You may cancel your subscription at any time. Upon cancellation:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>You will retain access until the end of your current billing period</li>
                <li>No refunds for partial billing periods</li>
                <li>You may resubscribe at any time</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Refund Policy:</strong> We offer a 7-day money-back guarantee for first-time subscribers. Contact
                hello@nextcareer.ai within 7 days of your initial purchase for a full refund.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">5.4 Failed Payments</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                If a payment fails, we will attempt to charge your payment method up to 3 times over 10 days. If payment remains
                unsuccessful, your account will be downgraded to the free tier.
              </p>
            </section>

            {/* Acceptable Use */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Acceptable Use Policy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                You agree NOT to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Violate any applicable laws or regulations</li>
                <li>Upload false, misleading, or fraudulent information</li>
                <li>Impersonate another person or entity</li>
                <li>Harass, abuse, or harm other users</li>
                <li>Distribute viruses, malware, or harmful code</li>
                <li>Attempt to gain unauthorized access to our systems</li>
                <li>Use automated tools (bots, scrapers) without permission</li>
                <li>Reverse engineer, decompile, or disassemble our software</li>
                <li>Resell, redistribute, or commercialize our Services</li>
                <li>Use our Services for spam or unsolicited marketing</li>
                <li>Submit content that infringes intellectual property rights</li>
                <li>Abuse our AI systems to generate harmful or illegal content</li>
              </ul>
            </section>

            {/* User Content */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. User Content and Intellectual Property</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">7.1 Your Content</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You retain ownership of all content you upload to NEXT (resumes, profile information, etc.). By submitting content,
                you grant us a non-exclusive, worldwide, royalty-free license to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Store, process, and display your content to provide our Services</li>
                <li>Use anonymized and aggregated data to improve our AI models</li>
                <li>Analyze usage patterns to enhance platform features</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Important:</strong> We will never share your resume or personal information with third parties for marketing
                purposes without your explicit consent.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">7.2 AI-Generated Content</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Content generated by our AI (resume bullets, interview answers, career advice) is provided as suggestions. You are
                responsible for reviewing, editing, and verifying all AI-generated content before use.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>No Guarantee of Outcomes:</strong> We do not guarantee that using our AI suggestions will result in job
                offers, interviews, or career advancement.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">7.3 Our Intellectual Property</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                All rights, title, and interest in NEXT's platform, including our AI models, algorithms, trademarks, logos, and
                proprietary technology, remain our exclusive property. These Terms do not grant you any intellectual property rights
                except as expressly stated.
              </p>
            </section>

            {/* AI Services Disclaimer */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">8. AI Services and Limitations</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Our AI-powered services are designed to assist with career-related tasks. However:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>AI suggestions are not professional career counseling or legal advice</li>
                <li>AI-generated content may contain errors or inaccuracies</li>
                <li>AI recommendations are based on patterns and may not apply to your situation</li>
                <li>You should independently verify all AI-generated content</li>
                <li>We are not responsible for decisions you make based on AI suggestions</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Human Review Recommended:</strong> Always review AI-generated resumes and interview answers before submission.
              </p>
            </section>

            {/* Privacy and Data */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">9. Privacy and Data Protection</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Your privacy is important to us. Please review our <a href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</a> to
                understand how we collect, use, and protect your information.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Key points:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>We do NOT sell your personal information</li>
                <li>We use industry-standard encryption and security measures</li>
                <li>You can request data export or deletion at any time</li>
                <li>We comply with GDPR, CCPA, and other privacy regulations</li>
              </ul>
            </section>

            {/* Disclaimers */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">10. Disclaimers and Limitations of Liability</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">10.1 Service "AS IS"</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                NEXT IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
                LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">10.2 No Employment Guarantee</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We do not guarantee that using NEXT will result in job offers, interviews, career advancement, or any specific outcome.
                Career success depends on many factors beyond our control.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">10.3 Third-Party Services</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We integrate with third-party services (job boards, payment processors). We are not responsible for the availability,
                accuracy, or content of third-party services.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">10.4 Limitation of Liability</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, NEXT SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL,
                OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, USE, OR GOODWILL, ARISING FROM:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Your use or inability to use our Services</li>
                <li>Errors or inaccuracies in AI-generated content</li>
                <li>Unauthorized access to your account</li>
                <li>Service interruptions or technical issues</li>
                <li>Third-party conduct or content</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID US IN THE PAST 12 MONTHS, OR $100, WHICHEVER IS GREATER.
              </p>
            </section>

            {/* Indemnification */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">11. Indemnification</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                You agree to indemnify, defend, and hold harmless NEXT, its affiliates, officers, directors, employees, and agents from
                any claims, liabilities, damages, losses, costs, or expenses (including legal fees) arising from:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Your use or misuse of our Services</li>
                <li>Your violation of these Terms</li>
                <li>Your violation of any third-party rights</li>
                <li>Content you submit or actions you take on NEXT</li>
              </ul>
            </section>

            {/* Termination */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">12. Termination</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">12.1 By You</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You may terminate your account at any time by contacting hello@nextcareer.ai or using the account deletion feature in
                your settings.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">12.2 By Us</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may suspend or terminate your account immediately if you:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Violate these Terms or our Acceptable Use Policy</li>
                <li>Engage in fraudulent or illegal activity</li>
                <li>Abuse our AI systems or platform resources</li>
                <li>Fail to pay subscription fees (after 3 failed attempts)</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                Upon termination, your right to use our Services ceases immediately. Data retention is governed by our Privacy Policy.
              </p>
            </section>

            {/* Changes to Terms */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">13. Changes to Terms</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may modify these Terms at any time. Changes will be posted on this page with an updated "Last Updated" date. For
                material changes, we will notify you via email or prominent notice on our platform at least 30 days in advance.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Your continued use of NEXT after changes take effect constitutes acceptance of the updated Terms. If you do not agree,
                you must stop using our Services.
              </p>
            </section>

            {/* Dispute Resolution */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">14. Dispute Resolution and Arbitration</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">14.1 Informal Resolution</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Before filing a claim, you agree to contact us at legal@nextcareer.ai to attempt informal resolution. We will try to
                resolve disputes within 60 days.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">14.2 Binding Arbitration</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                If informal resolution fails, you agree that any dispute shall be resolved through binding arbitration administered by
                the American Arbitration Association (AAA) under its Consumer Arbitration Rules.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Key terms:</strong>
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Arbitration is individual (no class actions or class arbitrations)</li>
                <li>Arbitrator's decision is binding and final</li>
                <li>Limited discovery rights</li>
                <li>We will pay arbitration fees for claims under $10,000</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">14.3 Class Action Waiver</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                YOU AGREE THAT ALL CLAIMS MUST BE BROUGHT IN YOUR INDIVIDUAL CAPACITY AND NOT AS A PLAINTIFF OR CLASS MEMBER IN ANY
                CLASS, COLLECTIVE, OR REPRESENTATIVE ACTION.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">14.4 Exceptions</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Either party may seek injunctive relief in court for intellectual property violations or data security breaches.
              </p>
            </section>

            {/* General Provisions */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">15. General Provisions</h2>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">15.1 Governing Law</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                These Terms are governed by the laws of the State of California, United States, without regard to conflict of law
                principles.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">15.2 Entire Agreement</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                These Terms, together with our Privacy Policy, constitute the entire agreement between you and NEXT.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">15.3 Severability</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                If any provision of these Terms is found invalid or unenforceable, the remaining provisions remain in full effect.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">15.4 No Waiver</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Our failure to enforce any provision does not waive our right to enforce it later.
              </p>

              <h3 className="text-xl font-semibold text-gray-700 mb-3">15.5 Assignment</h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                You may not assign or transfer these Terms. We may assign these Terms to any affiliate or successor.
              </p>
            </section>

            {/* Contact */}
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">16. Contact Information</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you have questions about these Terms, please contact us:
              </p>
              <div className="bg-gray-50 p-6 rounded-lg">
                <p className="text-gray-700 mb-2"><strong>NEXT Career Intelligence</strong></p>
                <p className="text-gray-700 mb-2">Email: legal@nextcareer.ai</p>
                <p className="text-gray-700 mb-2">Support: hello@nextcareer.ai</p>
                <p className="text-gray-700">Response Time: Within 3-5 business days</p>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              By using NEXT Career Intelligence, you acknowledge that you have read, understood, and agree to be bound by these
              Terms of Service. Last updated: {lastUpdated}.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
