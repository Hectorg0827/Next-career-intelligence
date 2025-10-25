import React from 'react';

interface MatchBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export default function MatchBadge({ 
  score, 
  size = 'md',
  showLabel = true 
}: MatchBadgeProps) {
  const percentage = Math.round(score * 100);
  
  const getColor = () => {
    if (percentage >= 80) return 'bg-green-100 text-green-800 border-green-300';
    if (percentage >= 60) return 'bg-blue-100 text-blue-800 border-blue-300';
    if (percentage >= 40) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-orange-100 text-orange-800 border-orange-300';
  };

  const getIcon = () => {
    if (percentage >= 80) return '⭐';
    if (percentage >= 60) return '✨';
    if (percentage >= 40) return '📍';
    return '🤔';
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1 text-xs';
      case 'lg':
        return 'px-4 py-3 text-lg';
      default:
        return 'px-3 py-2 text-sm';
    }
  };

  return (
    <div className={`flex items-center gap-2 rounded-lg border ${getColor()} ${getSizeClasses()} font-semibold`}>
      <span>{getIcon()}</span>
      <span>{percentage}% Match</span>
    </div>
  );
}
