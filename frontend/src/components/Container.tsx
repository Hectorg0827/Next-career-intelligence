import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
}

export const Container = ({ children, className = '' }: ContainerProps) => {
  const baseClasses = 'mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8';
  return (
    <div className={`${baseClasses} ${className}`.trim()}>
      {children}
    </div>
  );
};

export default Container;
