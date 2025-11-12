'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { intelligenceApi } from '@/lib/api';
import { Job, JobSearchQuery } from '@/types/jobs';
import { 
  Briefcase, 
  MapPin, 
  DollarSign, 
  Building2,
  Search,
  Filter,
  Sparkles,
  TrendingUp,
  Heart,
  ExternalLink,
  X,
  ChevronDown
} from 'lucide-react';

export default function JobsPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<JobSearchQuery>({
    page: 1,
    page_size: 20
  });

  useEffect(() => {
    loadJobs();
  }, [filters]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const response = await intelligenceApi.searchJobs(filters);
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, query: searchQuery, page: 1 }));
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Competitive';
    if (min && max) return `$${(min/1000).toFixed(0)}k - $${(max/1000).toFixed(0)}k`;
    if (min) return `From $${(min/1000).toFixed(0)}k`;
    return `Up to $${(max!/1000).toFixed(0)}k`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Glassmorphic Header */}
      <div className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 border-b border-white/20 shadow-lg shadow-black/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Title Section */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl blur-lg opacity-60"></div>
                <div className="relative p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl">
                  <Briefcase className="h-7 w-7 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Job Marketplace
                </h1>
                <p className="text-sm text-slate-600 mt-1">AI-powered matching with risk analysis</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="font-medium">{jobs.length} opportunities</span>
            </div>
          </div>

          {/* Premium Search Bar */}
          <div className="flex gap-3">
            <div className="flex-1 relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative backdrop-blur-sm bg-white/80 rounded-2xl border border-white/40 shadow-lg shadow-black/5 overflow-hidden">
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search jobs by title, skills, or company..."
                  className="w-full pl-14 pr-6 py-4 bg-transparent text-slate-800 placeholder:text-slate-400 focus:outline-none text-sm font-medium"
                />
              </div>
            </div>
            
            <button
              onClick={handleSearch}
              className="relative group/btn overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl transition-transform group-hover/btn:scale-105"></div>
              <div className="relative px-8 py-4 flex items-center gap-2 text-white font-semibold">
                <Search className="h-5 w-5" />
                <span className="hidden sm:inline">Search</span>
              </div>
            </button>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className="relative backdrop-blur-sm bg-white/80 rounded-2xl border border-white/40 px-6 py-4 hover:shadow-lg transition-all group/filter"
            >
              <div className="flex items-center gap-2 text-slate-700">
                <Filter className="h-5 w-5" />
                <span className="hidden sm:inline font-medium">Filters</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </div>
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-4 backdrop-blur-xl bg-white/80 rounded-2xl border border-white/40 p-6 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-800">Refine Your Search</h3>
                <button onClick={() => setShowFilters(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setFilters(prev => ({ ...prev, remote_only: !prev.remote_only }))}
                  className={`relative overflow-hidden rounded-xl p-4 transition-all ${
                    filters.remote_only 
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg' 
                      : 'bg-white/60 text-slate-700 hover:bg-white/80 border border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <MapPin className="h-5 w-5" />
                    <span className="font-medium">Remote Only</span>
                  </div>
                </button>

                <button
                  onClick={() => setFilters(prev => ({ ...prev, salary_min: prev.salary_min ? undefined : 100000 }))}
                  className={`relative overflow-hidden rounded-xl p-4 transition-all ${
                    filters.salary_min 
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg' 
                      : 'bg-white/60 text-slate-700 hover:bg-white/80 border border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <DollarSign className="h-5 w-5" />
                    <span className="font-medium">$100k+ Salary</span>
                  </div>
                </button>

                <button
                  className="relative overflow-hidden rounded-xl p-4 bg-white/60 text-slate-700 hover:bg-white/80 border border-slate-200 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-5 w-5" />
                    <span className="font-medium">AI Matched</span>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Job Cards Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="backdrop-blur-xl bg-white/70 rounded-2xl border border-white/40 p-6 animate-pulse">
                <div className="h-6 bg-slate-200 rounded-lg w-3/4 mb-4"></div>
                <div className="h-4 bg-slate-200 rounded w-1/2 mb-6"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-slate-200 rounded w-full"></div>
                  <div className="h-3 bg-slate-200 rounded w-5/6"></div>
                </div>
              </div>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="backdrop-blur-xl bg-white/70 rounded-3xl border border-white/40 p-16 text-center shadow-xl">
            <div className="relative mx-auto w-20 h-20 mb-6">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-full blur-xl"></div>
              <div className="relative backdrop-blur-sm bg-white/80 rounded-full p-5 border border-white/40">
                <Briefcase className="h-10 w-10 text-slate-400" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-slate-800 mb-2">No jobs found</h3>
            <p className="text-slate-600">Try adjusting your search or filters</p>
            {(searchQuery || filters.remote_only || filters.salary_min) && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setFilters({ page: 1, page_size: 20 });
                }}
                className="mt-6 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all font-medium"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="group relative backdrop-blur-xl bg-white/70 hover:bg-white/90 rounded-2xl border border-white/40 hover:border-white/60 p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 cursor-pointer"
              >
                {/* Hover Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-purple-600/0 group-hover:from-blue-500/5 group-hover:to-purple-600/5 rounded-2xl transition-all duration-300"></div>
                
                <div className="relative">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-slate-800 group-hover:text-blue-600 transition-colors mb-2 line-clamp-2">
                        {job.title}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-slate-600">
                        <Building2 className="h-4 w-4" />
                        <span className="font-medium">{job.company || 'Company Name'}</span>
                      </div>
                    </div>
                    <button className="p-2 rounded-xl hover:bg-slate-100 transition-colors">
                      <Heart className="h-5 w-5 text-slate-400 hover:text-red-500" />
                    </button>
                  </div>

                  {/* Details */}
                  <div className="flex flex-wrap gap-3 mb-4">
                    {job.location_city && (
                      <div className="flex items-center gap-1.5 px-3 py-1.5 backdrop-blur-sm bg-blue-50/80 rounded-lg text-sm text-blue-700 font-medium">
                        <MapPin className="h-4 w-4" />
                        {job.location_city}
                      </div>
                    )}
                    {job.location_type === 'remote' && (
                      <div className="flex items-center gap-1.5 px-3 py-1.5 backdrop-blur-sm bg-green-50/80 rounded-lg text-sm text-green-700 font-medium">
                        <Sparkles className="h-4 w-4" />
                        Remote
                      </div>
                    )}
                    {(job.salary_min || job.salary_max) && (
                      <div className="flex items-center gap-1.5 px-3 py-1.5 backdrop-blur-sm bg-purple-50/80 rounded-lg text-sm text-purple-700 font-medium">
                        <DollarSign className="h-4 w-4" />
                        {formatSalary(job.salary_min, job.salary_max)}
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-sm text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                    {job.description}
                  </p>

                  {/* Skills */}
                  {job.skills_extracted && job.skills_extracted.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills_extracted.slice(0, 5).map((skill: string, i: number) => (
                        <span
                          key={i}
                          className="px-3 py-1 text-xs font-medium bg-gradient-to-r from-slate-100 to-slate-50 text-slate-700 rounded-lg border border-slate-200/50"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-200/50">
                    <span className="text-xs text-slate-500 font-medium">
                      Posted {new Date(job.posted_at || job.created_at).toLocaleDateString()}
                    </span>
                    <button className="group/btn relative overflow-hidden px-5 py-2.5 rounded-xl font-semibold text-sm transition-all hover:shadow-lg">
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 transition-transform group-hover/btn:scale-105"></div>
                      <div className="relative flex items-center gap-2 text-white">
                        <span>View Details</span>
                        <ExternalLink className="h-4 w-4 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

