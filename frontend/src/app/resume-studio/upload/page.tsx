'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ResumeUpload from '@/components/resume-studio/ResumeUpload';

export default function UploadPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string>('dev_user_123');

  useEffect(() => {
    // Only access localStorage on client side
    if (typeof window !== 'undefined') {
      setUserId(localStorage.getItem('userId') || 'dev_user_123');
    }
  }, []);

  const handleSuccess = (profileId: string) => {
    // Redirect to profile page
    router.push(`/resume-studio/profile?id=${profileId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-5xl mx-auto px-4">
        <ResumeUpload
          userId={userId}
          onSuccess={handleSuccess}
        />
      </div>
    </div>
  );
}
