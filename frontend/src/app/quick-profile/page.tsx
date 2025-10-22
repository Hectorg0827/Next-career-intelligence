'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { Loader2, User, Briefcase, GraduationCap, Award, Save, ArrowLeft, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { NextLogo } from '@/components/branding/NextLogo';

export default function QuickProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    current_job_title: '',
    years_experience: '',
    skills: '',
    education: '',
    career_goals: ''
  });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
    
    // Pre-fill email if available
    if (user && user.email) {
      setFormData(prev => ({ ...prev, email: user.email as string }));
    }
  }, [user, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    try {
      setIsLoading(true);

      // Create profile in Supabase
      const { default: { createClient } } = await import('@supabase/supabase-js');
      const supabase = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
      );

      // Prepare profile data
      const profileData = {
        user_id: user.uid,
        profile_data: {
          personal_info: {
            full_name: formData.full_name,
            email: formData.email,
            phone: formData.phone
          },
          professional_summary: {
            current_role: formData.current_job_title,
            years_experience: parseInt(formData.years_experience) || 0,
            career_goals: formData.career_goals
          },
          skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean),
          education: formData.education ? [{
            degree: formData.education,
            institution: 'Not specified',
            year: new Date().getFullYear()
          }] : [],
          work_experience: formData.current_job_title ? [{
            title: formData.current_job_title,
            company: 'Current Position',
            duration: `${formData.years_experience} years`,
            description: 'Manually entered profile'
          }] : []
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Check if profile exists
      const { data: existingProfile } = await supabase
        .from('career_profiles')
        .select('id')
        .eq('user_id', user.uid)
        .single();

      if (existingProfile) {
        // Update existing profile
        const { error } = await supabase
          .from('career_profiles')
          .update({
            profile_data: profileData.profile_data,
            updated_at: new Date().toISOString()
          })
          .eq('user_id', user.uid);

        if (error) throw error;
        toast.success('Profile updated successfully!');
      } else {
        // Insert new profile
        const { error } = await supabase
          .from('career_profiles')
          .insert([profileData]);

        if (error) throw error;
        toast.success('Profile created successfully!');
      }

      // Redirect to Voice Coach
      setTimeout(() => {
        router.push('/voice-coach');
      }, 1500);

    } catch (error: any) {
      console.error('Profile creation error:', error);
      toast.error('Failed to create profile: ' + (error.message || 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-next-bg-light p-4">
      <div className="max-w-3xl mx-auto py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-next-royal-blue to-next-gold rounded-full flex items-center justify-center">
              <User className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-next-deep-blue font-heading">Quick Profile Setup</h1>
              <p className="text-sm text-next-text-muted font-body">Create your career profile to use Voice Coach</p>
            </div>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              💡 <strong>Quick Setup:</strong> Fill in basic information below to start using the AI Voice Coach. 
              You can always add more details later in Resume Studio.
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-6 space-y-6">
          {/* Personal Information */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-semibold text-next-deep-blue font-heading">Personal Information</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                  Phone (Optional)
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>
          </div>

          {/* Professional Information */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Briefcase className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-semibold text-next-deep-blue font-heading">Professional Background</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                  Current Job Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="current_job_title"
                  value={formData.current_job_title}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                  placeholder="e.g., Software Engineer, Teacher, Marketing Manager"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                  Years of Experience <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="years_experience"
                  value={formData.years_experience}
                  onChange={handleChange}
                  required
                  min="0"
                  max="50"
                  className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                  placeholder="5"
                />
              </div>
            </div>
          </div>

          {/* Skills */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Award className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-semibold text-next-deep-blue font-heading">Skills</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                Your Skills <span className="text-red-500">*</span>
              </label>
              <textarea
                name="skills"
                value={formData.skills}
                onChange={handleChange}
                required
                rows={3}
                className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                placeholder="e.g., Python, JavaScript, Project Management, Communication (separate with commas)"
              />
              <p className="text-xs text-gray-500 mt-1">Separate skills with commas</p>
            </div>
          </div>

          {/* Education */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <GraduationCap className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-semibold text-next-deep-blue font-heading">Education</h2>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
                Highest Education Level (Optional)
              </label>
              <input
                type="text"
                name="education"
                value={formData.education}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                placeholder="e.g., Bachelor's in Computer Science, High School Diploma"
              />
            </div>
          </div>

          {/* Career Goals */}
          <div>
            <label className="block text-sm font-medium text-next-text-muted font-body mb-1">
              Career Goals (Optional)
            </label>
            <textarea
              name="career_goals"
              value={formData.career_goals}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-next-text-muted/30 rounded-lg focus:ring-2 focus:ring-next-gold focus:border-next-gold"
              placeholder="What are your career aspirations? e.g., Transition to tech, Get promoted to senior role, Start my own business"
            />
          </div>

          {/* Submit Button */}
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-next-gold disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating Profile...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Create Profile & Start Voice Coach
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => router.push('/dashboard')}
              className="px-6 py-3 border border-next-text-muted/30 text-next-text-muted font-body rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>

          <p className="text-xs text-gray-500 text-center pt-2">
            By creating a profile, you agree to our Terms of Service and Privacy Policy
          </p>
        </form>
      </div>
    </div>
  );
}
