'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, TrendingUp, AlertCircle, BookOpen, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

interface MatchedSkill {
    name: string;
    proficiency_level: string;
    relevance_score: number;
}

interface GapSkill {
    name: string;
    importance: string;
    estimated_time_to_learn?: string;
    recommended_resources: string[];
}

interface LearningCluster {
    cluster_name: string;
    skills: string[];
    estimated_time?: string;
    priority: string;
}

interface SkillGapAnalysis {
    title: string;
    summary: string;
    role_fit_score: number;
    matched_skills: MatchedSkill[];
    matched_count: number;
    gap_skills: GapSkill[];
    gap_count: number;
    weak_skills: MatchedSkill[];
    suggested_learning_clusters: LearningCluster[];
    target_role: string;
}

export default function SkillGapWidget() {
    const [targetRole, setTargetRole] = useState('');
    const [analysis, setAnalysis] = useState<SkillGapAnalysis | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showDetails, setShowDetails] = useState(false);

    const analyzeGap = async () => {
        if (!targetRole.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/profile/skill-gap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_role_title: targetRole }),
            });

            if (response.ok) {
                const data = await response.json();
                setAnalysis(data);
            }
        } catch (error) {
            console.error('Skill gap analysis failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getFitColor = (score: number) => {
        if (score >= 80) return 'from-green-500 to-emerald-500';
        if (score >= 60) return 'from-blue-500 to-cyan-500';
        if (score >= 40) return 'from-yellow-500 to-orange-500';
        return 'from-red-500 to-pink-500';
    };

    const getImportanceColor = (importance: string) => {
        switch (importance.toLowerCase()) {
            case 'critical': return 'bg-red-100 text-red-700 border-red-200';
            case 'high': return 'bg-orange-100 text-orange-700 border-orange-200';
            case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
            case 'low': return 'bg-blue-100 text-blue-700 border-blue-200';
            default: return 'bg-slate-100 text-slate-700 border-slate-200';
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority.toLowerCase()) {
            case 'high': return 'from-red-500 to-orange-500';
            case 'medium': return 'from-yellow-500 to-amber-500';
            case 'low': return 'from-blue-500 to-cyan-500';
            default: return 'from-slate-500 to-gray-500';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl overflow-hidden"
        >
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
                <h3 className="text-2xl font-bold flex items-center gap-2 mb-2">
                    <Target className="w-6 h-6" />
                    Skill Gap Analyzer
                </h3>
                <p className="text-indigo-100">
                    Discover what you need to reach your target role
                </p>
            </div>

            {/* Input Section */}
            <div className="p-6 border-b border-slate-200">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                    Target Role
                </label>
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && analyzeGap()}
                        placeholder="e.g., Data Analyst, Software Engineer..."
                        className="flex-1 px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-indigo-500 focus:outline-none"
                    />
                    <button
                        onClick={analyzeGap}
                        disabled={isLoading || !targetRole.trim()}
                        className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
                    >
                        {isLoading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-4 h-4" />
                                Analyze
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Analysis Results */}
            <AnimatePresence mode="wait">
                {analysis && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="p-6 space-y-6"
                    >
                        {/* Fit Score */}
                        <div className="text-center">
                            <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 mb-4">
                                <div className="text-5xl font-bold bg-gradient-to-r ${getFitColor(analysis.role_fit_score)} bg-clip-text text-transparent">
                                    {Math.round(analysis.role_fit_score)}%
                                </div>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 mb-2">{analysis.title}</h4>
                            <p className="text-slate-600 max-w-2xl mx-auto">{analysis.summary}</p>
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
                                <div className="flex items-center gap-2 mb-1">
                                    <TrendingUp className="w-5 h-5 text-green-600" />
                                    <span className="text-sm font-medium text-green-900">Matched Skills</span>
                                </div>
                                <div className="text-3xl font-bold text-green-700">{analysis.matched_count}</div>
                            </div>
                            <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-4 border border-orange-200">
                                <div className="flex items-center gap-2 mb-1">
                                    <AlertCircle className="w-5 h-5 text-orange-600" />
                                    <span className="text-sm font-medium text-orange-900">Gap Skills</span>
                                </div>
                                <div className="text-3xl font-bold text-orange-700">{analysis.gap_count}</div>
                            </div>
                        </div>

                        {/* Toggle Details */}
                        <button
                            onClick={() => setShowDetails(!showDetails)}
                            className="w-full py-3 bg-slate-100 hover:bg-slate-200 rounded-xl font-medium text-slate-700 flex items-center justify-center gap-2 transition-all"
                        >
                            {showDetails ? (
                                <>
                                    <ChevronUp className="w-4 h-4" />
                                    Hide Details
                                </>
                            ) : (
                                <>
                                    <ChevronDown className="w-4 h-4" />
                                    Show Detailed Analysis
                                </>
                            )}
                        </button>

                        {/* Detailed Analysis */}
                        <AnimatePresence>
                            {showDetails && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="space-y-6 overflow-hidden"
                                >
                                    {/* Matched Skills */}
                                    {analysis.matched_skills.length > 0 && (
                                        <div>
                                            <h5 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
                                                <TrendingUp className="w-4 h-4 text-green-600" />
                                                Your Strengths ({analysis.matched_skills.length})
                                            </h5>
                                            <div className="space-y-2">
                                                {analysis.matched_skills.slice(0, 5).map((skill, i) => (
                                                    <div key={i} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                                                        <span className="font-medium text-green-900">{skill.name}</span>
                                                        <span className="text-sm text-green-600">{Math.round(skill.relevance_score)}% match</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Gap Skills */}
                                    {analysis.gap_skills.length > 0 && (
                                        <div>
                                            <h5 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
                                                <AlertCircle className="w-4 h-4 text-orange-600" />
                                                Skills to Develop ({analysis.gap_skills.length})
                                            </h5>
                                            <div className="space-y-3">
                                                {analysis.gap_skills.map((skill, i) => (
                                                    <div key={i} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <span className="font-semibold text-slate-900">{skill.name}</span>
                                                            <span className={`text-xs px-2 py-1 rounded-full border ${getImportanceColor(skill.importance)}`}>
                                                                {skill.importance}
                                                            </span>
                                                        </div>
                                                        {skill.estimated_time_to_learn && (
                                                            <div className="text-sm text-slate-600">
                                                                ⏱️ Est. time: {skill.estimated_time_to_learn}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Learning Clusters */}
                                    {analysis.suggested_learning_clusters.length > 0 && (
                                        <div>
                                            <h5 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
                                                <BookOpen className="w-4 h-4 text-blue-600" />
                                                Suggested Learning Path
                                            </h5>
                                            <div className="space-y-3">
                                                {analysis.suggested_learning_clusters.map((cluster, i) => (
                                                    <div key={i} className="p-4 rounded-xl border-2 border-slate-200 bg-gradient-to-br from-white to-slate-50">
                                                        <div className="flex items-center justify-between mb-3">
                                                            <h6 className="font-bold text-slate-900">{cluster.cluster_name}</h6>
                                                            <span className={`text-xs px-3 py-1 rounded-full bg-gradient-to-r ${getPriorityColor(cluster.priority)} text-white font-medium`}>
                                                                {cluster.priority} Priority
                                                            </span>
                                                        </div>
                                                        <div className="flex flex-wrap gap-2 mb-2">
                                                            {cluster.skills.map((skill, j) => (
                                                                <span key={j} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">
                                                                    {skill}
                                                                </span>
                                                            ))}
                                                        </div>
                                                        {cluster.estimated_time && (
                                                            <div className="text-sm text-slate-600">
                                                                📅 Timeline: {cluster.estimated_time}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Empty State */}
            {!analysis && !isLoading && (
                <div className="p-12 text-center">
                    <Target className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <p className="text-slate-500">
                        Enter a target role above to see your skill gap analysis
                    </p>
                </div>
            )}
        </motion.div>
    );
}
