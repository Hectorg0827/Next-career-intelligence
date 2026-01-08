'use client';

import React, { useState, useRef } from 'react';
import { ResumeUploadState, validateResumeFile } from '@/types/resume';
import { ResumeStudioAPI } from '@/lib/api/premiumAPI';

interface ResumeUploadProps {
  userId: string;
  onSuccess?: (profileId: string) => void;
  initialFile?: File | null;
}

export default function ResumeUpload({ userId, onSuccess, initialFile }: ResumeUploadProps) {
  const [state, setState] = useState<ResumeUploadState>({
    step: 'upload',
    uploadProgress: 0,
  });
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle initial file from homepage
  React.useEffect(() => {
    if (initialFile) {
      handleFileSelect(initialFile);
      // Auto-trigger upload after a short delay for better UX
      setTimeout(() => {
        if (initialFile) {
          setState((prev) => ({ ...prev, file: initialFile }));
        }
      }, 500);
    }
  }, [initialFile]);

  // Handle file selection
  const handleFileSelect = (file: File) => {
    const validation = validateResumeFile(file);

    if (!validation.valid) {
      setState({
        ...state,
        error: validation.error,
      });
      return;
    }

    setState({
      ...state,
      file,
      error: undefined,
    });
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // Upload and parse resume
  const handleUpload = async () => {
    if (!state.file) return;

    setState({ ...state, step: 'parsing', uploadProgress: 0 });

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setState((prev) => ({
          ...prev,
          uploadProgress: Math.min(prev.uploadProgress + 10, 90),
        }));
      }, 200);

      const response = await ResumeStudioAPI.ingestResume({
        user_id: userId,
        file: state.file,
      });

      clearInterval(progressInterval);

      setState({
        ...state,
        step: 'review',
        uploadProgress: 100,
        parsedProfile: response.profile,
        openQuestions: response.open_questions,
      });
    } catch (error: any) {
      setState({
        ...state,
        step: 'upload',
        error: error.message || 'Failed to parse resume',
        uploadProgress: 0,
      });
    }
  };

  // Confirm and save profile
  const handleConfirm = () => {
    if (state.parsedProfile) {
      setState({ ...state, step: 'complete' });
      onSuccess?.(state.parsedProfile.id);
    }
  };

  // Restart upload
  const handleRestart = () => {
    setState({
      step: 'upload',
      uploadProgress: 0,
      file: undefined,
      parsedProfile: undefined,
      openQuestions: undefined,
      error: undefined,
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Upload Step */}
      {state.step === 'upload' && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Your Resume</h2>

          {/* Drag and Drop Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-gray-50 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="text-6xl mb-4">📄</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {state.file ? state.file.name : 'Drag and drop your resume here'}
            </h3>
            <p className="text-gray-600 mb-6">or</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Browse Files
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => {
                const files = e.target.files;
                if (files && files.length > 0) {
                  handleFileSelect(files[0]);
                }
              }}
              className="hidden"
            />
            <p className="text-sm text-gray-500 mt-4">
              Supported formats: PDF, DOCX, TXT (Max 10MB)
            </p>
          </div>

          {/* Error Message */}
          {state.error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">❌ {state.error}</p>
            </div>
          )}

          {/* Upload Button */}
          {state.file && !state.error && (
            <div className="mt-6 flex gap-4">
              <button
                onClick={handleUpload}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Upload and Parse Resume
              </button>
              <button
                onClick={handleRestart}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      )}

      {/* Parsing Step */}
      {state.step === 'parsing' && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-600 mb-6"></div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Parsing Your Resume...</h2>
          <p className="text-gray-600 mb-6">AI is extracting information from your resume</p>

          {/* Progress Bar */}
          <div className="max-w-md mx-auto">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${state.uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">{state.uploadProgress}%</p>
          </div>
        </div>
      )}

      {/* Review Step */}
      {state.step === 'review' && state.parsedProfile && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Review Parsed Profile</h2>
          <p className="text-gray-600 mb-6">
            Please review the information we extracted from your resume
          </p>

          {/* Profile Preview */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            {/* Personal Info */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Personal Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Name:</span>
                  <span className="ml-2 font-medium">{state.parsedProfile.profile_data.personal_info.full_name}</span>
                </div>
                <div>
                  <span className="text-gray-600">Email:</span>
                  <span className="ml-2 font-medium">{state.parsedProfile.profile_data.personal_info.email}</span>
                </div>
                {state.parsedProfile.profile_data.personal_info.phone && (
                  <div>
                    <span className="text-gray-600">Phone:</span>
                    <span className="ml-2 font-medium">{state.parsedProfile.profile_data.personal_info.phone}</span>
                  </div>
                )}
                {state.parsedProfile.profile_data.personal_info.location_city && (
                  <div>
                    <span className="text-gray-600">Location:</span>
                    <span className="ml-2 font-medium">
                      {state.parsedProfile.profile_data.personal_info.location_city},{' '}
                      {state.parsedProfile.profile_data.personal_info.location_state}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Skills */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Skills</h3>
              <div className="flex flex-wrap gap-2">
                {state.parsedProfile.profile_data.skills.hard.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Work History */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Work History</h3>
              <div className="space-y-4">
                {state.parsedProfile.profile_data.work_history.slice(0, 2).map((work, idx) => (
                  <div key={idx} className="border-l-2 border-blue-600 pl-4">
                    <h4 className="font-medium text-gray-900">{work.title}</h4>
                    <p className="text-sm text-gray-600">{work.company}</p>
                    <p className="text-xs text-gray-500">
                      {work.start_date} - {work.end_date || 'Present'}
                    </p>
                  </div>
                ))}
                {state.parsedProfile.profile_data.work_history.length > 2 && (
                  <p className="text-sm text-gray-600">
                    +{state.parsedProfile.profile_data.work_history.length - 2} more positions
                  </p>
                )}
              </div>
            </div>

            {/* Education */}
            {state.parsedProfile.profile_data.education.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Education</h3>
                <div className="space-y-2">
                  {state.parsedProfile.profile_data.education.map((edu, idx) => (
                    <div key={idx}>
                      <p className="font-medium text-gray-900">
                        {edu.degree} in {edu.field_of_study}
                      </p>
                      <p className="text-sm text-gray-600">{edu.institution}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Open Questions */}
          {state.openQuestions && state.openQuestions.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-yellow-900 mb-2">
                ❓ We have some questions to improve your profile:
              </h3>
              <ul className="list-disc list-inside text-sm text-yellow-800 space-y-1">
                {state.openQuestions.map((question, idx) => (
                  <li key={idx}>{question}</li>
                ))}
              </ul>
              <p className="text-xs text-yellow-700 mt-2">
                You can answer these later in your profile settings
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={handleConfirm}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Looks Good! Create Profile
            </button>
            <button
              onClick={handleRestart}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Upload Different File
            </button>
          </div>
        </div>
      )}

      {/* Complete Step */}
      {state.step === 'complete' && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Created!</h2>
          <p className="text-gray-600 mb-6">
            Your career profile has been successfully created and is now your Single Source of Truth
          </p>
          <button
            onClick={() => onSuccess?.(state.parsedProfile!.id)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            View My Profile
          </button>
        </div>
      )}
    </div>
  );
}
