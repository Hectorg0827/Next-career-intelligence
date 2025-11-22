'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Zap, TrendingUp, Award, ChevronRight } from 'lucide-react';

interface Skill {
    id: string;
    name: string;
    category?: string;
    proficiency_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT';
    evidence_source: string;
}

interface SkillProfileData {
    user_id: string;
    skills: Skill[];
    total_count: number;
}

export default function SkillProfileWidget() {
    const [skillData, setSkillData] = useState<SkillProfileData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchSkills();
    }, []);

    const fetchSkills = async () => {
        try {
            const response = await fetch('/api/profile/skills');
            if (response.ok) {
                const data = await response.json();
                setSkillData(data);
            }
        } catch (error) {
            console.error('Failed to fetch skills:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const proficiencyColor = (level: string) => {
        switch (level) {
            case 'EXPERT': return 'from-purple-500 to-pink-500';
            case 'ADVANCED': return 'from-blue-500 to-cyan-500';
            case 'INTERMEDIATE': return 'from-green-500 to-emerald-500';
            case 'BEGINNER': return 'from-yellow-500 to-orange-500';
            default: return 'from-gray-500 to-slate-500';
        }
    };

    const proficiencyWidth = (level: string) => {
        switch (level) {
            case 'EXPERT': return '100%';
            case 'ADVANCED': return '75%';
            case 'INTERMEDIATE': return '50%';
            case 'BEGINNER': return '25%';
            default: return '10%';
        }
    };

    if (isLoading) {
        return (
            <div className="bg-white rounded-2xl shadow-xl p-8 animate-pulse">
                <div className="h-8 bg-slate-200 rounded-lg w-48 mb-6" />
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-16 bg-slate-100 rounded-lg" />
                    ))}
                </div>
            </div>
        );
    }

    if (!skillData || skillData.total_count === 0) {
        return (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-xl p-8 border-2 border-dashed border-blue-200">
                <div className="text-center">
                    <Zap className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Build Your Skill Profile</h3>
                    <p className="text-slate-600 mb-6">
                        Map your skills to unlock personalized insights and gap analysis
                    </p>
                    <button
                        onClick={() => window.location.href = '/onboarding/skills'}
                        className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all inline-flex items-center gap-2"
                    >
                        Get Started
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        );
    }

    const topSkills = skillData.skills.slice(0, 10);
    const expertCount = skillData.skills.filter(s => s.proficiency_level === 'EXPERT').length;
    const advancedCount = skillData.skills.filter(s => s.proficiency_level === 'ADVANCED').length;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl overflow-hidden"
        >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold flex items-center gap-2">
                        <Zap className="w-6 h-6" />
                        Your Skill Profile
                    </h3>
                    <button
                        onClick={() => window.location.href = '/onboarding/skills'}
                        className="text-sm bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-all"
                    >
                        Edit Skills
                    </button>
                </div>
                <p className="text-blue-100">
                    {skillData.total_count} skill{skillData.total_count !== 1 ? 's' : ''} mapped across your profile
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 p-6 bg-slate-50 border-b border-slate-200">
                <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-1">{expertCount}</div>
                    <div className="text-xs text-slate-600 uppercase tracking-wide">Expert</div>
                </div>
                <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-1">{advancedCount}</div>
                    <div className="text-xs text-slate-600 uppercase tracking-wide">Advanced</div>
                </div>
                <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-1">{skillData.total_count}</div>
                    <div className="text-xs text-slate-600 uppercase tracking-wide">Total</div>
                </div>
            </div>

            {/* Skills List */}
            <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
                {topSkills.map((skill, index) => (
                    <motion.div
                        key={skill.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="group"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-slate-800">{skill.name}</span>
                            <span className="text-xs px-2 py-1 bg-slate-100 text-slate-600 rounded-full uppercase tracking-wide">
                                {skill.proficiency_level}
                            </span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: proficiencyWidth(skill.proficiency_level) }}
                                transition={{ duration: 0.5, delay: index * 0.05 }}
                                className={`h-full bg-gradient-to-r ${proficiencyColor(skill.proficiency_level)} group-hover:shadow-lg transition-all`}
                            />
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Footer */}
            {skillData.total_count > 10 && (
                <div className="p-4 bg-slate-50 border-t border-slate-200 text-center">
                    <button
                        onClick={() => window.location.href = '/onboarding/skills'}
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm inline-flex items-center gap-1"
                    >
                        View all {skillData.total_count} skills
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            )}
        </motion.div>
    );
}
