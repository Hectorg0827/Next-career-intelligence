/**
 * Frontend Performance Monitoring
 * Track and report web vitals and custom metrics
 */

export interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta?: number;
  id?: string;
}

/**
 * Web Vitals thresholds
 */
const THRESHOLDS = {
  // Largest Contentful Paint (LCP)
  LCP: {
    good: 2500,
    poor: 4000,
  },
  // First Input Delay (FID)
  FID: {
    good: 100,
    poor: 300,
  },
  // Cumulative Layout Shift (CLS)
  CLS: {
    good: 0.1,
    poor: 0.25,
  },
  // First Contentful Paint (FCP)
  FCP: {
    good: 1800,
    poor: 3000,
  },
  // Time to First Byte (TTFB)
  TTFB: {
    good: 800,
    poor: 1800,
  },
  // Interaction to Next Paint (INP)
  INP: {
    good: 200,
    poor: 500,
  },
};

/**
 * Get rating for a metric value
 */
function getRating(
  name: string,
  value: number
): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[name as keyof typeof THRESHOLDS];
  if (!threshold) return 'good';
  
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

/**
 * Report metric to analytics
 */
function reportMetric(metric: PerformanceMetric) {
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${metric.name}:`, {
      value: Math.round(metric.value),
      rating: metric.rating,
      delta: metric.delta ? Math.round(metric.delta) : undefined,
    });
  }
  
  // Send to backend analytics endpoint
  if (typeof window !== 'undefined') {
    // Use sendBeacon for better reliability
    const data = JSON.stringify({
      ...metric,
      url: window.location.href,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
    });
    
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/analytics/performance', data);
    } else {
      // Fallback to fetch
      fetch('/api/analytics/performance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: data,
        keepalive: true,
      }).catch(console.error);
    }
  }
}

/**
 * Report Web Vitals
 * Use this in _app.tsx or layout.tsx
 */
export function reportWebVitals(metric: any) {
  const performanceMetric: PerformanceMetric = {
    name: metric.name,
    value: metric.value,
    rating: getRating(metric.name, metric.value),
    delta: metric.delta,
    id: metric.id,
  };
  
  reportMetric(performanceMetric);
}

/**
 * Measure custom performance metrics
 */
export class PerformanceMonitor {
  private marks: Map<string, number> = new Map();
  
  /**
   * Start measuring a custom metric
   */
  start(name: string) {
    if (typeof window === 'undefined') return;
    
    this.marks.set(name, performance.now());
    performance.mark(`${name}-start`);
  }
  
  /**
   * End measuring and report a custom metric
   */
  end(name: string) {
    if (typeof window === 'undefined') return;
    
    const startTime = this.marks.get(name);
    if (!startTime) {
      console.warn(`No start mark found for ${name}`);
      return;
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const metric: PerformanceMetric = {
      name: `custom.${name}`,
      value: duration,
      rating: duration < 100 ? 'good' : duration < 300 ? 'needs-improvement' : 'poor',
    };
    
    reportMetric(metric);
    this.marks.delete(name);
    
    return duration;
  }
  
  /**
   * Measure an async operation
   */
  async measure<T>(name: string, fn: () => Promise<T>): Promise<T> {
    this.start(name);
    try {
      const result = await fn();
      this.end(name);
      return result;
    } catch (error) {
      this.end(name);
      throw error;
    }
  }
}

/**
 * Global performance monitor instance
 */
export const performanceMonitor = new PerformanceMonitor();

/**
 * Monitor long tasks (> 50ms)
 */
export function monitorLongTasks() {
  if (typeof window === 'undefined') return;
  
  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) {
          const metric: PerformanceMetric = {
            name: 'long-task',
            value: entry.duration,
            rating: entry.duration < 100 ? 'needs-improvement' : 'poor',
          };
          reportMetric(metric);
        }
      }
    });
    
    observer.observe({ entryTypes: ['longtask'] });
  } catch (error) {
    // Long Task API not supported
    console.warn('Long Task API not supported');
  }
}

/**
 * Monitor resource loading
 */
export function monitorResourceLoading() {
  if (typeof window === 'undefined') return;
  
  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        const resource = entry as PerformanceResourceTiming;
        
        // Report slow resources (> 1s)
        if (resource.duration > 1000) {
          const metric: PerformanceMetric = {
            name: `resource.${resource.initiatorType}`,
            value: resource.duration,
            rating: getRating('TTFB', resource.duration),
          };
          reportMetric(metric);
        }
      }
    });
    
    observer.observe({ entryTypes: ['resource'] });
  } catch (error) {
    console.warn('Resource Timing API not supported');
  }
}

/**
 * Get current performance metrics
 */
export function getPerformanceMetrics() {
  if (typeof window === 'undefined') return null;
  
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  
  if (!navigation) return null;
  
  return {
    // Time to First Byte
    ttfb: navigation.responseStart - navigation.requestStart,
    
    // DOM Content Loaded
    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
    
    // Page Load
    load: navigation.loadEventEnd - navigation.loadEventStart,
    
    // DOM Interactive
    domInteractive: navigation.domInteractive - navigation.fetchStart,
    
    // DNS Lookup
    dns: navigation.domainLookupEnd - navigation.domainLookupStart,
    
    // TCP Connection
    tcp: navigation.connectEnd - navigation.connectStart,
    
    // Request + Response
    request: navigation.responseEnd - navigation.requestStart,
    
    // DOM Processing
    domProcessing: navigation.domComplete - navigation.domInteractive,
    
    // Total Page Load
    total: navigation.loadEventEnd - navigation.fetchStart,
  };
}

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring() {
  if (typeof window === 'undefined') return;
  
  // Monitor long tasks
  monitorLongTasks();
  
  // Monitor resource loading
  monitorResourceLoading();
  
  // Log initial metrics after page load
  if (document.readyState === 'complete') {
    logInitialMetrics();
  } else {
    window.addEventListener('load', logInitialMetrics);
  }
}

function logInitialMetrics() {
  setTimeout(() => {
    const metrics = getPerformanceMetrics();
    if (metrics) {
      console.log('[Performance] Initial metrics:', metrics);
    }
  }, 0);
}
