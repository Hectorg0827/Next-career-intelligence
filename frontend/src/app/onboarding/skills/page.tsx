'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Upload, MessageSquare, GraduationCap, Plus, X, Check } from 'lucide-react';

interface Skill {
    name: string;
    proficiency_level?: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT';
}

interface Education {
    degree: string;
    institution: string;
    field_of_study?: string;
    start_year?: number;
    end_year?: number;
}

export default function SkillIngestPage() {
    const router = useRouter();
    const [step, setStep] = useState(0);
    const [skills, setSkills] = useState<Skill[]>([]);
    const [newSkillName, setNewSkillName] = useState('');
    const [resumeText, setResumeText] = useState('');
    const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([
        { role: 'assistant', content: "Hi! I'm your AI coach. Let's map your skills together. Tell me about a project you're proud of." }
    ]);
    const [userMessage, setUserMessage] = useState('');
    const [education, setEducation] = useState<Education>({
        degree: '',
        institution: '',
        field_of_study: '',
    });
    const [isLoading, setIsLoading] = useState(false);

    const steps = [
        { id: 0, title: 'Manual Skills', icon: Plus },
        { id: 1, title: 'Resume Upload', icon: Upload },
        { id: 2, title: 'AI Conversation', icon: MessageSquare },
        { id: 3, title: 'Education', icon: GraduationCap },
    ];

    const addManualSkill = () => {
        if (newSkillName.trim()) {
            setSkills([...skills, { name: newSkillName.trim(), proficiency_level: 'INTERMEDIATE' }]);
            setNewSkillName('');
        }
    };

    const removeSkill = (index: number) => {
        setSkills(skills.filter((_, i) => i !== index));
    };

    const handleResumeUpload = async () => {
        if (!resumeText.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/profile/skills/from-resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume_text: resumeText }),
            });

            if (response.ok) {
                const data = await response.json();
                setSkills([...skills, ...data.skills.map((s: any) => ({ name: s.name, proficiency_level: s.proficiency_level }))]);
            }
        } catch (error) {
            console.error('Resume upload failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const sendChatMessage = async () => {
        if (!userMessage.trim()) return;

        const newMessages = [...chatMessages, { role: 'user', content: userMessage }];
        setChatMessages(newMessages);
        setUserMessage('');

        setIsLoading(true);
        try {
            const response = await fetch('/api/profile/skills/from-conversation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ conversation_transcript: userMessage }),
            });

            if (response.ok) {
                const data = await response.json();
                setChatMessages([...newMessages, {
                    role: 'assistant',
                    content: `Great! I extracted ${data.skills.length} skills from what you shared.`
                }]);
                setSkills([...skills, ...data.skills.map((s: any) => ({ name: s.name, proficiency_level: s.proficiency_level }))]);
            }
        } catch (error) {
            console.error('Conversation extraction failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const saveEducation = async () => {
        setIsLoading(true);
        try {
            await fetch('/api/profile/education', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(education),
            });
        } catch (error) {
            console.error('Education save failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const finishOnboarding = async () => {
        await saveEducation();
        router.push('/dashboard');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-12 px-4">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-full mb-4">
                        <Sparkles className="w-4 h-4" />
                        <span className="text-sm font-medium">AI-Powered Skill Mapping</span>
                    </div>
                    <h1 className="text-4xl font-bold text-slate-900 mb-3">
                        Let's Build Your Skill Profile
                    </h1>
                    <p className="text-lg text-slate-600">
                        We'll use multiple methods to create a comprehensive map of your abilities
                    </p>
                </motion.div>

                {/* Step Progress */}
                <div className="flex justify-center gap-3 mb-12">
                    {steps.map((s, i) => (
                        <button
                            key={s.id}
                            onClick={() => setStep(s.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${step === s.id
                                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105'
                                    : 'bg-white text-slate-600 hover:bg-slate-50'
                                }`}
                        >
                            <s.icon className="w-4 h-4" />
                            <span className="text-sm font-medium hidden sm:inline">{s.title}</span>
                        </button>
                    ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Content */}
                    <div className="lg:col-span-2">
                        <AnimatePresence mode="wait">
                            {step === 0 && (
                                <motion.div
                                    key="manual"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="bg-white rounded-2xl shadow-xl p-8"
                                >
                                    <h2 className="text-2xl font-bold text-slate-900 mb-4">Add Skills Manually</h2>
                                    <p className="text-slate-600 mb-6">Type in your key skills and we'll organize them</p>

                                    <div className="flex gap-3 mb-6">
                                        <input
                                            type="text"
                                            value={newSkillName}
                                            onChange={(e) => setNewSkillName(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && addManualSkill()}
                                            placeholder="e.g., Python, Project Management, SQL..."
                                            className="flex-1 px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none"
                                        />
                                        <button
                                            onClick={addManualSkill}
                                            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
                                        >
                                            Add
                                        </button>
                                    </div>

                                    <div className="flex flex-wrap gap-2">
                                        {skills.map((skill, i) => (
                                            <motion.div
                                                key={i}
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                className="flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 px-4 py-2 rounded-full border border-blue-200"
                                            >
                                                <span className="font-medium">{skill.name}</span>
                                                <button onClick={() => removeSkill(i)} className="hover:bg-blue-200 rounded-full p-1">
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}

                            {step === 1 && (
                                <motion.div
                                    key="resume"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="bg-white rounded-2xl shadow-xl p-8"
                                >
                                    <h2 className="text-2xl font-bold text-slate-900 mb-4">Upload Resume</h2>
                                    <p className="text-slate-600 mb-6">Paste your resume text and we'll extract skills automatically</p>

                                    <textarea
                                        value={resumeText}
                                        onChange={(e) => setResumeText(e.target.value)}
                                        placeholder="Paste your resume text here..."
                                        className="w-full h-64 px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none mb-4"
                                    />

                                    <button
                                        onClick={handleResumeUpload}
                                        disabled={isLoading}
                                        className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all disabled:opacity-50"
                                    >
                                        {isLoading ? 'Extracting...' : 'Extract Skills from Resume'}
                                    </button>
                                </motion.div>
                            )}

                            {step === 2 && (
                                <motion.div
                                    key="chat"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="bg-white rounded-2xl shadow-xl p-8"
                                >
                                    <h2 className="text-2xl font-bold text-slate-900 mb-4">Chat with AI Coach</h2>
                                    <p className="text-slate-600 mb-6">Share your experiences and I'll identify your skills</p>

                                    <div className="h-96 overflow-y-auto mb-4 p-4 bg-slate-50 rounded-xl">
                                        {chatMessages.map((msg, i) => (
                                            <div key={i} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                                                <div
                                                    className={`inline-block px-4 py-2 rounded-2xl ${msg.role === 'user'
                                                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                                                            : 'bg-white text-slate-800 shadow-sm'
                                                        }`}
                                                >
                                                    {msg.content}
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="flex gap-3">
                                        <input
                                            type="text"
                                            value={userMessage}
                                            onChange={(e) => setUserMessage(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                                            placeholder="Type your message..."
                                            className="flex-1 px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none"
                                        />
                                        <button
                                            onClick={sendChatMessage}
                                            disabled={isLoading}
                                            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
                                        >
                                            Send
                                        </button>
                                    </div>
                                </motion.div>
                            )}

                            {step === 3 && (
                                <motion.div
                                    key="education"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="bg-white rounded-2xl shadow-xl p-8"
                                >
                                    <h2 className="text-2xl font-bold text-slate-900 mb-4">Education</h2>
                                    <p className="text-slate-600 mb-6">Add your educational background</p>

                                    <div className="space-y-4 mb-6">
                                        <input
                                            type="text"
                                            value={education.degree}
                                            onChange={(e) => setEducation({ ...education, degree: e.target.value })}
                                            placeholder="Degree (e.g., Bachelor of Science)"
                                            className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none"
                                        />
                                        <input
                                            type="text"
                                            value={education.institution}
                                            onChange={(e) => setEducation({ ...education, institution: e.target.value })}
                                            placeholder="Institution"
                                            className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none"
                                        />
                                        <input
                                            type="text"
                                            value={education.field_of_study || ''}
                                            onChange={(e) => setEducation({ ...education, field_of_study: e.target.value })}
                                            placeholder="Field of Study (optional)"
                                            className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none"
                                        />
                                    </div>

                                    <button
                                        onClick={finishOnboarding}
                                        disabled={isLoading}
                                        className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-medium hover:shadow-lg transition-all flex items-center justify-center gap-2"
                                    >
                                        <Check className="w-5 h-5" />
                                        Complete Setup & Go to Dashboard
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Skill Preview Sidebar */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-6 bg-white rounded-2xl shadow-xl p-6">
                            <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-blue-600" />
                                Your Skill Profile
                            </h3>
                            <p className="text-sm text-slate-600 mb-4">
                                {skills.length} skill{skills.length !== 1 ? 's' : ''} mapped
                            </p>

                            <div className="space-y-2 max-h-96 overflow-y-auto">
                                {skills.length === 0 ? (
                                    <p className="text-sm text-slate-400 italic">No skills added yet. Start by adding some!</p>
                                ) : (
                                    skills.map((skill, i) => (
                                        <div
                                            key={i}
                                            className="flex items-center justify-between p-3 bg-gradient-to-r from-slate-50 to-blue-50 rounded-lg border border-slate-200"
                                        >
                                            <span className="font-medium text-slate-800 text-sm">{skill.name}</span>
                                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                                                {skill.proficiency_level || 'INTERMEDIATE'}
                                            </span>
                                        </div>
                                    ))
                                )}
                            </div>

                            <div className="mt-6 pt-6 border-t border-slate-200">
                                <div className="text-sm text-slate-600 space-y-2">
                                    <div className="flex justify-between">
                                        <span>Profile Completeness</span>
                                        <span className="font-bold text-blue-600">{Math.min(100, skills.length * 10)}%</span>
                                    </div>
                                    <div className="w-full bg-slate-200 rounded-full h-2">
                                        <div
                                            className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(100, skills.length * 10)}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
