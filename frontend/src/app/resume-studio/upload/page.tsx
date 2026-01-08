'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ResumeUpload from '@/components/resume-studio/ResumeUpload';

export default function UploadPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string>('dev_user_123');
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  useEffect(() => {
    // Only access localStorage on client side
    if (typeof window !== 'undefined') {
      setUserId(localStorage.getItem('userId') || 'dev_user_123');

      // Check for pending file upload from homepage
      const pendingUploadData = sessionStorage.getItem('pendingResumeUpload');
      if (pendingUploadData) {
        try {
          const fileData = JSON.parse(pendingUploadData);

          // Convert base64 back to File object
          const base64Content = fileData.content;
          const byteString = atob(base64Content.split(',')[1]);
          const mimeString = base64Content.split(',')[0].split(':')[1].split(';')[0];

          const ab = new ArrayBuffer(byteString.length);
          const ia = new Uint8Array(ab);
          for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
          }

          const blob = new Blob([ab], { type: mimeString });
          const file = new File([blob], fileData.name, {
            type: fileData.type,
            lastModified: fileData.lastModified,
          });

          setPendingFile(file);

          // Clear the sessionStorage
          sessionStorage.removeItem('pendingResumeUpload');
        } catch (error) {
          console.error('Failed to restore uploaded file:', error);
          sessionStorage.removeItem('pendingResumeUpload');
        }
      }
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
          initialFile={pendingFile}
        />
      </div>
    </div>
  );
}
