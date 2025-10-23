'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useSubscription } from '@/hooks/useSubscription';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { MessageSquare, Plus, Trash2, Archive, Clock, Sparkles } from 'lucide-react';
import { format } from 'date-fns';

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  last_message_at: string;
  is_active: string;
  message_count?: number;
}

export default function ConversationsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const { isPro, canUseCoach, loading: subLoading } = useSubscription();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !subLoading) {
      if (!user) {
        router.push('/auth/login');
        return;
      }
      if (!canUseCoach) {
        router.push('/pricing');
        return;
      }
      loadConversations();
    }
  }, [authLoading, subLoading, user, canUseCoach, router]);

  const loadConversations = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('authToken');
      if (!token) throw new Error('No auth token');

      const response = await fetch('http://localhost:8000/api/coach/conversations', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load conversations');
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (err: any) {
      console.error('Error loading conversations:', err);
      setError(err.message || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    setDeletingId(conversationId);
    try {
      const token = localStorage.getItem('authToken');
      if (!token) throw new Error('No auth token');

      const response = await fetch(
        `http://localhost:8000/api/coach/conversations/${conversationId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete conversation');
      }

      setConversations(prev => prev.filter(c => c.id !== conversationId));
    } catch (err: any) {
      console.error('Error deleting conversation:', err);
      setError(err.message || 'Failed to delete conversation');
    } finally {
      setDeletingId(null);
    }
  };

  const handleArchiveConversation = async (conversationId: string) => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) throw new Error('No auth token');

      const response = await fetch(
        `http://localhost:8000/api/coach/conversations/${conversationId}/archive`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to archive conversation');
      }

      setConversations(prev =>
        prev.map(c =>
          c.id === conversationId ? { ...c, is_active: 'archived' } : c
        )
      );
    } catch (err: any) {
      console.error('Error archiving conversation:', err);
      setError(err.message || 'Failed to archive conversation');
    }
  };

  if (authLoading || subLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading conversations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">My Conversations</h1>
            <p className="text-slate-400">
              {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
            </p>
          </div>
          <Link
            href="/coach/chat"
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Conversation
          </Link>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-200">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-slate-300">Loading conversations...</p>
          </div>
        ) : conversations.length === 0 ? (
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-12 text-center">
            <MessageSquare className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">No conversations yet</h2>
            <p className="text-slate-400 mb-6">
              Start a new conversation with your AI Career Coach
            </p>
            <Link
              href="/coach/chat"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5" />
              Start Conversation
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {conversations.map(conversation => (
              <div
                key={conversation.id}
                className="bg-slate-800 border border-slate-700 rounded-xl p-4 hover:border-slate-600 transition-colors group"
              >
                <div className="flex items-start justify-between">
                  <Link
                    href={`/coach/chat?conversation_id=${conversation.id}`}
                    className="flex-1 group-hover:bg-slate-750 p-2 rounded transition-colors"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <MessageSquare className="w-5 h-5 text-blue-400 flex-shrink-0" />
                      <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">
                        {conversation.title || 'Untitled Conversation'}
                      </h3>
                      {conversation.is_active === 'archived' && (
                        <span className="px-2 py-1 text-xs font-medium bg-slate-700 text-slate-300 rounded">
                          Archived
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-slate-400 text-sm">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        Created {format(new Date(conversation.created_at), 'MMM d, yyyy')}
                      </span>
                      <span>
                        Last message {format(new Date(conversation.last_message_at), 'MMM d, h:mm a')}
                      </span>
                    </div>
                  </Link>

                  <div className="flex items-center gap-2 ml-4">
                    {conversation.is_active === 'active' && (
                      <button
                        onClick={() => handleArchiveConversation(conversation.id)}
                        className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700 rounded transition-colors"
                        title="Archive conversation"
                      >
                        <Archive className="w-5 h-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteConversation(conversation.id)}
                      disabled={deletingId === conversation.id}
                      className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex gap-4 justify-center">
          <Link
            href="/coach/chat"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            Start New Chat
          </Link>
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
