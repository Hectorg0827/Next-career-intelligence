'use client';

import { useState, useEffect } from 'react';
import { CareerCoachAPI } from '@/lib/api/premiumAPI';
import Link from 'next/link';

interface Goal {
  id: string;
  user_id: string;
  goal_title: string;
  specific: string;
  measurable: string;
  achievable: string;
  relevant: string;
  time_bound: string;
  status: 'active' | 'completed' | 'archived';
  progress_percentage: number;
  created_at: string;
  target_date?: string;
  completed_at?: string;
}

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'completed'>('active');

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      setError(null);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const data = await CareerCoachAPI.getGoals(userId);
      setGoals(data.goals || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  const filteredGoals = goals.filter(goal =>
    filterStatus === 'all' ? true : goal.status === filterStatus
  );

  const stats = {
    total: goals.length,
    active: goals.filter(g => g.status === 'active').length,
    completed: goals.filter(g => g.status === 'completed').length,
    avgProgress: goals.filter(g => g.status === 'active').reduce((sum, g) => sum + g.progress_percentage, 0) /
                 Math.max(1, goals.filter(g => g.status === 'active').length),
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your goals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Career Goals</h1>
              <p className="text-gray-600">Track your SMART goals and measure progress</p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/coach/chat"
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Chat with Coach
              </Link>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-gold-primary text-white rounded-lg font-medium hover:bg-gold-accent transition-colors flex items-center"
              >
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Goal
              </button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Total Goals</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Active</div>
            <div className="text-3xl font-bold text-blue-600">{stats.active}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Completed</div>
            <div className="text-3xl font-bold text-green-600">{stats.completed}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Avg Progress</div>
            <div className="text-3xl font-bold text-gold-primary">{Math.round(stats.avgProgress)}%</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                filterStatus === 'all'
                  ? 'border-gold-primary text-gold-primary'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              All ({goals.length})
            </button>
            <button
              onClick={() => setFilterStatus('active')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                filterStatus === 'active'
                  ? 'border-gold-primary text-gold-primary'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Active ({stats.active})
            </button>
            <button
              onClick={() => setFilterStatus('completed')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                filterStatus === 'completed'
                  ? 'border-gold-primary text-gold-primary'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Completed ({stats.completed})
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center text-red-800">
              <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!error && filteredGoals.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filterStatus === 'all' ? 'No goals yet' : `No ${filterStatus} goals`}
            </h3>
            <p className="text-gray-600 mb-6">
              {filterStatus === 'all'
                ? 'Set your first career goal to start tracking your progress'
                : `Create a new goal or change the filter to see ${filterStatus === 'active' ? 'completed' : 'active'} goals`}
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-6 py-3 bg-gold-primary text-white rounded-lg font-medium hover:bg-gold-accent"
            >
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Your First Goal
            </button>
          </div>
        )}

        {/* Goals List */}
        {filteredGoals.length > 0 && (
          <div className="grid gap-6">
            {filteredGoals.map((goal) => (
              <GoalCard key={goal.id} goal={goal} onUpdate={fetchGoals} />
            ))}
          </div>
        )}

        {/* Create Goal Modal */}
        {showCreateModal && (
          <CreateGoalModal
            onClose={() => setShowCreateModal(false)}
            onCreated={() => {
              setShowCreateModal(false);
              fetchGoals();
            }}
          />
        )}
      </div>
    </div>
  );
}

function GoalCard({ goal, onUpdate }: { goal: Goal; onUpdate: () => void }) {
  const [expanded, setExpanded] = useState(false);

  const getDaysRemaining = () => {
    if (!goal.target_date) return null;
    const today = new Date();
    const target = new Date(goal.target_date);
    const diffTime = target.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysRemaining = getDaysRemaining();

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-center mb-2">
              <h3 className="text-xl font-bold text-gray-900">{goal.goal_title}</h3>
              <span className={`ml-3 px-3 py-1 rounded-full text-xs font-medium ${
                goal.status === 'active' ? 'bg-blue-100 text-blue-800' :
                goal.status === 'completed' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {goal.status === 'active' && '🎯 Active'}
                {goal.status === 'completed' && '✅ Completed'}
                {goal.status === 'archived' && '📦 Archived'}
              </span>
            </div>
            <p className="text-gray-600 mb-4">{goal.specific}</p>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Progress</span>
                <span className="text-sm font-bold text-gray-900">{goal.progress_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    goal.progress_percentage >= 100 ? 'bg-green-500' :
                    goal.progress_percentage >= 75 ? 'bg-blue-500' :
                    goal.progress_percentage >= 50 ? 'bg-yellow-500' :
                    'bg-orange-500'
                  }`}
                  style={{ width: `${goal.progress_percentage}%` }}
                ></div>
              </div>
            </div>

            {/* Timeline */}
            <div className="flex items-center text-sm text-gray-600">
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Created {new Date(goal.created_at).toLocaleDateString()}</span>
              {daysRemaining !== null && (
                <>
                  <span className="mx-2">•</span>
                  <span className={daysRemaining < 7 ? 'text-red-600 font-medium' : ''}>
                    {daysRemaining > 0 ? `${daysRemaining} days remaining` : 'Overdue'}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            {expanded ? 'Hide Details' : 'View SMART Details'}
          </button>
          <Link
            href="/coach/chat"
            className="px-4 py-2 border border-gold-primary text-gold-primary rounded-lg font-medium hover:bg-silver-soft transition-colors"
          >
            Discuss with Coach
          </Link>
        </div>
      </div>

      {/* Expanded SMART Details */}
      {expanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">SMART Breakdown</h4>
          <div className="space-y-4">
            <SMARTSection label="Specific" value={goal.specific} icon="🎯" />
            <SMARTSection label="Measurable" value={goal.measurable} icon="📊" />
            <SMARTSection label="Achievable" value={goal.achievable} icon="✅" />
            <SMARTSection label="Relevant" value={goal.relevant} icon="💡" />
            <SMARTSection label="Time-bound" value={goal.time_bound} icon="⏰" />
          </div>
        </div>
      )}
    </div>
  );
}

function SMARTSection({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="bg-white rounded-lg p-4">
      <div className="flex items-center mb-2">
        <span className="text-xl mr-2">{icon}</span>
        <span className="font-medium text-gray-900">{label}</span>
      </div>
      <p className="text-gray-700 text-sm">{value}</p>
    </div>
  );
}

function CreateGoalModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-lg w-full p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Create a New Goal</h2>
        <p className="text-gray-600 mb-6">
          Chat with your AI Career Coach to create a structured SMART goal tailored to your aspirations.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <Link
            href="/coach/chat"
            className="flex-1 text-center px-4 py-2 bg-gold-primary text-white rounded-lg font-medium hover:bg-gold-accent transition-colors"
          >
            Go to Coach
          </Link>
        </div>
      </div>
    </div>
  );
}
