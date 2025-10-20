"use client";

import { useState } from "react";
import { Brain, ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { analyzeCareer, generateCareerRoadmap } from "@/lib/api";
import type { 
  CareerAnalysis, 
  CareerRoadmapResponse,
  SankeyData, 
  IndustryBenchmarks 
} from "@/lib/types";

// Feature 5 & 6 Components
import CareerSankeyDiagram from "@/components/VisualCareerMaps/CareerSankeyDiagram";
import ShareCareerMap from "@/components/VisualCareerMaps/ShareCareerMap";
import RiskComparisonBadge from "@/components/Benchmarking/RiskComparisonBadge";
import BenchmarkChart from "@/components/Benchmarking/BenchmarkChart";
import ProgressTracker from "@/components/Benchmarking/ProgressTracker";
import TrendIndicator from "@/components/Benchmarking/TrendIndicator";

interface FormData {
  jobTitle: string;
  skills: string;
  location: string;
  yearsExperience: string;
  timeline: string;
}

export default function DashboardPage() {
  const [formData, setFormData] = useState<FormData>({
    jobTitle: "",
    skills: "",
    location: "",
    yearsExperience: "",
    timeline: "5 years",
  });

  const [analysisResult, setAnalysisResult] = useState<CareerAnalysis | null>(null);
  const [roadmapResult, setRoadmapResult] = useState<CareerRoadmapResponse | null>(null);
  const [sankeyData, setSankeyData] = useState<SankeyData | null>(null);
  const [benchmarkData, setBenchmarkData] = useState<IndustryBenchmarks | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingRoadmap, setIsGeneratingRoadmap] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await analyzeCareer({
        job_title: formData.jobTitle,
        skills: formData.skills.split(",").map((s) => s.trim()),
        location: formData.location,
        years_experience: parseInt(formData.yearsExperience) || undefined,
      });

      setAnalysisResult(result);
      
      // Extract Feature 6: Industry Benchmarks
      if (result.industry_benchmarks) {
        setBenchmarkData(result.industry_benchmarks);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze career");
      console.error("Analysis error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!analysisResult) return;

    setError(null);
    setIsGeneratingRoadmap(true);

    try {
      const result = await generateCareerRoadmap({
        job_title: formData.jobTitle,
        skills: formData.skills.split(",").map((s) => s.trim()),
        location: formData.location,
        years_experience: parseInt(formData.yearsExperience) || undefined,
        timeline: formData.timeline,
      });

      setRoadmapResult(result);
      
      // Extract Feature 5: Sankey Data for Visual Career Maps
      if (result.career_roadmap?.sankey_data) {
        setSankeyData(result.career_roadmap.sankey_data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate roadmap");
      console.error("Roadmap error:", err);
    } finally {
      setIsGeneratingRoadmap(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "Low":
        return "text-green-600 bg-green-50";
      case "Medium":
        return "text-yellow-600 bg-yellow-50";
      case "High":
        return "text-orange-600 bg-orange-50";
      case "Critical":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 border-b border-gray-200">
        <nav className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 hover:opacity-80">
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm">Back to Home</span>
            </Link>
          </div>
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              NEXT Dashboard
            </span>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Input Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h1 className="text-3xl font-bold mb-6">Career Analysis & Roadmap</h1>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title *
                </label>
                <input
                  type="text"
                  value={formData.jobTitle}
                  onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Software Engineer"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location *
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., San Francisco, CA"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skills * (comma-separated)
              </label>
              <textarea
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder="e.g., Python, JavaScript, Project Management, Communication"
                required
              />
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Years of Experience
                </label>
                <input
                  type="number"
                  value={formData.yearsExperience}
                  onChange={(e) => setFormData({ ...formData, yearsExperience: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 5"
                  min="0"
                  max="50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timeline for Career Roadmap
                </label>
                <select
                  value={formData.timeline}
                  onChange={(e) => setFormData({ ...formData, timeline: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="3 years">3 Years</option>
                  <option value="5 years">5 Years</option>
                  <option value="10 years">10 Years</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  "Analyze Career"
                )}
              </button>

              {analysisResult && (
                <button
                  type="button"
                  onClick={handleGenerateRoadmap}
                  disabled={isGeneratingRoadmap}
                  className="flex-1 bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                >
                  {isGeneratingRoadmap ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    "Generate Visual Roadmap"
                  )}
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Analysis Results */}
        {analysisResult && (
          <div className="space-y-8">
            {/* AI Displacement Risk */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold mb-6">AI Displacement Risk Analysis</h2>
              
              <div className="mb-6">
                <div className="flex items-center gap-4 mb-4">
                  <span
                    className={`px-6 py-3 rounded-full font-bold text-lg ${getRiskLevelColor(
                      analysisResult.ai_displacement_risk.level
                    )}`}
                  >
                    {analysisResult.ai_displacement_risk.level} Risk
                  </span>
                  <span className="text-4xl font-bold text-gray-800">
                    {analysisResult.ai_displacement_risk.risk_score.toFixed(1)}%
                  </span>
                </div>

                <div className="space-y-2 text-gray-700">
                  <p>
                    <strong>Reasoning:</strong> {analysisResult.ai_displacement_risk.reasoning}
                  </p>
                </div>
              </div>

              {/* Feature 6: Industry Benchmarks - Risk Comparison */}
              {benchmarkData?.benchmarks?.automation_risk_comparison && (
                <div className="mt-6">
                  <h3 className="text-xl font-semibold mb-4">How You Compare</h3>
                  <RiskComparisonBadge
                    yourScore={benchmarkData.benchmarks.automation_risk_comparison.your_score}
                    industryAverage={benchmarkData.benchmarks.automation_risk_comparison.industry_average}
                    percentile={benchmarkData.benchmarks.automation_risk_comparison.percentile}
                    comparisonText={benchmarkData.benchmarks.automation_risk_comparison.comparison_text}
                    trend={benchmarkData.benchmarks.automation_risk_comparison.trend as "improving" | "declining" | "stable"}
                  />
                </div>
              )}
            </div>

            {/* Feature 6: Industry Benchmarking Dashboard */}
            {benchmarkData && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-6">📊 Industry Benchmarks</h2>
                
                <div className="space-y-8">
                  {/* Skill Demand Analysis */}
                  {benchmarkData.benchmarks?.skill_demand && (
                    <div>
                      <h3 className="text-xl font-semibold mb-4">Skill Demand & Gaps</h3>
                      <ProgressTracker
                        overallScore={benchmarkData.benchmarks.skill_demand.overall_score}
                        topSkills={benchmarkData.benchmarks.skill_demand.top_skills}
                        skillGaps={benchmarkData.benchmarks.skill_demand.skill_gaps}
                      />
                    </div>
                  )}

                  {/* Salary Benchmarking */}
                  {benchmarkData.benchmarks?.salary_benchmark && (
                    <div>
                      <h3 className="text-xl font-semibold mb-4">Salary Benchmarking</h3>
                      <BenchmarkChart
                        yourEstimatedRange={benchmarkData.benchmarks.salary_benchmark.your_estimated_range}
                        industryMedian={benchmarkData.benchmarks.salary_benchmark.industry_median}
                        percentile25={benchmarkData.benchmarks.salary_benchmark.percentile_25}
                        percentile50={benchmarkData.benchmarks.salary_benchmark.percentile_50}
                        percentile75={benchmarkData.benchmarks.salary_benchmark.percentile_75}
                        percentile90={benchmarkData.benchmarks.salary_benchmark.percentile_90}
                        yourPosition={benchmarkData.benchmarks.salary_benchmark.your_position}
                      />
                    </div>
                  )}

                  {/* Market Trends & Career Progression */}
                  {benchmarkData.benchmarks?.market_trends && benchmarkData.benchmarks?.career_progression && (
                    <div>
                      <h3 className="text-xl font-semibold mb-4">Market Trends & Career Progression</h3>
                      <TrendIndicator
                        roleGrowth={benchmarkData.benchmarks.market_trends.role_growth}
                        hiringDifficulty={benchmarkData.benchmarks.market_trends.hiring_difficulty}
                        remoteAvailability={benchmarkData.benchmarks.market_trends.remote_availability}
                        topHiringIndustries={benchmarkData.benchmarks.market_trends.top_hiring_industries}
                        careerPace={benchmarkData.benchmarks.career_progression.pace}
                        typicalYearsToNextLevel={benchmarkData.benchmarks.career_progression.typical_years_to_next_level}
                        readinessScore={benchmarkData.benchmarks.career_progression.your_readiness_score}
                      />
                    </div>
                  )}

                  {/* Competitive Position */}
                  {benchmarkData.benchmarks?.competitive_position && (
                    <div className="mt-6 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl">
                      <h3 className="text-xl font-semibold mb-4">Your Competitive Position</h3>
                      <div className="space-y-3">
                        <p className="text-lg">
                          <strong>Ranking:</strong>{" "}
                          <span className="text-purple-600 font-bold">
                            {benchmarkData.benchmarks.competitive_position.peer_ranking}
                          </span>
                        </p>
                        {benchmarkData.benchmarks.competitive_position.strengths && benchmarkData.benchmarks.competitive_position.strengths.length > 0 && (
                          <div>
                            <strong>Strengths:</strong>
                            <ul className="mt-2 space-y-1">
                              {benchmarkData.benchmarks.competitive_position.strengths.map((strength: string, idx: number) => (
                                <li key={idx} className="text-green-700 flex items-center gap-2">
                                  <span className="text-green-500">✓</span> {strength}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {benchmarkData.benchmarks.competitive_position.areas_for_improvement && benchmarkData.benchmarks.competitive_position.areas_for_improvement.length > 0 && (
                          <div>
                            <strong>Areas for Improvement:</strong>
                            <ul className="mt-2 space-y-1">
                              {benchmarkData.benchmarks.competitive_position.areas_for_improvement.map((area: string, idx: number) => (
                                <li key={idx} className="text-orange-700 flex items-center gap-2">
                                  <span className="text-orange-500">→</span> {area}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Skill Insights */}
            {analysisResult.skill_insights && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-6">💡 Skill Intelligence</h2>
                
                {/* Skill Strength Score */}
                {analysisResult.skill_insights.skill_strength_score && (
                  <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
                    <h3 className="text-xl font-semibold mb-3">Overall Skill Strength</h3>
                    <div className="flex items-center gap-4">
                      <div className="text-5xl font-bold text-blue-600">
                        {analysisResult.skill_insights.skill_strength_score.overall_score.toFixed(1)}
                      </div>
                      <div className="flex-1">
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-500"
                            style={{ width: `${analysisResult.skill_insights.skill_strength_score.overall_score}%` }}
                          />
                        </div>
                        <p className="mt-2 text-gray-700">
                          {analysisResult.skill_insights.skill_strength_score.interpretation}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Transferable Skills */}
                {analysisResult.skill_insights.transferable_to && analysisResult.skill_insights.transferable_to.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-xl font-semibold mb-3">🔄 Transferable Skills</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {analysisResult.skill_insights.transferable_to.map((skill, idx) => (
                        <div key={idx} className="p-4 bg-green-50 border border-green-200 rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-semibold text-green-800">{skill.skill}</span>
                            <span className="text-sm text-green-600">
                              {(skill.confidence * 100).toFixed(0)}% match
                            </span>
                          </div>
                          <p className="text-sm text-gray-700">{skill.reasoning}</p>
                          {skill.source_skills && skill.source_skills.length > 0 && (
                            <p className="text-xs text-gray-500 mt-2">
                              From: {skill.source_skills.join(", ")}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Hidden Skills */}
                {analysisResult.skill_insights.hidden_skills && analysisResult.skill_insights.hidden_skills.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-xl font-semibold mb-3">💎 Hidden Skills Detected</h3>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.skill_insights.hidden_skills.map((skillObj, idx) => (
                        <span
                          key={idx}
                          className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full font-medium"
                          title={typeof skillObj === 'object' ? skillObj.why_hidden : ''}
                        >
                          {typeof skillObj === 'string' ? skillObj : skillObj.skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skill Gaps for Growth */}
                {analysisResult.skill_insights.skill_gaps_for_growth && analysisResult.skill_insights.skill_gaps_for_growth.length > 0 && (
                  <div>
                    <h3 className="text-xl font-semibold mb-3">📈 Skills to Develop</h3>
                    <div className="space-y-3">
                      {analysisResult.skill_insights.skill_gaps_for_growth.map((gap, idx) => (
                        <div
                          key={idx}
                          className="p-4 bg-orange-50 border-l-4 border-orange-400 rounded-r-lg"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-semibold text-orange-800">{gap.skill}</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              gap.priority === "Critical" ? "bg-red-100 text-red-700" :
                              gap.priority === "High" ? "bg-orange-100 text-orange-700" :
                              gap.priority === "Medium" ? "bg-yellow-100 text-yellow-700" :
                              "bg-blue-100 text-blue-700"
                            }`}>
                              {gap.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{gap.why_important}</p>
                          <div className="flex gap-4 text-sm text-gray-600">
                            <span>⏱ {gap.estimated_learning_time}</span>
                            <span>📊 {gap.market_demand}</span>
                            <span>🎯 {gap.learn_difficulty}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Feature 5: Visual Career Map */}
            {sankeyData && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-6">🗺️ Your Visual Career Map</h2>
                <p className="text-gray-600 mb-6">
                  Interactive visualization of your career pathways. Click on nodes to highlight connections.
                </p>
                
                <CareerSankeyDiagram 
                  data={sankeyData as any}
                  currentRole={formData.jobTitle}
                />

                <div className="mt-6">
                  <ShareCareerMap 
                    careerData={{
                      currentRole: formData.jobTitle,
                      futureRole: sankeyData.nodes.length > 0 
                        ? sankeyData.nodes[sankeyData.nodes.length - 1].name 
                        : "Future Role",
                      timeline: formData.timeline,
                    }}
                  />
                </div>
              </div>
            )}

            {/* Career Roadmap Details */}
            {roadmapResult && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-6">Career Roadmap Details</h2>
                
                {["3_year", "5_year", "10_year"].map((timeframe) => {
                  const pathway = roadmapResult.career_roadmap[timeframe as keyof typeof roadmapResult.career_roadmap];
                  if (!pathway || typeof pathway !== "object" || !("primary_path" in pathway)) return null;

                  return (
                    <div key={timeframe} className="mb-8 last:mb-0">
                      <h3 className="text-xl font-semibold mb-4 capitalize">
                        {timeframe.replace("_", "-")} Path
                      </h3>
                      
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl mb-4">
                        <h4 className="font-bold text-lg text-blue-900 mb-2">
                          {(pathway.primary_path as any)?.target_role}
                        </h4>
                        <p className="text-gray-700 mb-4">{(pathway.primary_path as any)?.milestone_title}</p>
                        
                        <div className="grid md:grid-cols-2 gap-4 text-sm">
                          {(pathway.primary_path as any)?.skills_to_develop && (pathway.primary_path as any)?.skills_to_develop.length > 0 && (
                            <div>
                              <strong>Skills to Develop:</strong>
                              <ul className="mt-2 space-y-1">
                                {(pathway.primary_path as any)?.skills_to_develop.map((skill: string, idx: number) => (
                                  <li key={idx} className="text-gray-700">• {skill}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {(pathway.primary_path as any)?.certifications && (pathway.primary_path as any)?.certifications.length > 0 && (
                            <div>
                              <strong>Certifications:</strong>
                              <ul className="mt-2 space-y-1">
                                {(pathway.primary_path as any)?.certifications.map((cert: string, idx: number) => (
                                  <li key={idx} className="text-gray-700">• {cert}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        <div className="mt-4 pt-4 border-t border-blue-200">
                          <div className="flex justify-between items-center text-sm">
                            <span>
                              <strong>Salary Range:</strong> {(pathway.primary_path as any)?.estimated_salary_range}
                            </span>
                            <span>
                              <strong>AI Resilience:</strong>{" "}
                              <span className="text-green-600 font-bold">
                                {(pathway.primary_path as any)?.ai_resilience_score}/100
                              </span>
                            </span>
                          </div>
                        </div>
                      </div>

                      {(pathway as any).alternative_path && (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h5 className="font-semibold mb-2">Alternative: {(pathway as any).alternative_path.target_role}</h5>
                          <p className="text-sm text-gray-600">{(pathway as any).alternative_path.why_consider}</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Transition Pathways */}
            {analysisResult.transition_pathways && analysisResult.transition_pathways.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-6">🎯 Recommended Career Transitions</h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  {analysisResult.transition_pathways.map((pathway, idx) => (
                    <div
                      key={idx}
                      className="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-400 transition-all"
                    >
                      <h3 className="text-xl font-bold mb-2">{pathway.role}</h3>
                      <div className="mb-4">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-gray-600">Transition Ease</span>
                          <span className="text-sm font-semibold">{pathway.ease.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
                            style={{ width: `${pathway.ease}%` }}
                          />
                        </div>
                      </div>

                      <div className="space-y-3 text-sm">
                        {pathway.required_skills && pathway.required_skills.length > 0 && (
                          <div>
                            <strong>Required Skills:</strong>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {pathway.required_skills.map((skill, skillIdx) => (
                                <span
                                  key={skillIdx}
                                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {pathway.estimated_training_time && (
                          <p>
                            <strong>Training Time:</strong> {pathway.estimated_training_time}
                          </p>
                        )}
                        
                        {pathway.salary_potential && (
                          <p>
                            <strong>Salary Range:</strong> {pathway.salary_potential}
                          </p>
                        )}
                        
                        {pathway.demand_trend && (
                          <p>
                            <strong>Market Demand:</strong> {pathway.demand_trend}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
