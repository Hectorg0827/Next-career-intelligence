import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: boolean;
}

export const Card = ({ children, className = '', padding = true }: CardProps) => {
  // Modern design: No borders, just subtle shadows for depth
  const baseClasses = 'rounded-xl bg-white/5 backdrop-blur-md shadow-[0_4px_20px_rgba(0,0,0,0.15)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.2)] transition-shadow duration-300';
  const paddingClass = padding ? 'p-6' : '';

  return (
    <div className={`${baseClasses} ${className}`.trim()}>
      {padding ? (
        <div className={paddingClass}>
          {children}
        </div>
      ) : (
        children
      )}
    </div>
  );
};

export default Card;
