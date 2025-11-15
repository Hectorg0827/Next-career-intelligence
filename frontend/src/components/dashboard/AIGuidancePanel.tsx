/**
 * AI Guidance Panel Component
 * 
 * Displays proactive guidance messages from the AI agents
 * with priority-based styling and action buttons.
 */

'use client';

import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Info, TrendingUp, X } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface GuidanceMessage {
  guidance_type: string;
  priority: number;
  content: string;
  action_items: string[];
  impact_description?: string;
}

interface AIGuidancePanelProps {
  userId?: string;
  maxMessages?: number;
  showDismiss?: boolean;
}

export default function AIGuidancePanel({ 
  userId, 
  maxMessages = 5,
  showDismiss = true 
}: AIGuidancePanelProps) {
  const [messages, setMessages] = useState<GuidanceMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchGuidance();
  }, [userId]);

  const fetchGuidance = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/ai/guidance');
      
      if (response.success && response.messages) {
        // Sort by priority (1 = highest)
        const sorted = response.messages.sort((a: GuidanceMessage, b: GuidanceMessage) => 
          a.priority - b.priority
        );
        setMessages(sorted.slice(0, maxMessages));
      }
    } catch (error) {
      console.error('Failed to fetch AI guidance:', error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = (index: number) => {
    const messageId = `${messages[index].guidance_type}-${index}`;
    setDismissedIds(prev => new Set([...prev, messageId]));
    
    // Optionally persist dismissals to localStorage
    const dismissed = Array.from(dismissedIds);
    dismissed.push(messageId);
    localStorage.setItem('dismissed_guidance', JSON.stringify(dismissed));
  };

  const handleAction = (message: GuidanceMessage, action: string) => {
    // Route to appropriate page based on action
    const router = useRouter();
    
    if (action.toLowerCase().includes('profile')) {
      router.push('/profile');
    } else if (action.toLowerCase().includes('skill')) {
      router.push('/skills');
    } else if (action.toLowerCase().includes('job') || action.toLowerCase().includes('apply')) {
      router.push('/jobs');
    } else if (action.toLowerCase().includes('goal')) {
      router.push('/goals');
    }
  };

  const getPriorityConfig = (priority: number) => {
    switch (priority) {
      case 1: // Critical
        return {
          bgColor: 'bg-red-50 dark:bg-red-900/20',
          borderColor: 'border-red-500',
          textColor: 'text-red-900 dark:text-red-100',
          icon: <AlertCircle className="w-5 h-5 text-red-500" />,
          badge: 'Critical',
          badgeBg: 'bg-red-500',
        };
      case 2: // High
        return {
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
          borderColor: 'border-yellow-500',
          textColor: 'text-yellow-900 dark:text-yellow-100',
          icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
          badge: 'High Priority',
          badgeBg: 'bg-yellow-500',
        };
      case 3: // Medium
        return {
          bgColor: 'bg-blue-50 dark:bg-blue-900/20',
          borderColor: 'border-blue-500',
          textColor: 'text-blue-900 dark:text-blue-100',
          icon: <Info className="w-5 h-5 text-blue-500" />,
          badge: 'Recommended',
          badgeBg: 'bg-blue-500',
        };
      default: // Low
        return {
          bgColor: 'bg-gray-50 dark:bg-gray-900/20',
          borderColor: 'border-gray-400',
          textColor: 'text-gray-900 dark:text-gray-100',
          icon: <TrendingUp className="w-5 h-5 text-gray-500" />,
          badge: 'Tip',
          badgeBg: 'bg-gray-500',
        };
    }
  };

  const formatGuidanceType = (type: string) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
        <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="glass-card p-6 text-center">
        <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-white mb-2">
          You're All Set! 🎉
        </h3>
        <p className="text-ink-300">
          No guidance needed right now. Keep up the great work!
        </p>
      </div>
    );
  }

  const visibleMessages = messages.filter((msg, idx) => 
    !dismissedIds.has(`${msg.guidance_type}-${idx}`)
  );

  if (visibleMessages.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {visibleMessages.map((message, index) => {
        const config = getPriorityConfig(message.priority);
        
        return (
          <div
            key={index}
            className={`${config.bgColor} ${config.borderColor} border-l-4 rounded-lg p-4 relative`}
          >
            {/* Dismiss Button */}
            {showDismiss && (
              <button
                onClick={() => handleDismiss(index)}
                className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                aria-label="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            {/* Header */}
            <div className="flex items-start gap-3 mb-3">
              {config.icon}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className={`font-semibold ${config.textColor}`}>
                    {formatGuidanceType(message.guidance_type)}
                  </h4>
                  <span className={`${config.badgeBg} text-white text-xs px-2 py-0.5 rounded-full`}>
                    {config.badge}
                  </span>
                </div>
                
                {/* Content */}
                <p className={`${config.textColor} text-sm leading-relaxed`}>
                  {message.content}
                </p>

                {/* Impact Description */}
                {message.impact_description && (
                  <p className="mt-2 text-xs text-gray-600 dark:text-gray-400 italic">
                    💡 {message.impact_description}
                  </p>
                )}
              </div>
            </div>

            {/* Action Items */}
            {message.action_items && message.action_items.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2 ml-8">
                {message.action_items.map((action, actionIdx) => (
                  <button
                    key={actionIdx}
                    onClick={() => handleAction(message, action)}
                    className="px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// Hook to use in components
import { useRouter } from 'next/navigation';

export function useAIGuidance() {
  const [guidance, setGuidance] = useState<GuidanceMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchGuidance = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/ai/guidance');
      
      if (response.success && response.messages) {
        setGuidance(response.messages);
      }
    } catch (error) {
      console.error('Failed to fetch AI guidance:', error);
      setGuidance([]);
    } finally {
      setLoading(false);
    }
  };

  return {
    guidance,
    loading,
    fetchGuidance,
    hasHighPriority: guidance.some(m => m.priority <= 2),
    highPriorityCount: guidance.filter(m => m.priority <= 2).length,
  };
}
