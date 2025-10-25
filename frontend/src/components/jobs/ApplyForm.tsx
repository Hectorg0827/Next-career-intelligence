import React, { useState } from 'react';
import { useAuth } from '@/lib/firebase';
import { jobsApi } from '@/lib/api';

interface ApplyFormProps {
  jobId: string;
  onSuccess?: () => void;
}

export default function ApplyForm({ jobId, onSuccess }: ApplyFormProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user) {
      setError('Please log in to apply');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await jobsApi.applyToJob({
        job_id: jobId
      });

      setSuccess(true);
      if (onSuccess) {
        setTimeout(onSuccess, 2000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="text-center space-y-3">
        <div className="text-4xl">✅</div>
        <p className="text-gray-900 font-semibold">Application Submitted!</p>
        <p className="text-sm text-gray-600">We'll track this application for you.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors font-semibold disabled:cursor-not-allowed"
      >
        {loading ? 'Applying...' : 'Confirm Apply'}
      </button>

      <button
        type="button"
        onClick={onSuccess}
        className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
      >
        Cancel
      </button>
    </form>
  );
}
