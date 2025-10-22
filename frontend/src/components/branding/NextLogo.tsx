'use client';

import React from 'react';

interface LogoProps {
  variant?: 'full' | 'icon' | 'text';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  animated?: boolean;
  className?: string;
}

export const NextLogo: React.FC<LogoProps> = ({ 
  variant = 'full', 
  size = 'md',
  animated = false,
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-8',
    md: 'h-12',
    lg: 'h-16',
    xl: 'h-24'
  };

  const animationClass = animated ? 'next-swoosh-slide' : '';

  // SVG version of the logo for inline use
  const IconSVG = () => (
    <svg 
      viewBox="0 0 800 800" 
      className={`${sizeClasses[size]} w-auto ${animationClass} ${className}`}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Deep Blue X */}
      <path
        d="M 50 150 L 250 150 L 400 400 L 550 150 L 750 150 L 500 550 L 750 650 L 550 650 L 400 400 L 250 650 L 50 650 L 300 550 Z"
        fill="#0B1D45"
        filter="drop-shadow(0 4px 8px rgba(11, 29, 69, 0.3))"
      />
      {/* Gold Swoosh */}
      <path
        d="M 150 100 Q 400 350, 750 50 L 780 80 Q 430 380, 180 130 Z"
        fill="#CBA135"
        className={animated ? 'next-swoosh-slide' : ''}
      />
    </svg>
  );

  const LoadingIconSVG = () => (
    <svg 
      viewBox="0 0 800 800" 
      className={`${sizeClasses[size]} w-auto next-logo-pulse ${className}`}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Animated X for loading */}
      <path
        d="M 50 150 L 250 150 L 400 400 L 550 150 L 750 150 L 500 550 L 750 650 L 550 650 L 400 400 L 250 650 L 50 650 L 300 550 Z"
        fill="#1E3C78"
        opacity="0.3"
      />
      <path
        d="M 150 100 Q 400 350, 750 50 L 780 80 Q 430 380, 180 130 Z"
        fill="#CBA135"
        className="next-logo-pulse"
      />
    </svg>
  );

  const TextLogo = () => (
    <div className={`flex items-center gap-3 ${className}`}>
      <IconSVG />
      <span className="font-heading font-bold text-next-deep-blue" style={{
        fontSize: size === 'sm' ? '1.25rem' : size === 'md' ? '1.75rem' : size === 'lg' ? '2.25rem' : '3rem'
      }}>
        NEXT
      </span>
    </div>
  );

  if (variant === 'icon') {
    return <IconSVG />;
  }

  if (variant === 'text') {
    return <TextLogo />;
  }

  return <TextLogo />;
};

// Loading spinner using the X logo
export const NextLoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  };

  return (
    <div className={`${sizeClasses[size]} relative`}>
      <svg 
        viewBox="0 0 100 100" 
        className="w-full h-full next-logo-pulse"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Simplified X shape */}
        <path
          d="M 10 20 L 30 20 L 50 50 L 70 20 L 90 20 L 60 60 L 90 80 L 70 80 L 50 50 L 30 80 L 10 80 L 40 60 Z"
          fill="#1E3C78"
        />
        {/* Gold accent */}
        <circle cx="50" cy="50" r="35" fill="none" stroke="#CBA135" strokeWidth="3" strokeDasharray="160" strokeDashoffset="40" className="next-logo-rotate" opacity="0.6" />
      </svg>
    </div>
  );
};

// Full logo with tagline
export const NextFullBrand: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`flex flex-col items-center ${className}`}>
      <NextLogo variant="text" size="lg" animated />
      <p className="text-next-text-muted text-sm mt-2 font-body tracking-wide">
        Adaptive Career Intelligence
      </p>
    </div>
  );
};

export default NextLogo;
