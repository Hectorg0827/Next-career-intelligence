'use client';

import { Lock, Star, CheckCircle, ArrowRight } from 'lucide-react';

interface PremiumContentOverlayProps {
  onUnlock: () => void;
  feature: string;
}

export default function PremiumContentOverlay({ onUnlock, feature }: PremiumContentOverlayProps) {
  return (
    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-premium-bg/95 to-premium-bg rounded-2xl flex items-center justify-center backdrop-blur-[2px] z-10">
      <div className="text-center px-8 py-10 max-w-md relative">
        <div className="absolute inset-0 premium-bg-gradient opacity-20 -z-10" />
        
        {/* Lock Icon */}
        <div className="w-16 h-16 mx-auto mb-6 bg-premium-accent/10 border border-premium-accent/20 rounded-full flex items-center justify-center">
          <Lock className="w-6 h-6 text-premium-accent" />
        </div>

        {/* Title */}
        <h3 className="text-2xl font-serif italic text-white mb-3">
          Unlock {feature}
        </h3>
        
        {/* Description */}
        <p className="text-premium-text-muted text-sm mb-8 leading-relaxed">
          Create a free account to access the full depth of our multi-agent intelligence report.
        </p>

        {/* Benefits */}
        <div className="space-y-3 mb-10 text-left max-w-[280px] mx-auto">
          {[
            'Complete compatibility score',
            'Personalized skill roadmap',
            'AI career coach questions',
            'Save and track progress'
          ].map((benefit, i) => (
            <div key={i} className="flex items-center gap-3 text-premium-text-muted">
              <CheckCircle className="w-4 h-4 text-premium-accent flex-shrink-0" />
              <span className="text-xs tracking-wide">{benefit}</span>
            </div>
          ))}
        </div>

        {/* CTA Button */}
        <button
          onClick={onUnlock}
          className="premium-btn-primary w-full py-3.5 flex items-center justify-center gap-2 group"
        >
          <span className="text-sm">Unlock Full Analysis</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>

        {/* Fine Print */}
        <p className="text-premium-text-muted/30 text-[10px] uppercase tracking-widest mt-6">
          No credit card required • 30 second setup
        </p>
      </div>
    </div>
  );
}
