'use client';

import { useRouter } from 'next/navigation';
import { XCircle, ArrowLeft, RefreshCcw } from 'lucide-react';

export default function CheckoutCancelPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Cancel Icon */}
        <div className="relative mb-8">
          <XCircle className="w-32 h-32 text-yellow-400 mx-auto" />
        </div>

        {/* Cancel Message */}
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
          Checkout Cancelled
        </h1>
        <p className="text-xl text-white/80 mb-8">
          No worries! Your subscription was not created.
        </p>

        {/* Information */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-xl font-bold text-white mb-4">What happened?</h2>
          <p className="text-white/70 mb-6">
            You cancelled the checkout process before completing your payment. No charges were made to your account.
          </p>

          <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
            <p className="text-blue-200 text-sm">
              <strong>Still interested in Pro?</strong> You can try again anytime. All your progress is saved!
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.push('/pricing')}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
          >
            <RefreshCcw className="w-5 h-5" />
            Try Again
          </button>
          
          <button
            onClick={() => router.push('/dashboard')}
            className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20 flex items-center justify-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
        </div>

        {/* Support */}
        <p className="text-white/50 text-sm mt-8">
          Questions? Contact us at <a href="mailto:support@nextcareer.ai" className="text-purple-400 hover:text-purple-300">support@nextcareer.ai</a>
        </p>
      </div>
    </div>
  );
}
