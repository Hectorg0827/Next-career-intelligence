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
            className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden"
        >
            {/* Header */}
            <div className="bg-gradient-to-r from-royal-blue-deep/50 to-purple-900/50 p-6 border-b border-white/10">
                <h3 className="text-xl font-bold flex items-center gap-2 mb-2 text-white">
                    <Target className="w-6 h-6 text-gold-primary" />
                    Skill Gap Analyzer
                </h3>
                <p className="text-white/70 text-sm">
                    Discover what you need to reach your target role
                </p>
            </div>

            {/* Input Section */}
            <div className="p-6 border-b border-white/5">
                <label className="block text-sm font-medium text-white/80 mb-2">
                    Target Role
                </label>
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && analyzeGap()}
                        placeholder="e.g., Data Analyst, Software Engineer..."
                        className="flex-1 input-glass"
                    />
                    <button
                        onClick={analyzeGap}
                        disabled={isLoading || !targetRole.trim()}
                        className="px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent text-royal-navy rounded-xl font-bold hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98]"
                    >
                        {isLoading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-royal-navy border-t-transparent rounded-full animate-spin" />
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
                        <div className="text-center relative">
                            {/* Glow effect behind score */}
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-gold-primary/20 blur-3xl rounded-full pointer-events-none" />

                            <div className="inline-flex items-center justify-center w-32 h-32 rounded-full border border-slate-600 bg-slate-700 mb-4 relative z-10">
                                <div className={`text-5xl font-bold bg-gradient-to-r ${getFitColor(analysis.role_fit_score)} bg-clip-text text-transparent`}>
                                    {Math.round(analysis.role_fit_score)}%
                                </div>
                            </div>
                            <h4 className="text-xl font-bold text-white mb-2">{analysis.title}</h4>
                            <p className="text-white/60 max-w-2xl mx-auto text-sm leading-relaxed">{analysis.summary}</p>
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 rounded-xl p-4 border border-green-500/20">
                                <div className="flex items-center gap-2 mb-1">
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                    <span className="text-xs font-semibold uppercase tracking-wider text-green-400">Matched</span>
                                </div>
                                <div className="text-3xl font-bold text-white">{analysis.matched_count}</div>
                            </div>
                            <div className="bg-gradient-to-br from-orange-900/30 to-red-900/30 rounded-xl p-4 border border-orange-500/20">
                                <div className="flex items-center gap-2 mb-1">
                                    <AlertCircle className="w-4 h-4 text-orange-400" />
                                    <span className="text-xs font-semibold uppercase tracking-wider text-orange-400">Missing</span>
                                </div>
                                <div className="text-3xl font-bold text-white">{analysis.gap_count}</div>
                            </div>
                        </div>

                        {/* Toggle Details */}
                        <button
                            onClick={() => setShowDetails(!showDetails)}
                            className="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-medium text-white/80 flex items-center justify-center gap-2 transition-all group"
                        >
                            {showDetails ? (
                                <>
                                    <ChevronUp className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
                                    Hide Details
                                </>
                            ) : (
                                <>
                                    <ChevronDown className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
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
                                            <h5 className="font-bold text-white mb-3 flex items-center gap-2 text-sm uppercase tracking-wider">
                                                <TrendingUp className="w-4 h-4 text-green-400" />
                                                Your Strengths <span className="text-white/40">({analysis.matched_skills.length})</span>
                                            </h5>
                                            <div className="space-y-2">
                                                {analysis.matched_skills.slice(0, 5).map((skill, i) => (
                                                    <div key={i} className="flex items-center justify-between p-3 bg-green-500/5 rounded-lg border border-green-500/10 hover:bg-green-500/10 transition-colors">
                                                        <span className="font-medium text-white/90 text-sm">{skill.name}</span>
                                                        <span className="text-xs font-semibold text-green-400 bg-green-500/10 px-2 py-1 rounded">{Math.round(skill.relevance_score)}%</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Gap Skills */}
                                    {analysis.gap_skills.length > 0 && (
                                        <div>
                                            <h5 className="font-bold text-white mb-3 flex items-center gap-2 text-sm uppercase tracking-wider">
                                                <AlertCircle className="w-4 h-4 text-orange-400" />
                                                Skills to Develop <span className="text-white/40">({analysis.gap_skills.length})</span>
                                            </h5>
                                            <div className="space-y-3">
                                                {analysis.gap_skills.map((skill, i) => (
                                                    <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/10 hover:border-gold-primary/30 transition-colors">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <span className="font-semibold text-white">{skill.name}</span>
                                                            <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${getImportanceColor(skill.importance)}`}>
                                                                {skill.importance}
                                                            </span>
                                                        </div>
                                                        {skill.estimated_time_to_learn && (
                                                            <div className="text-sm text-white/50 flex items-center gap-1.5">
                                                                <span className="text-xs">⏱️</span> Est. time: {skill.estimated_time_to_learn}
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
                                            <h5 className="font-bold text-white mb-3 flex items-center gap-2 text-sm uppercase tracking-wider">
                                                <BookOpen className="w-4 h-4 text-blue-400" />
                                                Suggested Learning Path
                                            </h5>
                                            <div className="space-y-3">
                                                {analysis.suggested_learning_clusters.map((cluster, i) => (
                                                    <div key={i} className="p-4 rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-transparent relative overflow-hidden group">
                                                        {/* Hover glow */}
                                                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

                                                        <div className="flex items-center justify-between mb-3 relative z-10">
                                                            <h6 className="font-bold text-white">{cluster.cluster_name}</h6>
                                                            <span className={`text-[10px] uppercase tracking-wide px-2 py-0.5 rounded-full bg-gradient-to-r ${getPriorityColor(cluster.priority)} text-white font-bold shadow-lg`}>
                                                                {cluster.priority} Priority
                                                            </span>
                                                        </div>
                                                        <div className="flex flex-wrap gap-2 mb-2 relative z-10">
                                                            {cluster.skills.map((skill, j) => (
                                                                <span key={j} className="px-2.5 py-1 bg-royal-blue/30 text-blue-200 border border-blue-500/20 rounded-md text-xs font-medium">
                                                                    {skill}
                                                                </span>
                                                            ))}
                                                        </div>
                                                        {cluster.estimated_time && (
                                                            <div className="text-xs text-white/40 mt-3 border-t border-white/5 pt-2 flex items-center gap-1.5">
                                                                <span>📅</span> Timeline: {cluster.estimated_time}
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
                    <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6 border border-white/10">
                        <Target className="w-10 h-10 text-white/20" />
                    </div>
                    <p className="text-white/50 text-sm max-w-xs mx-auto">
                        Enter a target role above (e.g., "Product Manager") to see AI-powered skill gap analysis.
                    </p>
                </div>
            )}
        </motion.div>
    );
}
