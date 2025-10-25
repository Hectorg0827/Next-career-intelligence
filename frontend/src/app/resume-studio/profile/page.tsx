'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import ProfileView from '@/components/resume-studio/ProfileView';
import { ResumeStudioAPI } from '@/lib/api/premiumAPI';
import { CareerProfile } from '@/types/resume';

export default function ProfilePage() {
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<CareerProfile | null>(null);

  // Fetch profile
  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setError(null);

      try {
        const userId = localStorage.getItem('userId') || 'dev_user_123';
        const profileData = await ResumeStudioAPI.getProfile(userId);
        setProfile(profileData.profile);
      } catch (err: any) {
        console.error('Failed to fetch profile:', err);
        setError(err.message || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // Handle edit section
  const handleEdit = (section: string) => {
    alert(`Edit ${section} functionality coming soon!`);
    // TODO: Open edit modal or navigate to edit page
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Career Profile</h1>
          <p className="text-gray-600">
            Single Source of Truth • Last updated {profile && new Date(profile.updated_at).toLocaleDateString()}
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gold-primary mb-4"></div>
            <p className="text-gray-600">Loading your profile...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 font-medium">❌ {error}</p>
            <p className="text-sm text-red-600 mt-2">
              Don't have a profile yet?{' '}
              <a href="/resume-studio/upload" className="underline font-semibold">
                Upload your resume
              </a>
            </p>
          </div>
        )}

        {/* Profile View */}
        {!loading && !error && profile && (
          <ProfileView profile={profile} onEdit={handleEdit} editable={true} />
        )}
      </div>
    </div>
  );
}
