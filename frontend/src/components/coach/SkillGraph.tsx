'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';

interface Skill {
  id: string;
  skill_name: string;
  category: string | null;
  proficiency_level: number | null;
  confidence_score: number;
  source_tags: string[];
  evidence_snippets: string[];
  confirmed_by_user: boolean;
  last_updated_at: string;
}

export default function SkillGraph() {
  const { user } = useAuth();
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'confirmed' | 'inferred'>('all');

  useEffect(() => {
    if (user) {
      fetchSkills();
    }
  }, [user]);

  const fetchSkills = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://localhost:8000/api/skills/user/${user?.uid}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch skills');
      
      const data = await response.json();
      setSkills(data);
    } catch (error) {
      console.error('Failed to load skills:', error);
    } finally {
      setLoading(false);
    }
  };

  const confirmSkill = async (skillId: string) => {
    try {
      const token = localStorage.getItem('authToken');
      await fetch(`http://localhost:8000/api/skills/user/${user?.uid}/confirm/${skillId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Refresh skills
      fetchSkills();
    } catch (error) {
      console.error('Failed to confirm skill:', error);
    }
  };

  const hideSkill = async (skillId: string) => {
    try {
      const token = localStorage.getItem('authToken');
      await fetch(`http://localhost:8000/api/skills/user/${user?.uid}/hide/${skillId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Refresh skills
      fetchSkills();
    } catch (error) {
      console.error('Failed to hide skill:', error);
    }
  };

  const filteredSkills = skills.filter(skill => {
    if (filter === 'confirmed') return skill.confirmed_by_user;
    if (filter === 'inferred') return !skill.confirmed_by_user;
    return true;
  });

  const getSourceBadgeColor = (source: string) => {
    switch(source) {
      case 'conversation': return 'bg-blue-100 text-blue-800';
      case 'resume': return 'bg-green-100 text-green-800';
      case 'task': return 'bg-purple-100 text-purple-800';
      case 'inferred_prior': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getProficiencyLabel = (level: number | null) => {
    if (!level) return 'Unknown';
    const labels = ['Beginner', 'Basic', 'Intermediate', 'Advanced', 'Expert'];
    return labels[level - 1] || 'Unknown';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Your Skills Graph</h2>
          <p className="text-gray-600 mt-1">
            Skills mined from your conversations, resume, and role profile
          </p>
        </div>
        
        {/* Filter Tabs */}
        <div className="flex gap-2 bg-white rounded-lg shadow-sm p-1">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded font-medium transition-colors ${
              filter === 'all' 
                ? 'bg-gold-primary text-white' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            All ({skills.length})
          </button>
          <button
            onClick={() => setFilter('confirmed')}
            className={`px-4 py-2 rounded font-medium transition-colors ${
              filter === 'confirmed' 
                ? 'bg-gold-primary text-white' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            Confirmed ({skills.filter(s => s.confirmed_by_user).length})
          </button>
          <button
            onClick={() => setFilter('inferred')}
            className={`px-4 py-2 rounded font-medium transition-colors ${
              filter === 'inferred' 
                ? 'bg-gold-primary text-white' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            Inferred ({skills.filter(s => !s.confirmed_by_user).length})
          </button>
        </div>
      </div>

      {/* Skills Grid */}
      {filteredSkills.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No {filter === 'all' ? '' : filter} skills yet
          </h3>
          <p className="text-gray-600">
            Start chatting with the Coach to discover your skills automatically!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill) => (
            <div
              key={skill.id}
              className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow border-l-4"
              style={{ borderLeftColor: skill.confirmed_by_user ? '#D4AF37' : '#9CA3AF' }}
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 mb-1">
                    {skill.skill_name}
                  </h3>
                  {skill.category && (
                    <span className="text-xs text-gray-500">{skill.category}</span>
                  )}
                </div>
                {skill.confirmed_by_user && (
                  <svg className="h-6 w-6 text-gold-primary" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              {/* Confidence & Proficiency */}
              <div className="mb-3 space-y-2">
                <div>
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Confidence</span>
                    <span className="font-medium">{Math.round(skill.confidence_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gold-primary h-2 rounded-full transition-all"
                      style={{ width: `${skill.confidence_score * 100}%` }}
                    />
                  </div>
                </div>
                
                {skill.proficiency_level && (
                  <div className="text-xs text-gray-600">
                    <span className="font-medium">Level:</span> {getProficiencyLabel(skill.proficiency_level)}
                  </div>
                )}
              </div>

              {/* Source Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {skill.source_tags.map((source, idx) => (
                  <span
                    key={idx}
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceBadgeColor(source)}`}
                  >
                    {source}
                  </span>
                ))}
              </div>

              {/* Evidence (Collapsible) */}
              {skill.evidence_snippets.length > 0 && (
                <details className="text-xs text-gray-600 mb-3">
                  <summary className="cursor-pointer font-medium hover:text-gold-primary">
                    View Evidence ({skill.evidence_snippets.length})
                  </summary>
                  <ul className="mt-2 space-y-1 pl-4">
                    {skill.evidence_snippets.slice(0, 3).map((evidence, idx) => (
                      <li key={idx} className="list-disc">{evidence}</li>
                    ))}
                  </ul>
                </details>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-3 border-t border-gray-100">
                {!skill.confirmed_by_user && (
                  <button
                    onClick={() => confirmSkill(skill.id)}
                    className="flex-1 px-3 py-2 bg-gold-primary text-white rounded font-medium text-sm hover:bg-gold-accent transition-colors"
                  >
                    ✓ Confirm
                  </button>
                )}
                <button
                  onClick={() => hideSkill(skill.id)}
                  className="px-3 py-2 border border-gray-300 text-gray-700 rounded font-medium text-sm hover:bg-gray-50 transition-colors"
                >
                  Hide
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
