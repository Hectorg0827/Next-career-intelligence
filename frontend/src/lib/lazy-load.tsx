/**
 * Lazy Loading Utilities
 * Improve initial load time by deferring non-critical components
 */

import dynamic from 'next/dynamic';
import { ComponentType, ReactElement } from 'react';

/**
 * Loading fallback component
 */
export const LoadingFallback = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

/**
 * Error fallback component
 */
export const ErrorFallback = ({ error }: { error?: Error }) => (
  <div className="flex items-center justify-center p-8">
    <div className="text-red-600">
      <p className="font-semibold">Failed to load component</p>
      {error && <p className="text-sm">{error.message}</p>}
    </div>
  </div>
);

/**
 * Options for lazy loading components
 */
interface LazyLoadOptions {
  loading?: () => ReactElement;
  ssr?: boolean;
}

/**
 * Create a lazy-loaded component with customizable options
 */
export function lazyLoad<P = {}>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  options: LazyLoadOptions = {}
) {
  return dynamic(importFn, {
    loading: options.loading || LoadingFallback,
    ssr: options.ssr !== false,
  });
}

/**
 * Lazy load heavy components
 */
export const LazyComponents = {
  // Charts - COMMENTED OUT: Components don't exist yet
  // JobMatchChart: lazyLoad(() => import('@/components/dashboard/JobMatchChart'), {
  //   ssr: false,
  // }),
  // SkillsRadarChart: lazyLoad(() => import('@/components/dashboard/SkillsRadarChart'), {
  //   ssr: false,
  // }),
  // CareerProgressChart: lazyLoad(() => import('@/components/dashboard/CareerProgressChart'), {
  //   ssr: false,
  // }),
  
  // Resume Builder - COMMENTED OUT: Components don't exist yet
  // ResumeEditor: lazyLoad(() => import('@/components/resume/ResumeEditor'), {
  //   ssr: false,
  // }),
  // ResumePreviewer: lazyLoad(() => import('@/components/resume/ResumePreviewer'), {
  //   ssr: false,
  // }),
  
  // AI Features - COMMENTED OUT: Components don't exist yet
  // CareerCoach: lazyLoad(() => import('@/components/ai/CareerCoach'), {
  //   ssr: false,
  // }),
  // InterviewPractice: lazyLoad(() => import('@/components/ai/InterviewPractice'), {
  //   ssr: false,
  // }),
  
  // Modals - COMMENTED OUT: Components don't exist yet
  // JobDetailsModal: lazyLoad(() => import('@/components/jobs/JobDetailsModal'), {
  //   ssr: false,
  // }),
  // ApplicationModal: lazyLoad(() => import('@/components/jobs/ApplicationModal'), {
  //   ssr: false,
  // }),
  
  // Settings - COMMENTED OUT: Components don't exist yet
  // ProfileSettings: lazyLoad(() => import('@/components/settings/ProfileSettings')),
  // NotificationSettings: lazyLoad(() => import('@/components/settings/NotificationSettings')),
  
  // Marketplace - COMMENTED OUT: Components don't exist yet
  // JobMarketplace: lazyLoad(() => import('@/components/marketplace/JobMarketplace')),
  // EmployerDashboard: lazyLoad(() => import('@/components/marketplace/EmployerDashboard')),
};

/**
 * Preload a component when user hovers over a trigger
 */
export function usePreload<P>(
  importFn: () => Promise<{ default: ComponentType<P> }>
) {
  return () => {
    // Preload the component
    importFn();
  };
}

/**
 * Intersection Observer hook for lazy loading on scroll
 */
import { useEffect, useRef, useState } from 'react';

export function useLazyLoad<T extends HTMLElement>(
  options: IntersectionObserverInit = {}
) {
  const ref = useRef<T>(null);
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.disconnect();
      }
    }, {
      rootMargin: '50px',
      ...options,
    });
    
    observer.observe(element);
    
    return () => observer.disconnect();
  }, [options]);
  
  return { ref, isVisible };
}

/**
 * Component wrapper for lazy loading on scroll
 */
interface LazyLoadOnScrollProps {
  children: ReactElement;
  placeholder?: ReactElement;
  className?: string;
}

export function LazyLoadOnScroll({
  children,
  placeholder,
  className,
}: LazyLoadOnScrollProps) {
  const { ref, isVisible } = useLazyLoad<HTMLDivElement>();
  
  return (
    <div ref={ref} className={className}>
      {isVisible ? children : (placeholder || <LoadingFallback />)}
    </div>
  );
}

/**
 * Image lazy loading component with blur placeholder
 */
import Image from 'next/image';

interface LazyImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
}

export function LazyImage({
  src,
  alt,
  width,
  height,
  className,
  priority = false,
}: LazyImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={priority ? 'eager' : 'lazy'}
        className={`
          duration-700 ease-in-out
          ${isLoading ? 'scale-110 blur-2xl grayscale' : 'scale-100 blur-0 grayscale-0'}
        `}
        onLoadingComplete={() => setIsLoading(false)}
      />
    </div>
  );
}

/**
 * Code splitting for routes
 * COMMENTED OUT: Dashboard routes are in different locations
 */
export const LazyRoutes = {
  // Dashboard: lazyLoad(() => import('@/app/(dashboard)/dashboard/page')),
  // Jobs: lazyLoad(() => import('@/app/(dashboard)/jobs/page')),
  // Applications: lazyLoad(() => import('@/app/(dashboard)/applications/page')),
  // Resume: lazyLoad(() => import('@/app/(dashboard)/resume/page')),
  // Learning: lazyLoad(() => import('@/app/(dashboard)/learning/page')),
  // Profile: lazyLoad(() => import('@/app/(dashboard)/profile/page')),
  // Settings: lazyLoad(() => import('@/app/(dashboard)/settings/page')),
};
