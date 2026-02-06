import React from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'hover' | 'interactive';
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base styles: Solid white, subtle border, no blur
          "bg-card text-card-foreground rounded-xl border border-border shadow-sm",
          // Hover effects (only if requested)
          variant === 'hover' && "transition-shadow duration-200 hover:shadow-md",
          variant === 'interactive' && "cursor-pointer transition-all duration-200 hover:shadow-md hover:border-primary/20 hover:-translate-y-0.5",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCard.displayName = "GlassCard";

export default GlassCard;
