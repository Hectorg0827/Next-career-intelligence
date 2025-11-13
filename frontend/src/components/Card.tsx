import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: boolean;
}

export const Card = ({ children, className = '', padding = true }: CardProps) => {
  const baseClasses = 'rounded-xl border border-white/10 bg-white/5 backdrop-blur-md shadow-glass';
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
