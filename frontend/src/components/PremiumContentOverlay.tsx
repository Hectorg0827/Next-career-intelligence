'use client';

import { Lock, Star, CheckCircle, ArrowRight } from 'lucide-react';

interface PremiumContentOverlayProps {
  onUnlock: () => void;
  feature: string;
}

export default function PremiumContentOverlay({ onUnlock, feature }: PremiumContentOverlayProps) {
  return (
    <div className="absolute inset-0 bg-gradient-to-b from-slate-900/80 via-slate-900/95 to-slate-900 rounded-2xl flex items-center justify-center z-10">
      <div className="text-center px-6 py-8 max-w-md">
        {/* Lock Icon */}
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-gold-primary to-gold-accent rounded-full flex items-center justify-center shadow-gold">
          <Lock className="w-8 h-8 text-royal-navy" />
        </div>

        {/* Title */}
        <h3 className="text-2xl font-bold text-white mb-2">
          Unlock Full {feature}
        </h3>
        
        {/* Description */}
        <p className="text-white/80 mb-6 leading-relaxed">
          Create a free account to see your complete analysis and personalized career roadmap
        </p>

        {/* Benefits */}
        <div className="space-y-2 mb-6 text-left">
          <div className="flex items-center gap-2 text-white/90">
            <CheckCircle className="w-5 h-5 text-gold-primary flex-shrink-0" />
            <span className="text-sm">Complete career compatibility score</span>
          </div>
          <div className="flex items-center gap-2 text-white/90">
            <CheckCircle className="w-5 h-5 text-gold-primary flex-shrink-0" />
            <span className="text-sm">Personalized skill development roadmap</span>
          </div>
          <div className="flex items-center gap-2 text-white/90">
            <CheckCircle className="w-5 h-5 text-gold-primary flex-shrink-0" />
            <span className="text-sm">AI career coach questions</span>
          </div>
          <div className="flex items-center gap-2 text-white/90">
            <CheckCircle className="w-5 h-5 text-gold-primary flex-shrink-0" />
            <span className="text-sm">Save and track your progress</span>
          </div>
        </div>

        {/* CTA Button */}
        <button
          onClick={onUnlock}
          className="w-full px-6 py-4 bg-gradient-to-r from-gold-primary to-gold-accent hover:from-gold-accent hover:to-gold-hover text-royal-navy font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 group"
        >
          <Star className="w-5 h-5 group-hover:rotate-12 transition-transform" />
          <span>See Full Analysis - Free</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>

        {/* Fine Print */}
        <p className="text-white/50 text-xs mt-4">
          No credit card required • Takes 30 seconds
        </p>
      </div>
    </div>
  );
}
