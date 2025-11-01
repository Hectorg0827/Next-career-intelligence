/**
 * Optimized API Client with caching, retries, and performance monitoring
 * This is an enhanced version with Phase 4 performance improvements
 */

import { performanceMonitor } from './performance';

// Export all the optimized API functionality
export * from './api-client';

/**
 * Additional performance optimizations for Phase 4
 */

// Request deduplication
const pendingRequests = new Map<string, Promise<any>>();

export function deduplicateRequest<T>(
  key: string,
  fn: () => Promise<T>
): Promise<T> {
  const existing = pendingRequests.get(key);
  if (existing) {
    console.log(`[Request Deduplication] ${key}`);
    return existing;
  }
  
  const promise = fn().finally(() => {
    pendingRequests.delete(key);
  });
  
  pendingRequests.set(key, promise);
  return promise;
}

// Batch requests
interface BatchRequest {
  id: string;
  endpoint: string;
  options?: RequestInit;
}

export async function batchRequests(requests: BatchRequest[]) {
  return Promise.all(
    requests.map(req =>
      fetch(req.endpoint, req.options)
        .then(res => res.json())
        .then(data => ({ id: req.id, data, error: null }))
        .catch(error => ({ id: req.id, data: null, error }))
    )
  );
}

// Prefetch utilities
export function prefetchData(endpoint: string, options?: RequestInit) {
  if (typeof window === 'undefined') return;
  
  // Use link prefetch
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = endpoint;
  link.as = 'fetch';
  document.head.appendChild(link);
}

export function prefetchOnHover(element: HTMLElement, endpoint: string) {
  const handler = () => {
    prefetchData(endpoint);
    element.removeEventListener('mouseenter', handler);
  };
  
  element.addEventListener('mouseenter', handler);
}
