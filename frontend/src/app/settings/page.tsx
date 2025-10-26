'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  User, Mail, Lock, Bell, Globe, Trash2, Download, 
  Check, X, AlertCircle, Loader2, Save, Camera, Shield
} from 'lucide-react';
import { auth } from '@/lib/firebase';
import { updateProfile, updateEmail, updatePassword, deleteUser } from 'firebase/auth';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Personal Info State
  const [personalInfo, setPersonalInfo] = useState({
    displayName: '',
    email: '',
    phoneNumber: ''
  });

  // Password State
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Preferences State
  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    jobAlerts: true,
    newsletter: false,
    weeklyDigest: true
  });

  // Delete Account State
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  useEffect(() => {
    const { currentUser } = auth;
    if (!currentUser) {
      router.push('/auth/login');
      return;
    }

    setUser(currentUser);
    setPersonalInfo({
      displayName: currentUser.displayName || '',
      email: currentUser.email || '',
      phoneNumber: currentUser.phoneNumber || ''
    });
  }, [router]);

  const handleUpdatePersonalInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaveSuccess('');
    setLoading(true);

    try {
      if (!user) throw new Error('No user logged in');

      // Update display name
      if (personalInfo.displayName !== user.displayName) {
        await updateProfile(user, {
          displayName: personalInfo.displayName
        });
      }

      // Update email (requires re-authentication in production)
      if (personalInfo.email !== user.email) {
        await updateEmail(user, personalInfo.email);
      }

      setSaveSuccess('Profile updated successfully!');
      setTimeout(() => setSaveSuccess(''), 3000);
    } catch (err: any) {
      console.error('Update error:', err);
      if (err.code === 'auth/requires-recent-login') {
        setError('Please log out and log back in to update your email.');
      } else if (err.code === 'auth/email-already-in-use') {
        setError('This email is already in use.');
      } else {
        setError(err.message || 'Failed to update profile.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaveSuccess('');

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match.');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);

    try {
      if (!user) throw new Error('No user logged in');

      await updatePassword(user, passwordData.newPassword);

      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });

      setSaveSuccess('Password changed successfully!');
      setTimeout(() => setSaveSuccess(''), 3000);
    } catch (err: any) {
      console.error('Password error:', err);
      if (err.code === 'auth/requires-recent-login') {
        setError('Please log out and log back in to change your password.');
      } else if (err.code === 'auth/weak-password') {
        setError('Password is too weak. Please use a stronger password.');
      } else {
        setError(err.message || 'Failed to change password.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePreferences = async () => {
    setError('');
    setSaveSuccess('');
    setLoading(true);

    try {
      // TODO: Save preferences to backend
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      setSaveSuccess('Preferences updated successfully!');
      setTimeout(() => setSaveSuccess(''), 3000);
    } catch (err: any) {
      setError('Failed to update preferences.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') {
      setError('Please type DELETE to confirm account deletion.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      if (!user) throw new Error('No user logged in');

      await deleteUser(user);
      router.push('/');
    } catch (err: any) {
      console.error('Delete error:', err);
      if (err.code === 'auth/requires-recent-login') {
        setError('Please log out and log back in to delete your account.');
      } else {
        setError(err.message || 'Failed to delete account.');
      }
      setLoading(false);
    }
  };

  const handleDownloadData = async () => {
    // TODO: Implement download data functionality
    alert('Data download will be implemented soon!');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Account Settings</h1>
          <p className="text-slate-400">Manage your account preferences and security</p>
        </div>

        {/* Success/Error Messages */}
        {saveSuccess && (
          <div className="mb-6 flex items-center gap-3 p-4 bg-green-500/20 border border-green-500/30 rounded-xl">
            <Check className="w-5 h-5 text-green-400" />
            <p className="text-green-200">{saveSuccess}</p>
          </div>
        )}

        {error && (
          <div className="mb-6 flex items-center gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Personal Information */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <User className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Personal Information</h2>
          </div>

          <form onSubmit={handleUpdatePersonalInfo} className="space-y-4">
            <div>
              <label className="block text-slate-300 font-medium mb-2">Full Name</label>
              <input
                type="text"
                value={personalInfo.displayName}
                onChange={(e) => setPersonalInfo({ ...personalInfo, displayName: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your full name"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-2">Email Address</label>
              <input
                type="email"
                value={personalInfo.email}
                onChange={(e) => setPersonalInfo({ ...personalInfo, email: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
              />
              <p className="text-slate-400 text-sm mt-1">
                Changing your email will require verification
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Changes
                </>
              )}
            </button>
          </form>
        </div>

        {/* Password & Security */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <Lock className="w-6 h-6 text-gold-hover" />
            <h2 className="text-2xl font-bold text-white">Password & Security</h2>
          </div>

          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-slate-300 font-medium mb-2">Current Password</label>
              <input
                type="password"
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-royal-blue"
                placeholder="Enter current password"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-2">New Password</label>
              <input
                type="password"
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-royal-blue"
                placeholder="Enter new password"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-2">Confirm New Password</label>
              <input
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-royal-blue"
                placeholder="Confirm new password"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !passwordData.currentPassword || !passwordData.newPassword}
              className="flex items-center gap-2 px-6 py-3 bg-gold-primary hover:bg-gold-accent text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Changing...
                </>
              ) : (
                <>
                  <Shield className="w-5 h-5" />
                  Change Password
                </>
              )}
            </button>
          </form>
        </div>

        {/* Preferences */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <Bell className="w-6 h-6 text-green-400" />
            <h2 className="text-2xl font-bold text-white">Notification Preferences</h2>
          </div>

          <div className="space-y-4">
            {Object.entries(preferences).map(([key, value]) => (
              <label key={key} className="flex items-center justify-between cursor-pointer group">
                <span className="text-slate-300 group-hover:text-white transition-colors">
                  {key === 'emailNotifications' && 'Email Notifications'}
                  {key === 'jobAlerts' && 'Job Alerts'}
                  {key === 'newsletter' && 'Newsletter Subscription'}
                  {key === 'weeklyDigest' && 'Weekly Digest'}
                </span>
                <button
                  type="button"
                  onClick={() => setPreferences({ ...preferences, [key]: !value })}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    value ? 'bg-green-500' : 'bg-slate-600'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      value ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </label>
            ))}
          </div>

          <button
            onClick={handleUpdatePreferences}
            disabled={loading}
            className="mt-6 flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Save Preferences
              </>
            )}
          </button>
        </div>

        {/* Account Management */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Globe className="w-6 h-6 text-orange-400" />
            <h2 className="text-2xl font-bold text-white">Account Management</h2>
          </div>

          <div className="space-y-4">
            <button
              onClick={handleDownloadData}
              className="w-full flex items-center justify-between px-4 py-3 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-lg text-white transition-colors"
            >
              <span className="flex items-center gap-2">
                <Download className="w-5 h-5" />
                Download My Data
              </span>
            </button>

            <div className="pt-4 border-t border-slate-700">
              <button
                onClick={() => setShowDeleteConfirm(!showDeleteConfirm)}
                className="w-full flex items-center justify-between px-4 py-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Trash2 className="w-5 h-5" />
                  Delete Account
                </span>
              </button>

              {showDeleteConfirm && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <p className="text-red-300 mb-4">
                    This action cannot be undone. All your data will be permanently deleted.
                  </p>
                  <p className="text-slate-300 mb-2">
                    Type <strong>DELETE</strong> to confirm:
                  </p>
                  <input
                    type="text"
                    value={deleteConfirmText}
                    onChange={(e) => setDeleteConfirmText(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-700 border border-red-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500 mb-4"
                    placeholder="Type DELETE"
                  />
                  <div className="flex gap-3">
                    <button
                      onClick={handleDeleteAccount}
                      disabled={loading || deleteConfirmText !== 'DELETE'}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4" />
                          Delete Account
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => {
                        setShowDeleteConfirm(false);
                        setDeleteConfirmText('');
                      }}
                      className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
