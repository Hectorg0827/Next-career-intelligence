'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

/**
 * FEATURE 5: Social Sharing Component
 * 
 * Allows users to share their career map on social media
 */

interface ShareCareerMapProps {
  careerData: {
    currentRole: string;
    futureRole: string;
    timeline: string;
  };
}

export default function ShareCareerMap({ careerData }: ShareCareerMapProps) {
  const [copied, setCopied] = useState(false);

  const shareText = `🚀 My ${careerData.timeline} career path: ${careerData.currentRole} → ${careerData.futureRole}! Check out your AI-resilient career roadmap at career-intel.ai`;

  const handleShare = (platform: string) => {
    const encodedText = encodeURIComponent(shareText);
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodedText}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedText}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?quote=${encodedText}`
    };

    window.open(urls[platform as keyof typeof urls], '_blank', 'width=600,height=400');
  };

  const copyLink = () => {
    navigator.clipboard.writeText(shareText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-4"
    >
      <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
        <span>📤</span>
        Share Your Career Map
      </h4>
      
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleShare('twitter')}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <span>🐦</span> Twitter
        </button>
        
        <button
          onClick={() => handleShare('linkedin')}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <span>💼</span> LinkedIn
        </button>
        
        <button
          onClick={copyLink}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          {copied ? '✓ Copied!' : '📋 Copy Link'}
        </button>
      </div>
    </motion.div>
  );
}
