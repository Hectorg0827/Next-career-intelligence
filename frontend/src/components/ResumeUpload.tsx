'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileText, X, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import { resumeApi } from '@/lib/api';

interface ResumeUploadProps {
    onUploadStart?: () => void;
    onUploadComplete?: (jobTitle: string) => void;
    onError?: (error: string) => void;
}

export default function ResumeUpload({ onUploadStart, onUploadComplete, onError }: ResumeUploadProps) {
    const router = useRouter();
    const [isDragOver, setIsDragOver] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);

    const processFile = async (file: File) => {
        // Validate file type
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png', 'image/jpeg'];
        if (!validTypes.includes(file.type)) {
            setUploadError('Please upload a PDF, DOCX, or Image file.');
            return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            setUploadError('File size must be under 10MB.');
            return;
        }

        try {
            setIsUploading(true);
            setUploadError(null);
            onUploadStart?.();

            // Upload and process resume
            const response = await resumeApi.uploadResume(file);

            let detectedJobTitle = '';

            // Try to extract job title from response if available
            // @ts-ignore - API response type might be partial or we access deeply
            if (response?.profile_data?.work_history?.length > 0) {
                // @ts-ignore
                const latestJob = response.profile_data.work_history.find((j: any) => j.is_current) || response.profile_data.work_history[0];
                if (latestJob) {
                    detectedJobTitle = latestJob.title;
                }
            }

            // If not in response, try fetching profile as a fallback
            if (!detectedJobTitle) {
                try {
                    const profile = await resumeApi.getResumeProfile();
                    const latestJob = profile.profile_data.work_history.find(j => j.is_current) || profile.profile_data.work_history[0];
                    if (latestJob) {
                        detectedJobTitle = latestJob.title;
                    }
                } catch (err) {
                    console.warn('Could not fetch parsed profile immediately', err);
                }
            }

            if (!detectedJobTitle) {
                // Fallback title
                detectedJobTitle = "Professional";
            }

            onUploadComplete?.(detectedJobTitle);

        } catch (err) {
            console.error('Upload failed:', err);
            const msg = err instanceof Error ? err.message : 'Upload failed. Please try again.';
            setUploadError(msg);
            onError?.(msg);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            processFile(files[0]);
        }
    };

    return (
        <div
            className={`relative group rounded-xl border-2 border-dashed transition-all duration-300 ${isDragOver
                ? 'border-nci-primary bg-nci-primary/10'
                : 'border-white/10 hover:border-white/20 hover:bg-white/5'
                }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <input
                type="file"
                id="resume-upload"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
                onChange={handleFileSelect}
                disabled={isUploading}
            />

            <div className="p-8 flex flex-col items-center justify-center text-center">
                {isUploading ? (
                    <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                        <Loader2 className="w-10 h-10 text-nci-primary animate-spin mb-4" />
                        <p className="text-white font-medium">Analyzing your resume...</p>
                        <p className="text-sm text-g-400 mt-2">Extracting career DNA</p>
                    </div>
                ) : uploadError ? (
                    <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
                            <AlertCircle className="w-6 h-6 text-red-400" />
                        </div>
                        <p className="text-red-400 font-medium mb-1">Upload Failed</p>
                        <p className="text-sm text-g-400 mb-4 max-w-xs">{uploadError}</p>
                        <button
                            className="text-white text-sm underline hover:text-nci-primary relative z-20"
                            onClick={(e) => {
                                e.stopPropagation();
                                e.preventDefault();
                                setUploadError(null);
                            }}
                        >
                            Try Again
                        </button>
                    </div>
                ) : (
                    <>
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 transition-colors ${isDragOver ? 'bg-nci-primary text-white' : 'bg-white/5 text-g-400 group-hover:text-white'}`}>
                            <Upload className="w-6 h-6" />
                        </div>
                        <h3 className="text-white font-semibold mb-2">Upload Resume or CV</h3>
                        <p className="text-sm text-g-400 max-w-xs mx-auto mb-4">
                            Drag & drop or click to upload. <br />
                            <span className="text-xs opacity-70">Supports PDF, DOCX, PNG, JPG</span>
                        </p>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/5 text-[11px] font-medium text-g-400">
                            <Sparkles className="w-3 h-3 text-nci-amber" />
                            <span>Get 2x more accurate results</span>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
