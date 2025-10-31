/**
 * API Utilities
 * Provides retry logic, timeout handling, and error management for API calls
 */

export interface FetchOptions extends RequestInit {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  onRetry?: (attempt: number, error: Error) => void;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public statusText?: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Wait for specified milliseconds
 */
const wait = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Fetch with timeout
 */
const fetchWithTimeout = async (
  url: string,
  options: RequestInit,
  timeout: number
): Promise<Response> => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(`Request timeout after ${timeout}ms`, 408, 'Request Timeout');
    }
    throw error;
  }
};

/**
 * Enhanced fetch with retry logic and timeout
 */
export async function fetchWithRetry(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const {
    timeout = 30000, // 30 seconds default
    retries = 3,
    retryDelay = 1000,
    onRetry,
    ...fetchOptions
  } = options;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetchWithTimeout(url, fetchOptions, timeout);

      // Don't retry on successful responses or client errors (4xx)
      if (response.ok || (response.status >= 400 && response.status < 500)) {
        return response;
      }

      // Server error (5xx) - may be retryable
      if (attempt < retries) {
        const error = new ApiError(
          `Server error: ${response.statusText}`,
          response.status,
          response.statusText
        );
        lastError = error;
        
        if (onRetry) {
          onRetry(attempt + 1, error);
        }

        // Exponential backoff
        await wait(retryDelay * Math.pow(2, attempt));
        continue;
      }

      return response;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on timeout or abort errors after first attempt
      if (
        lastError instanceof ApiError &&
        lastError.status === 408 &&
        attempt < retries
      ) {
        if (onRetry) {
          onRetry(attempt + 1, lastError);
        }
        await wait(retryDelay * Math.pow(2, attempt));
        continue;
      }

      // Network errors - retry
      if (attempt < retries) {
        if (onRetry) {
          onRetry(attempt + 1, lastError);
        }
        await wait(retryDelay * Math.pow(2, attempt));
        continue;
      }

      throw lastError;
    }
  }

  throw lastError || new Error('Request failed after retries');
}

/**
 * Parse JSON response with error handling
 */
export async function parseJsonResponse<T = unknown>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type');
  
  if (!contentType || !contentType.includes('application/json')) {
    const text = await response.text();
    throw new ApiError(
      'Expected JSON response',
      response.status,
      response.statusText,
      text
    );
  }

  try {
    const data = await response.json();
    
    if (!response.ok) {
      throw new ApiError(
        data.message || data.error || 'Request failed',
        response.status,
        response.statusText,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      'Failed to parse JSON response',
      response.status,
      response.statusText
    );
  }
}

/**
 * API Client class with common methods
 */
export class ApiClient {
  private baseUrl: string;
  private defaultOptions: FetchOptions;

  constructor(baseUrl = '', defaultOptions: FetchOptions = {}) {
    this.baseUrl = baseUrl;
    this.defaultOptions = {
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      ...defaultOptions,
    };
  }

  /**
   * GET request
   */
  async get<T = unknown>(
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetchWithRetry(url, {
      ...this.defaultOptions,
      ...options,
      method: 'GET',
    });

    return parseJsonResponse<T>(response);
  }

  /**
   * POST request
   */
  async post<T = unknown>(
    endpoint: string,
    data?: unknown,
    options: FetchOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetchWithRetry(url, {
      ...this.defaultOptions,
      ...options,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return parseJsonResponse<T>(response);
  }

  /**
   * PUT request
   */
  async put<T = unknown>(
    endpoint: string,
    data?: unknown,
    options: FetchOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetchWithRetry(url, {
      ...this.defaultOptions,
      ...options,
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return parseJsonResponse<T>(response);
  }

  /**
   * DELETE request
   */
  async delete<T = unknown>(
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetchWithRetry(url, {
      ...this.defaultOptions,
      ...options,
      method: 'DELETE',
    });

    return parseJsonResponse<T>(response);
  }

  /**
   * PATCH request
   */
  async patch<T = unknown>(
    endpoint: string,
    data?: unknown,
    options: FetchOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetchWithRetry(url, {
      ...this.defaultOptions,
      ...options,
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return parseJsonResponse<T>(response);
  }
}

/**
 * Default API client instance
 * Can be configured with base URL from environment variables
 */
export const apiClient = new ApiClient(
  process.env.NEXT_PUBLIC_API_BASE_URL || '/api'
);

/**
 * Example usage:
 * 
 * try {
 *   const data = await apiClient.get('/users/profile', {
 *     timeout: 5000,
 *     retries: 2,
 *     onRetry: (attempt, error) => {
 *       console.log(`Retry attempt ${attempt}:`, error.message);
 *     }
 *   });
 * } catch (error) {
 *   if (error instanceof ApiError) {
 *     console.error(`API Error: ${error.message} (${error.status})`);
 *   }
 * }
 */
