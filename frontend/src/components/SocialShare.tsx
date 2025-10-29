'use client';

import { useState } from 'react';
import { Share2, Mail, X, Check, Copy, Linkedin, Facebook, Twitter, Download } from 'lucide-react';

interface SocialShareProps {
  jobTitle: string;
  riskScore: number;
  riskLevel: string;
  analysisUrl?: string;
}

export default function SocialShare({ jobTitle, riskScore, riskLevel, analysisUrl }: SocialShareProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const shareUrl = analysisUrl || typeof window !== 'undefined' ? window.location.href : 'https://www.nextci.net';
  
  // Pre-filled share messages
  const shareText = `I just discovered my ${jobTitle} role has a ${riskScore}% AI displacement risk using NEXT Career Intelligence! 🚀 Check your career's AI-proof score: ${shareUrl}`;
  
  const emailSubject = `My ${jobTitle} Career Analysis from NEXT CI`;
  const emailBody = `Hi,\n\nI just completed my career analysis with NEXT Career Intelligence!\n\nMy Role: ${jobTitle}\nAI Displacement Risk: ${riskScore}% (${riskLevel})\n\nNEXT CI uses advanced AI to analyze automation risks and provides personalized skill roadmaps. I thought you might find it valuable too!\n\nTry it for free: ${shareUrl}\n\nBest regards`;

  const getRiskEmoji = () => {
    if (riskScore < 40) return '✅';
    if (riskScore < 70) return '⚠️';
    return '🚨';
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleEmailShare = () => {
    const mailtoLink = `mailto:?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`;
    window.open(mailtoLink, '_blank');
    setEmailSent(true);
    setTimeout(() => setEmailSent(false), 2000);
  };

  const handleLinkedInShare = () => {
    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
    window.open(linkedInUrl, '_blank', 'width=600,height=600');
  };

  const handleTwitterShare = () => {
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
    window.open(twitterUrl, '_blank', 'width=600,height=600');
  };

  const handleFacebookShare = () => {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
    window.open(facebookUrl, '_blank', 'width=600,height=600');
  };

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `My ${jobTitle} Career Analysis`,
          text: shareText,
          url: shareUrl,
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    }
  };

  const handleDownloadImage = () => {
    // Create a shareable image (simplified version - can be enhanced with canvas)
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = 1200;
    canvas.height = 630;

    // Background gradient
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1150A3');
    gradient.addColorStop(1, '#0B2C6B');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Text
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 48px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(`${jobTitle} Career Analysis`, canvas.width / 2, 200);

    ctx.font = 'bold 72px Inter';
    ctx.fillStyle = riskScore < 40 ? '#4ADE80' : riskScore < 70 ? '#FBBF24' : '#EF4444';
    ctx.fillText(`${riskScore}% Risk`, canvas.width / 2, 320);

    ctx.font = '32px Inter';
    ctx.fillStyle = '#E5B73B';
    ctx.fillText('Get your free career analysis at nextci.net', canvas.width / 2, 500);

    // Download
    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `nextci-career-analysis-${jobTitle.replace(/\s+/g, '-')}.png`;
      a.click();
      URL.revokeObjectURL(url);
    });
  };

  return (
    <>
      {/* Share Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl"
      >
        <Share2 className="w-5 h-5" />
        Share My Results
      </button>

      {/* Share Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-gradient-to-br from-royal-navy to-royal-blue-deep rounded-2xl border border-white/20 max-w-md w-full shadow-2xl animate-scale-in">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                <Share2 className="w-6 h-6 text-gold-primary" />
                Share Your Results
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-white/70 hover:text-white" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Preview Card */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-3xl">{getRiskEmoji()}</span>
                  <div>
                    <h4 className="text-white font-semibold">{jobTitle}</h4>
                    <p className="text-gold-primary text-sm">{riskScore}% AI Risk • {riskLevel}</p>
                  </div>
                </div>
                <p className="text-white/70 text-sm mt-2">
                  I just analyzed my career with NEXT CI! Check your AI-proof score too 🚀
                </p>
              </div>

              {/* Social Media Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={handleLinkedInShare}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-[#0077B5] hover:bg-[#006399] text-white rounded-lg transition-all"
                >
                  <Linkedin className="w-5 h-5" />
                  LinkedIn
                </button>
                <button
                  onClick={handleTwitterShare}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-[#1DA1F2] hover:bg-[#1a8cd8] text-white rounded-lg transition-all"
                >
                  <Twitter className="w-5 h-5" />
                  Twitter
                </button>
                <button
                  onClick={handleFacebookShare}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-[#1877F2] hover:bg-[#1464d4] text-white rounded-lg transition-all"
                >
                  <Facebook className="w-5 h-5" />
                  Facebook
                </button>
                <button
                  onClick={handleEmailShare}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy rounded-lg transition-all"
                >
                  {emailSent ? <Check className="w-5 h-5" /> : <Mail className="w-5 h-5" />}
                  Email
                </button>
              </div>

              {/* Additional Actions */}
              <div className="space-y-2">
                <button
                  onClick={handleCopyLink}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all border border-white/20"
                >
                  {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
                  {copied ? 'Link Copied!' : 'Copy Link'}
                </button>

                <button
                  onClick={handleDownloadImage}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all border border-white/20"
                >
                  <Download className="w-5 h-5" />
                  Download Image
                </button>

                {/* Native Share API (Mobile) */}
                {typeof window !== 'undefined' && 'share' in navigator && (
                  <button
                    onClick={handleNativeShare}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all border border-white/20"
                  >
                    <Share2 className="w-5 h-5" />
                    More Options
                  </button>
                )}
              </div>

              {/* Footer */}
              <p className="text-white/50 text-xs text-center">
                Sharing helps others discover career insights too! 🌟
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
