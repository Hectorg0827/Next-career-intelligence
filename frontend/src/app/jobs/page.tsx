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
    <div className="min-h-screen gradient-dark-glass">
      {/* Glassmorphic Header */}
      <div className="sticky top-20 z-40 glass-card border-b border-glass-line shadow-glass-lg rounded-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          {/* Title Section */}
          <div className="flex items-center justify-between mb-4 sm:mb-6">
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-accent-500 rounded-2xl blur-lg opacity-60"></div>
                <div className="relative p-2 sm:p-3 bg-gradient-to-br from-accent-500 to-accent-400 rounded-xl sm:rounded-2xl shadow-glass-md">
                  <Briefcase className="h-5 w-5 sm:h-7 sm:w-7 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-xl sm:text-3xl font-bold bg-gradient-to-r from-accent-500 to-accent-400 bg-clip-text text-transparent">
                  Job Marketplace
                </h1>
                <p className="text-xs sm:text-sm text-ink-300 mt-0.5 sm:mt-1">AI-powered matching with risk analysis</p>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 text-sm text-ink-300">
              <TrendingUp className="h-4 w-4 text-accent-400" />
              <span className="font-medium">{jobs.length} opportunities</span>
            </div>
          </div>

          {/* Premium Search Bar */}
          <div className="flex gap-2 sm:gap-3">
            <div className="flex-1 relative group">
              <div className="absolute inset-0 bg-accent-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative glass-card overflow-hidden">
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-ink-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search jobs by title, skills, or company..."
                  className="input-glass w-full pl-14 pr-6 py-4 text-sm font-medium"
                />
              </div>
            </div>

            <button
              onClick={handleSearch}
              className="primary-btn flex items-center gap-2 px-3 sm:px-4"
            >
              <Search className="h-5 w-5" />
              <span className="hidden sm:inline">Search</span>
            </button>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className="glass-card px-3 sm:px-6 py-4 hover:bg-glass-edge transition-all flex-shrink-0"
            >
              <div className="flex items-center gap-2 text-white">
                <Filter className="h-5 w-5" />
                <span className="hidden sm:inline font-medium">Filters</span>
                <ChevronDown className={`hidden sm:block h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </div>
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-4 glass-card p-6 shadow-glass-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white">Refine Your Search</h3>
                <button onClick={() => setShowFilters(false)} className="text-ink-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setFilters(prev => ({ ...prev, remote_only: !prev.remote_only }))}
                  className={`relative overflow-hidden rounded-xl p-4 transition-all ${
                    filters.remote_only
                      ? 'primary-btn'
                      : 'glass-card hover:bg-glass-edge text-white'
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
                      ? 'primary-btn'
                      : 'glass-card hover:bg-glass-edge text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <DollarSign className="h-5 w-5" />
                    <span className="font-medium">$100k+ Salary</span>
                  </div>
                </button>

                <button
                  className="glass-card hover:bg-glass-edge text-white rounded-xl p-4 transition-all"
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
              <div key={i} className="glass-card p-6">
                <div className="skeleton-glass h-6 w-3/4 mb-4"></div>
                <div className="skeleton-glass h-4 w-1/2 mb-6"></div>
                <div className="space-y-2">
                  <div className="skeleton-glass h-3 w-full"></div>
                  <div className="skeleton-glass h-3 w-5/6"></div>
                </div>
              </div>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="glass-card rounded-3xl p-16 text-center shadow-glass-xl">
            <div className="relative mx-auto w-20 h-20 mb-6">
              <div className="absolute inset-0 bg-accent-500/20 rounded-full blur-xl"></div>
              <div className="relative glass-card rounded-full p-5">
                <Briefcase className="h-10 w-10 text-ink-400" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No jobs found</h3>
            <p className="text-ink-300">Try adjusting your search or filters</p>
            {(searchQuery || filters.remote_only || filters.salary_min) && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setFilters({ page: 1, page_size: 20 });
                }}
                className="mt-6 primary-btn"
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
                className="glass-card hover-reflect group p-6 cursor-pointer hover:shadow-glass-xl transition-all duration-300"
              >
                {/* Hover Glow Effect */}
                <div className="absolute inset-0 bg-accent-500/0 group-hover:bg-accent-500/5 rounded-2xl transition-all duration-300"></div>

                <div className="relative">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-white group-hover:text-accent-400 transition-colors mb-2 line-clamp-2">
                        {job.title}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-ink-300">
                        <Building2 className="h-4 w-4" />
                        <span className="font-medium">{job.company || 'Company Name'}</span>
                      </div>
                    </div>
                    <button className="p-2 rounded-xl hover:bg-glass-edge transition-colors">
                      <Heart className="h-5 w-5 text-ink-400 hover:text-red-500" />
                    </button>
                  </div>

                  {/* Details */}
                  <div className="flex flex-wrap gap-3 mb-4">
                    {job.location_city && (
                      <div className="glass-pill flex items-center gap-1.5 text-sm text-accent-400 font-medium">
                        <MapPin className="h-4 w-4" />
                        {job.location_city}
                      </div>
                    )}
                    {job.location_type === 'remote' && (
                      <div className="glass-pill flex items-center gap-1.5 text-sm text-accent-400 font-medium">
                        <Sparkles className="h-4 w-4" />
                        Remote
                      </div>
                    )}
                    {(job.salary_min || job.salary_max) && (
                      <div className="glass-pill flex items-center gap-1.5 text-sm text-accent-400 font-medium">
                        <DollarSign className="h-4 w-4" />
                        {formatSalary(job.salary_min, job.salary_max)}
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-sm text-ink-300 line-clamp-3 mb-4 leading-relaxed">
                    {job.description}
                  </p>

                  {/* Skills */}
                  {job.skills_extracted && job.skills_extracted.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills_extracted.slice(0, 5).map((skill: string, i: number) => (
                        <span
                          key={i}
                          className="px-3 py-1 text-xs font-medium bg-glass-white text-ink-200 rounded-lg border border-glass-line"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-glass-line">
                    <span className="text-xs text-ink-400 font-medium">
                      Posted {new Date(job.posted_at || job.created_at).toLocaleDateString()}
                    </span>
                    <button className="primary-btn px-5 py-2.5 text-sm flex items-center gap-2">
                      <span>View Details</span>
                      <ExternalLink className="h-4 w-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
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

